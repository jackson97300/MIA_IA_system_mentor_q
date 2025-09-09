#!/usr/bin/env python3
"""
🔢 UTILS NUMERIC - MIA_IA_SYSTEM
Fonctions de comparaison flottantes robustes avec EPSILON

Centralise toutes les comparaisons numériques pour éviter les divergences
et assurer la cohérence dans tout le système.
"""

from math import ulp
from typing import Union, Optional

# Constante EPSILON globale pour tout le système
EPSILON = 1e-7

def _tol(a: float, b: float, eps: float = EPSILON) -> float:
    """
    Calcule la tolérance adaptative pour comparaisons flottantes robustes.
    
    Combine :
    - Tolérance absolue (eps * 1.1)
    - ULP (Unit in Last Place) pour précision machine
    - Micro tolérance relative pour grandes valeurs
    
    Args:
        a: Première valeur
        b: Deuxième valeur  
        eps: Tolérance de base (défaut: EPSILON)
        
    Returns:
        float: Tolérance adaptative
    """
    return max(
        eps * 1.1,  # Marge de sécurité
        ulp(a) + ulp(b),  # Précision machine
        1e-12 * max(1.0, abs(a), abs(b))  # Micro tolérance relative
    )

def approx_eq(a: float, b: float, eps: float = EPSILON) -> bool:
    """
    Teste si deux valeurs flottantes sont approximativement égales.
    
    Args:
        a: Première valeur
        b: Deuxième valeur
        eps: Tolérance (défaut: EPSILON)
        
    Returns:
        bool: True si |a - b| ≤ tolérance adaptative
    """
    return abs(a - b) <= _tol(a, b, eps)

def approx_le(a: float, b: float, eps: float = EPSILON) -> bool:
    """
    Teste si a ≤ b (approximativement).
    
    Args:
        a: Première valeur
        b: Deuxième valeur
        eps: Tolérance (défaut: EPSILON)
        
    Returns:
        bool: True si a ≤ b + tolérance adaptative
    """
    return a <= b + _tol(a, b, eps)

def approx_ge(a: float, b: float, eps: float = EPSILON) -> bool:
    """
    Teste si a ≥ b (approximativement).
    
    Args:
        a: Première valeur
        b: Deuxième valeur
        eps: Tolérance (défaut: EPSILON)
        
    Returns:
        bool: True si a ≥ b - tolérance adaptative
    """
    return a >= b - _tol(a, b, eps)

def approx_lt(a: float, b: float, eps: float = EPSILON) -> bool:
    """
    Teste si a < b (approximativement).
    
    Args:
        a: Première valeur
        b: Deuxième valeur
        eps: Tolérance (défaut: EPSILON)
        
    Returns:
        bool: True si a < b - tolérance adaptative
    """
    return a < b - _tol(a, b, eps)

def approx_gt(a: float, b: float, eps: float = EPSILON) -> bool:
    """
    Teste si a > b (approximativement).
    
    Args:
        a: Première valeur
        b: Deuxième valeur
        eps: Tolérance (défaut: EPSILON)
        
    Returns:
        bool: True si a > b + tolérance adaptative
    """
    return a > b + _tol(a, b, eps)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clampe une valeur entre min_val et max_val.
    
    Args:
        value: Valeur à clamper
        min_val: Valeur minimum
        max_val: Valeur maximum
        
    Returns:
        float: Valeur clampee dans [min_val, max_val]
    """
    return max(min_val, min(max_val, value))

def is_near_boundary(value: float, boundary: float, threshold: Optional[float] = None) -> bool:
    """
    Détecte si une valeur est proche d'une frontière (pour surveillance).
    
    Args:
        value: Valeur à tester
        boundary: Frontière de référence
        threshold: Seuil de détection (défaut: 2 * EPSILON)
        
    Returns:
        bool: True si |value - boundary| < threshold
    """
    if threshold is None:
        threshold = 2 * EPSILON
    return abs(value - boundary) < threshold

def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Division sécurisée avec valeur par défaut si dénominateur nul.
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut si division impossible
        
    Returns:
        float: Résultat de la division ou valeur par défaut
    """
    if abs(denominator) < EPSILON:
        return default
    return numerator / denominator

# Fonctions utilitaires pour tests et validation
def validate_range(value: float, min_val: float, max_val: float, name: str = "value") -> None:
    """
    Valide qu'une valeur est dans une plage donnée.
    
    Args:
        value: Valeur à valider
        min_val: Valeur minimum
        max_val: Valeur maximum
        name: Nom de la variable pour les messages d'erreur
        
    Raises:
        ValueError: Si la valeur est hors plage
    """
    if not (approx_ge(value, min_val) and approx_le(value, max_val)):
        raise ValueError(f"{name} = {value} hors plage [{min_val}, {max_val}]")

def validate_positive(value: float, name: str = "value") -> None:
    """
    Valide qu'une valeur est positive.
    
    Args:
        value: Valeur à valider
        name: Nom de la variable pour les messages d'erreur
        
    Raises:
        ValueError: Si la valeur n'est pas positive
    """
    if not approx_ge(value, 0.0):
        raise ValueError(f"{name} = {value} n'est pas positif")

# Constantes pour tests et validation
NEAR_BOUNDARY_THRESHOLD = 2 * EPSILON  # Seuil pour détection "proche frontière"
VALIDATION_EPSILON = EPSILON  # EPSILON pour validation (peut différer de EPSILON principal)

if __name__ == "__main__":
    # Tests unitaires rapides
    print("🧪 Tests utils/numeric.py")
    
    # Test approx_eq
    assert approx_eq(0.1, 0.1)
    assert approx_eq(0.0999999, 0.1)  # Cas problématique résolu
    assert not approx_eq(0.1, 0.2)
    
    # Test approx_le/approx_ge
    assert approx_le(0.1, 0.1)
    assert approx_le(0.0999999, 0.1)
    assert approx_ge(0.1, 0.1)
    assert approx_ge(0.1000001, 0.1)
    
    # Test clamp
    assert clamp(0.5, 0.0, 1.0) == 0.5
    assert clamp(-0.1, 0.0, 1.0) == 0.0
    assert clamp(1.1, 0.0, 1.0) == 1.0
    
    # Test is_near_boundary
    assert is_near_boundary(0.1, 0.1)
    assert is_near_boundary(0.1000001, 0.1)
    assert not is_near_boundary(0.2, 0.1)
    
    print("✅ Tous les tests passés!")


