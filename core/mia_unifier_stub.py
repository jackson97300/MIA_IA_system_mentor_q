"""
MIA Unifier — Stub de référence (v1)
------------------------------------

Objectif
========
Créer une "vue unifiée" en RAM à partir de trois flux/fichiers JSONL produits par l'ACSIL :
  - Graph 3 (G3) : live (quotes, trades, depth, vwap, vva, pvwap, nbcv, vix...)
  - Graph 4 (G4) : M30 (basedata, vwap, nbcv...)
  - Graph 10 (G10) : M30 niveaux MenthorQ (gamma, blind spots, swing)

Sans écrire un 4ᵉ fichier, la unification se fait à la volée côté MIA :
  - Priorité de collisions : G3 > G4 > G10
  - Hot path : G3 est émis immédiatement (latence minimale) avec un contexte M30/levels attaché quand dispo
  - Patches : quand G4/G10 se mettent à jour sur la barre active, on émet un context_update léger

Remarques
---------
- Les timestamps "t" observés peuvent être des *Excel Serial Dates* (ex: 45908.708333) ou de l'époque Unix.
- L'index de barre M30 "i" est présent côté G4 et (souvent) G10. G3 n'a pas toujours "i".
- Ce stub gère les cas communs de manière robuste, avec fallback si certains champs manquent.

Comment utiliser (démo)
-----------------------
python MIA_Unifier_Stub.py --g3 chart_3_20250908.jsonl --g4 chart_4_20250908.jsonl --g10 chart_10_20250908.jsonl \
  --print-unified

Dans un vrai système, branchez `UnifiedEmitter.on_unified()` et `UnifiedEmitter.on_context_update()`
vers vos bus/queues (Kafka, NATS, Redis Streams, websockets, etc.).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Deque, Dict, Iterable, Iterator, List, Optional, Tuple

################################################################################
# Utilitaires temps & formats
################################################################################

EXCEL_EPOCH_OFFSET = 25569  # jours entre 1899-12-30 et 1970-01-01 (Excel/Unix)


def is_probably_excel_serial(t: float) -> bool:
    """Heuristique simple: un Excel serial récent ~ 45000..60000, un epoch s (10^9) ou ms (10^12).
    """
    return 20000 < t < 90000


def normalize_ts_seconds(t: float) -> float:
    """Normalise un timestamp quelconque en secondes Unix (float)."""
    # cas 1: Excel serial days -> convert to seconds
    if is_probably_excel_serial(t):
        return (t - EXCEL_EPOCH_OFFSET) * 86400.0
    # cas 2: epoch ms
    if t > 1e11:
        return t / 1000.0
    # cas 3: epoch s
    return float(t)

################################################################################
# Modèle de state par symbole
################################################################################

@dataclass
class VixState:
    value: Optional[float] = None
    ts_sec: Optional[float] = None  # seconds epoch

    def is_stale(self, now_sec: float, ttl_ms: int = 500) -> bool:
        if self.value is None or self.ts_sec is None:
            return True
        return (now_sec - self.ts_sec) * 1000.0 > ttl_ms


@dataclass
class M30Bar:
    i: Optional[int] = None
    last_update_ts: Optional[float] = None
    # Sous-objets : basedata, vwap, pvwap_diag, nbcv_*
    basedata: Dict[str, Any] = field(default_factory=dict)
    vwap: Dict[str, Any] = field(default_factory=dict)
    vwap_diag: Dict[str, Any] = field(default_factory=dict)
    pvwap: Dict[str, Any] = field(default_factory=dict)
    pvwap_diag: Dict[str, Any] = field(default_factory=dict)
    nbcv_footprint: Dict[str, Any] = field(default_factory=dict)
    nbcv_metrics: Dict[str, Any] = field(default_factory=dict)
    nbcv_orderflow: Dict[str, Any] = field(default_factory=dict)
    nbcv_diag: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Levels:
    i: Optional[int] = None
    last_update_ts: Optional[float] = None
    gamma: Dict[str, Any] = field(default_factory=dict)       # gamma_lvl_1..19
    blind: Dict[str, Any] = field(default_factory=dict)       # blind_spot_1..9
    swing: Dict[str, Any] = field(default_factory=dict)       # swing_lvl_1..9
    diag: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SymState:
    # Dernier G4 M30 connu par i (on garde actif et précédent)
    m30_by_i: Dict[int, M30Bar] = field(default_factory=dict)
    # Derniers niveaux G10 par i (actif et précédent)
    levels_by_i: Dict[int, Levels] = field(default_factory=dict)
    # VIX carry-forward
    vix: VixState = field(default_factory=VixState)
    # i actif si connu (sinon max(i) observé)
    active_i: Optional[int] = None

    def pick_active_i(self) -> Optional[int]:
        if self.active_i is not None:
            return self.active_i
        if self.m30_by_i:
            return max(self.m30_by_i.keys())
        if self.levels_by_i:
            return max(self.levels_by_i.keys())
        return None

    def compact(self, keep: int = 2) -> None:
        """Ne garder que les keep derniers i pour M30 et Levels."""
        def _compact(d: Dict[int, Any], keep: int) -> None:
            if len(d) <= keep:
                return
            for k in sorted(d.keys())[:-keep]:
                d.pop(k, None)

        _compact(self.m30_by_i, keep)
        _compact(self.levels_by_i, keep)


################################################################################
# Emetteur — pluggez vos bus ici
################################################################################

class UnifiedEmitter:
    def __init__(self,
                 on_unified: Optional[Callable[[Dict[str, Any]], None]] = None,
                 on_context_update: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        self.on_unified = on_unified
        self.on_context_update = on_context_update

    def emit_unified(self, event: Dict[str, Any]) -> None:
        if self.on_unified:
            self.on_unified(event)

    def emit_context_update(self, patch: Dict[str, Any]) -> None:
        if self.on_context_update:
            self.on_context_update(patch)


################################################################################
# Routeur & unification
################################################################################

class MIAUnifier:
    def __init__(self, emitter: UnifiedEmitter, vix_ttl_ms: int = 500) -> None:
        self.emitter = emitter
        self.vix_ttl_ms = vix_ttl_ms
        self.state_by_sym: Dict[str, SymState] = defaultdict(SymState)

    # ---------------------------- Ingestion publique ---------------------------

    def ingest(self, rec: Dict[str, Any]) -> None:
        """Ingestion d'un enregistrement JSON déjà parsé."""
        chart = rec.get("chart")
        sym = rec.get("sym")
        if not sym or chart is None:
            return
        if chart == 3:
            self._ingest_g3(sym, rec)
        elif chart == 4:
            self._ingest_g4(sym, rec)
        elif chart == 10:
            self._ingest_g10(sym, rec)
        else:
            # Autres charts ignorés dans ce stub
            pass

    # -------------------------------- G3 (live) --------------------------------

    def _ingest_g3(self, sym: str, rec: Dict[str, Any]) -> None:
        st = self.state_by_sym[sym]
        t = rec.get("t")
        t_sec = normalize_ts_seconds(float(t)) if t is not None else time.time()

        # Capture VIX si présent
        if rec.get("type") == "vix":
            v = rec.get("v") or rec.get("value")
            if isinstance(v, (int, float)):
                st.vix.value = float(v)
                st.vix.ts_sec = t_sec

        # Déterminer i actif pour joindre le contexte
        i = self._guess_active_i(sym)
        # Construire l'événement unifié (hot path)
        unified = self._build_unified_g3(sym, rec, active_i=i, now_sec=t_sec)
        self.emitter.emit_unified(unified)

    # -------------------------------- G4 (M30) ---------------------------------

    def _ingest_g4(self, sym: str, rec: Dict[str, Any]) -> None:
        st = self.state_by_sym[sym]
        i = self._extract_i(rec)
        if i is None:
            return
        t = rec.get("t")
        t_sec = normalize_ts_seconds(float(t)) if t is not None else time.time()

        m30 = st.m30_by_i.get(i)
        if not m30:
            m30 = M30Bar(i=i)
            st.m30_by_i[i] = m30
        m30.last_update_ts = t_sec

        rtype = rec.get("type")
        payload = self._payload_without_common(rec)
        if rtype == "basedata":
            m30.basedata.update(payload)
        elif rtype == "vwap":
            m30.vwap.update(payload)
        elif rtype == "vwap_diag":
            m30.vwap_diag.update(payload)
        elif rtype == "pvwap":
            m30.pvwap.update(payload)
        elif rtype == "pvwap_diag":
            m30.pvwap_diag.update(payload)
        elif rtype == "nbcv_footprint":
            m30.nbcv_footprint.update(payload)
        elif rtype == "nbcv_metrics":
            m30.nbcv_metrics.update(payload)
        elif rtype == "nbcv_orderflow":
            m30.nbcv_orderflow.update(payload)
        elif rtype == "nbcv_diag":
            m30.nbcv_diag.update(payload)
        # else: ignorer autres types éventuels

        # Si i est actif, émettre un patch contextuel
        active_i = self._guess_active_i(sym)
        if active_i == i:
            patch = {
                "t": rec.get("t"),
                "sym": sym,
                "chart": 4,
                "type": "context_update",
                "i": i,
                "changed": {"m30": self._m30_snapshot(m30)},
            }
            self.emitter.emit_context_update(patch)

        # Compactage mémoire
        st.compact(keep=2)

    # ------------------------------- G10 (levels) -------------------------------

    def _ingest_g10(self, sym: str, rec: Dict[str, Any]) -> None:
        st = self.state_by_sym[sym]
        i = self._extract_i(rec)
        if i is None:
            # Fallback : attacher aux i actifs si vraiment rien (rare)
            i = self._guess_active_i(sym)
            if i is None:
                return
        t = rec.get("t")
        t_sec = normalize_ts_seconds(float(t)) if t is not None else time.time()

        lv = st.levels_by_i.get(i)
        if not lv:
            lv = Levels(i=i)
            st.levels_by_i[i] = lv
        lv.last_update_ts = t_sec

        rtype = rec.get("type")
        payload = self._payload_without_common(rec)
        if rtype == "menthorq_level":
            # Nouveau format avec level_type spécifique
            level_type = payload.get("level_type", "")
            price = payload.get("price")
            subgraph = payload.get("subgraph")
            study_id = payload.get("study_id")
            
            if level_type and price is not None:
                # Stocker par level_type avec métadonnées
                level_data = {
                    "price": price,
                    "subgraph": subgraph,
                    "study_id": study_id,
                    "level_type": level_type
                }
                
                # Catégoriser par type de niveau
                if level_type.startswith("call_resistance"):
                    lv.gamma[f"call_resistance_{subgraph}"] = level_data
                elif level_type.startswith("put_support"):
                    lv.gamma[f"put_support_{subgraph}"] = level_data
                elif level_type.startswith("hvl"):
                    lv.gamma[f"hvl_{subgraph}"] = level_data
                elif level_type.startswith("gex_"):
                    lv.gamma[f"gex_{subgraph}"] = level_data
                elif level_type.startswith("blind_spot_"):
                    lv.blind[f"blind_spot_{subgraph}"] = level_data
                elif level_type.startswith("swing_"):
                    lv.swing[f"swing_{subgraph}"] = level_data
                else:
                    # Autres types de niveaux
                    lv.diag[f"{level_type}_{subgraph}"] = level_data
        elif rtype == "menthorq":
            # Ancien format (fallback)
            for k, v in payload.items():
                if isinstance(k, str):
                    kl = k.lower()
                    if kl.startswith("gamma_"):
                        lv.gamma[k] = v
                    elif kl.startswith("blind_spot_"):
                        lv.blind[k] = v
                    elif kl.startswith("swing_"):
                        lv.swing[k] = v
                    else:
                        lv.diag[k] = v
        elif rtype == "menthorq_diag":
            lv.diag.update(payload)
        # else: ignorer autres types

        active_i = self._guess_active_i(sym)
        if active_i == i:
            patch = {
                "t": rec.get("t"),
                "sym": sym,
                "chart": 10,
                "type": "context_update",
                "i": i,
                "changed": {"levels": self._levels_snapshot(lv)},
            }
            self.emitter.emit_context_update(patch)

        st.compact(keep=2)

    # ------------------------------- Helpers -----------------------------------

    @staticmethod
    def _extract_i(rec: Dict[str, Any]) -> Optional[int]:
        i = rec.get("i")
        if isinstance(i, int):
            return i
        try:
            if i is not None:
                return int(i)
        except Exception:
            pass
        # Certains enregistrements G4/G10 peuvent avoir i dans un sous-objet;
        # ajoutez ici d'autres heuristiques si besoin.
        return None

    @staticmethod
    def _payload_without_common(rec: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in rec.items() if k not in {"t", "sym", "chart", "type", "i"}}

    def _guess_active_i(self, sym: str) -> Optional[int]:
        st = self.state_by_sym[sym]
        # Priorité: i explicite si déjà fixé, sinon max i vu
        i = st.pick_active_i()
        if i is not None:
            return i
        # Rien vu encore -> None
        return None

    def _m30_snapshot(self, m30: M30Bar) -> Dict[str, Any]:
        return {
            "i": m30.i,
            "basedata": m30.basedata.copy(),
            "vwap": m30.vwap.copy(),
            "vwap_diag": m30.vwap_diag.copy(),
            "pvwap": m30.pvwap.copy(),
            "pvwap_diag": m30.pvwap_diag.copy(),
            "nbcv_footprint": m30.nbcv_footprint.copy(),
            "nbcv_metrics": m30.nbcv_metrics.copy(),
            "nbcv_orderflow": m30.nbcv_orderflow.copy(),
            "nbcv_diag": m30.nbcv_diag.copy(),
        }

    def _levels_snapshot(self, lv: Levels) -> Dict[str, Any]:
        return {
            "i": lv.i,
            "gamma": lv.gamma.copy(),
            "blind": lv.blind.copy(),
            "swing": lv.swing.copy(),
            "diag": lv.diag.copy(),
        }

    def _build_unified_g3(self, sym: str, rec: Dict[str, Any], active_i: Optional[int], now_sec: float) -> Dict[str, Any]:
        st = self.state_by_sym[sym]
        g3_payload = self._payload_without_common(rec)

        # Contexte M30 & levels
        m30_obj = st.m30_by_i.get(active_i) if active_i is not None else None
        lv_obj = st.levels_by_i.get(active_i) if active_i is not None else None

        unified = {
            "t": rec.get("t"),
            "sym": sym,
            "chart": 3,
            "type": rec.get("type"),
            "g3": g3_payload,  # G3 brut (prioritaire)
            "stale_flags": {
                "vix": st.vix.is_stale(now_sec, self.vix_ttl_ms),
                "m30": m30_obj is None,
                "levels": lv_obj is None,
            },
        }

        if m30_obj is not None:
            unified["m30"] = self._m30_snapshot(m30_obj)
        if lv_obj is not None:
            unified["levels"] = self._levels_snapshot(lv_obj)

        # Si VIX non présent dans g3 mais connu et non stale, l'attacher
        if "vix" not in g3_payload and not st.vix.is_stale(now_sec, self.vix_ttl_ms) and st.vix.value is not None:
            unified.setdefault("g3", {})["vix"] = st.vix.value

        return unified

