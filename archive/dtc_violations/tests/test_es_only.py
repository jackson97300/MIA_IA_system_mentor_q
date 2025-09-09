#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, json, time, threading

ENCODING_COMPACT_JSON = 2
PROTOCOL_VERSION = 8

TYPE_ENCODING_REQUEST   = 0
TYPE_LOGON_REQUEST      = 1
TYPE_LOGON_RESPONSE     = 2
TYPE_HEARTBEAT          = 3
TYPE_MARKET_DATA_REQUEST = 101

def send_json(sock, obj):
    # Compact, sans espaces + TERMINATEUR \x00 pour Sierra Chart
    data = json.dumps(obj, separators=(',', ':')).encode('utf-8') + b'\x00'
    sock.sendall(data)

def recv_bytes(sock, timeout=1.0, bufsize=65536):
    sock.settimeout(timeout)
    try:
        data = sock.recv(bufsize)
        return data if data else b''
    except socket.timeout:
        return b''
    except Exception as e:
        print(f"❌ Erreur recv: {e}")
        return b''

def iter_null_framed_json(buffer_bytes: bytearray):
    """
    Consomme buffer_bytes jusqu'aux b'\x00'.
    Rend les objets JSON décodés, laisse les restes (paquets partiels) dans buffer_bytes.
    """
    start = 0
    while True:
        try:
            idx = buffer_bytes.index(0, start)  # chercher b'\x00'
        except ValueError:
            # pas de terminator complet : garder le reste pour la prochaine recv
            if start > 0:
                del buffer_bytes[:start]
            return
        chunk = bytes(buffer_bytes[start:idx])  # sans le \x00
        start = idx + 1
        if chunk.strip():
            try:
                yield json.loads(chunk.decode('utf-8'))
            except json.JSONDecodeError:
                # ignorer silencieusement un chunk corrompu/partiel
                pass

class DTCClient:
    def __init__(self, host, port, user, pwd, name="MIA DTC ES Test", hb=20, trade_mode=0):
        self.host, self.port = host, port
        self.user, self.pwd = user, pwd
        self.client_name = name
        self.hb = hb
        self.trade_mode = trade_mode
        self.sock = None
        self.session_id = 0
        self.logged_on = False
        self.run_hb = False
        self.hb_thread = None

    def connect(self):
        print(f"🔌 Connexion TCP à {self.host}:{self.port}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            print(f"🔌 Tentative de connexion à {self.host}:{self.port}...")
            self.sock.connect((self.host, self.port))
            print("✅ Connexion TCP réussie")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False

    def close(self):
        print("🔌 Fermeture de la connexion...")
        self.run_hb = False
        if self.hb_thread: 
            self.hb_thread.join(timeout=2)
        if self.sock:
            try: 
                self.sock.close()
            except: 
                pass
        print("🔌 Déconnexion TCP effectuée")

    # -------- DTC messages (COMPACT JSON + \x00) ----------
    def send_encoding_request(self):
        msg = {"Type": TYPE_ENCODING_REQUEST, "F": [PROTOCOL_VERSION, ENCODING_COMPACT_JSON]}
        send_json(self.sock, msg)
        print(f"📤 ENCODING_REQUEST -> {msg}")

    def send_logon_request(self):
        F = [PROTOCOL_VERSION, self.user, self.pwd, self.hb, self.client_name, self.trade_mode]
        msg = {"Type": TYPE_LOGON_REQUEST, "F": F}
        send_json(self.sock, msg)
        print(f"📤 LOGON_REQUEST -> {msg}")

    def send_heartbeat(self):
        msg = {"Type": TYPE_HEARTBEAT, "F": [self.session_id]}
        send_json(self.sock, msg)

    def hb_loop(self):
        while self.run_hb and self.logged_on:
            try:
                self.send_heartbeat()
            except: break
            time.sleep(2)  # Heartbeat toutes les 2s pour éviter le timeout 5s

    def wait_messages(self, want_types, wait_sec=10):
        """Collecte messages pendant wait_sec et renvoie le premier dont Type est dans want_types"""
        deadline = time.time() + wait_sec
        buf = bytearray()
        while time.time() < deadline:
            chunk = recv_bytes(self.sock, timeout=1.0)
            if not chunk:
                continue
            buf.extend(chunk)
            for obj in iter_null_framed_json(buf):
                t = obj.get("Type")
                # Debug minimal
                if t == TYPE_HEARTBEAT:
                    print("💓 HEARTBEAT reçu")
                if t in want_types:
                    return obj
        return None

    def logon(self):
        print("🔐 Processus de logon (JSON compact + \\x00)...")
        # 1) Confirmer encodage compact JSON
        self.send_encoding_request()
        # 2) Envoyer LOGON_REQUEST compact
        self.send_logon_request()

        # 3) Attendre LOGON_RESPONSE
        obj = self.wait_messages({TYPE_LOGON_RESPONSE}, wait_sec=10)
        if not obj:
            print("❌ Timeout LOGON_RESPONSE")
            return False

        # En compact, SessionID est dans F. DTC place généralement SessionID en position 0.
        F = obj.get("F", [])
        self.session_id = F[0] if F else 0
        self.logged_on = True
        print(f"✅ LOGON_RESPONSE reçu - SessionID: {self.session_id}")

        # 4) Heartbeat rapide
        self.run_hb = True
        self.hb_thread = threading.Thread(target=self.hb_loop, daemon=True)
        self.hb_thread.start()
        return True

if __name__ == "__main__":
    print("🔍 TEST INSTANCE ES SEULEMENT (Port 11099)")
    print("="*50)
    
    print("🚀 Démarrage du test ES...")
    c = DTCClient("127.0.0.1", 11099, "lazard973", "LEpretre-973", "MIA DTC ES Test")
    
    try:
        print("📡 Tentative de connexion...")
        if c.connect():
            print("🔐 Tentative de logon...")
            if c.logon():
                print("✅ Logon ES réussi")
                # Garder la connexion ouverte quelques secondes pour tester le heartbeat
                time.sleep(5)
            else:
                print("❌ Logon ES échoué")
        else:
            print("❌ Connexion ES échouée")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    finally:
        print("🧹 Nettoyage...")
        c.close()
    
    print("\n📊 FIN DU TEST ES")
    print("="*50)
