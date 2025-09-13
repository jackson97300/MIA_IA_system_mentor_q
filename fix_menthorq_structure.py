#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger la structure MenthorQ dans les données de test
"""

import re

def fix_menthorq_structure():
    """Corrige la structure MenthorQ dans le fichier de test"""
    
    file_path = "test_data/menthorq_first_test_data.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour trouver les structures MenthorQ avec listes
    pattern = r"'menthorq': \{[^}]*'gamma_wall': \[[^\]]*\][^}]*'put_support': \[[^\]]*\][^}]*'hvl': \[[^\]]*\][^}]*'gex_levels': \[[^\]]*\][^}]*'blind_spots': \[[^\]]*\][^}]*\}"
    
    def replace_menthorq_structure(match):
        """Remplace une structure MenthorQ avec listes par une structure avec dictionnaires"""
        menthorq_block = match.group(0)
        
        # Extraire les prix des listes
        gamma_wall_match = re.search(r"'gamma_wall': \[[^\]]*'price': ([0-9.]+)", menthorq_block)
        put_support_match = re.search(r"'put_support': \[[^\]]*'price': ([0-9.]+)", menthorq_block)
        hvl_match = re.search(r"'hvl': \[[^\]]*'price': ([0-9.]+)", menthorq_block)
        gex_match = re.search(r"'gex_levels': \[[^\]]*'price': ([0-9.]+)", menthorq_block)
        blind_spot_match = re.search(r"'blind_spots': \[[^\]]*'price': ([0-9.]+)", menthorq_block)
        
        # Créer la nouvelle structure
        new_structure = "'menthorq': {\n"
        new_structure += "                    'gamma_wall': {\n"
        new_structure += f"                        'call_resistance_1': {gamma_wall_match.group(1) if gamma_wall_match else '4500.0'},\n"
        new_structure += f"                        'call_resistance_2': {float(gamma_wall_match.group(1)) + 1.0 if gamma_wall_match else '4501.0'}\n"
        new_structure += "                    },\n"
        new_structure += "                    'put_support': {\n"
        new_structure += f"                        'put_support_1': {put_support_match.group(1) if put_support_match else '4499.0'},\n"
        new_structure += f"                        'put_support_2': {float(put_support_match.group(1)) - 1.0 if put_support_match else '4498.0'}\n"
        new_structure += "                    },\n"
        new_structure += "                    'hvl': {\n"
        new_structure += f"                        'hvl_1': {hvl_match.group(1) if hvl_match else '4500.0'},\n"
        new_structure += f"                        'hvl_2': {float(hvl_match.group(1)) - 0.5 if hvl_match else '4499.5'}\n"
        new_structure += "                    },\n"
        new_structure += "                    'gex_levels': {\n"
        new_structure += f"                        'gex_1': {gex_match.group(1) if gex_match else '4500.0'},\n"
        new_structure += f"                        'gex_2': {float(gex_match.group(1)) + 0.5 if gex_match else '4500.5'}\n"
        new_structure += "                    },\n"
        new_structure += "                    'blind_spots': {\n"
        new_structure += f"                        'blind_spot_1': {blind_spot_match.group(1) if blind_spot_match else '4501.0'},\n"
        new_structure += f"                        'blind_spot_2': {float(blind_spot_match.group(1)) + 1.0 if blind_spot_match else '4502.0'}\n"
        new_structure += "                    }\n"
        new_structure += "                }"
        
        return new_structure
    
    # Remplacer toutes les occurrences
    new_content = re.sub(pattern, replace_menthorq_structure, content, flags=re.DOTALL)
    
    # Écrire le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Structure MenthorQ corrigée dans les données de test")

if __name__ == "__main__":
    fix_menthorq_structure()
