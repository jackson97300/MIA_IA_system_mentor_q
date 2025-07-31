    else:
        # Fallback pour Python < 3.7
        try:
        except:
            # Si erreur, ne rien faire (éviter le crash)
            pass'''

def fix_file(filepath):
    """Corrige un fichier Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le pattern existe
            # Remplacer
            new_content = re.sub(OLD_PATTERN, NEW_PATTERN, content, flags=re.MULTILINE | re.DOTALL)
            
            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Corrigé: {filepath}")
            return True
    except Exception as e:
        print(f"❌ Erreur sur {filepath}: {e}")
    
    return False

def main():
    """Parcourt tous les fichiers Python et corrige l'encodage"""
    fixed_count = 0
    
    # Parcourir tous les .py
    for filepath in Path('.').rglob('*.py'):
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n📊 Total: {fixed_count} fichiers corrigés")

if __name__ == "__main__":
    main()