################################################################################
# Lecture JSONL — Démonstration (pull-based)
################################################################################

class JSONLReader:
    """Lecteur simple de JSONL.
    - En mode démo : lit séquentiellement et appelle `unifier.ingest(rec)`.
    - Dans la vraie vie : remplacez par un tail/streaming + threads/async.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                yield rec

################################################################################
# CLI de démo
################################################################################

class _PrintEmitter(UnifiedEmitter):
    def __init__(self, print_unified: bool = False, print_updates: bool = True, max_lines: int = 5) -> None:
        super().__init__(self.on_unified, self.on_context_update)
        self.print_unified_flag = print_unified
        self.print_updates_flag = print_updates
        self.unified_count = 0
        self.max_lines = max_lines

    def on_unified(self, ev: Dict[str, Any]) -> None:
        if not self.print_unified_flag:
            return
        if self.unified_count < self.max_lines:
            print("UNIFIED:", json.dumps(ev, ensure_ascii=False))
            self.unified_count += 1

    def on_context_update(self, patch: Dict[str, Any]) -> None:
        if not self.print_updates_flag:
            return
        print("CTX_PATCH:", json.dumps(patch, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="MIA Unifier — démo")
    parser.add_argument("--g3", type=Path, help="Fichier JSONL Graph 3")
    parser.add_argument("--g4", type=Path, help="Fichier JSONL Graph 4")
    parser.add_argument("--g10", type=Path, help="Fichier JSONL Graph 10")
    parser.add_argument("--print-unified", action="store_true", help="Afficher quelques events unifiés")
    parser.add_argument("--max-lines", type=int, default=5, help="Nb d'events UNIFIED à afficher")
    args = parser.parse_args(argv)

    emitter = _PrintEmitter(print_unified=args.print_unified, print_updates=True, max_lines=args.max_lines)
    unifier = MIAUnifier(emitter)

    # Démo : on lit G4 puis G10 pour établir un contexte, ensuite G3
    # (dans la vraie vie, vous ferez du streaming en parallèle)
    for rec in JSONLReader(args.g4):
        unifier.ingest(rec)
    for rec in JSONLReader(args.g10):
        unifier.ingest(rec)
    for rec in JSONLReader(args.g3):
        unifier.ingest(rec)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
