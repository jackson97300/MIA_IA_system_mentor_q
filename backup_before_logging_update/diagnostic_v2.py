    else:
        # Fallback pour Python < 3.7
        try:
        except:
            # Si erreur, ne rien faire (éviter le crash)
            pass

"""
            # Insérer après les imports
            import_end = content.find('\n\n')
            if import_end != -1:
                content = content[:import_end] + '\n' + utf8_config + content[import_end:]
            else:
                content = utf8_config + content
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixes_applied.append(f"✅ {file_path.name}: Configuration UTF-8 ajoutée")
            
    def check_config_files(self):
        """Vérifie tous les fichiers de configuration JSON"""
        config_dir = self.project_root / 'config_files'
        
        for json_file in config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                logger.info("{json_file.name}")
            except json.JSONDecodeError as e:
                self.errors.append({
                    'file': str(json_file),
                    'type': 'json_error',
                    'error': str(e)
                })
                logger.error("{json_file.name}: Erreur JSON")
                
    def test_all_imports(self):
        """Teste l'import de tous les modules principaux"""
        modules_to_test = [
            'config', 'core', 'features', 'strategies',
            'execution', 'monitoring', 'data', 'ml', 'performance'
        ]
        
        logger.info("\n🧪 Test des imports principaux...")
        
        for module in modules_to_test:
            try:
                spec = importlib.util.spec_from_file_location(
                    module,
                    self.project_root / module / "__init__.py"
                )
                if spec and spec.loader:
                    module_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_obj)
                    logger.info("{module}")
            except Exception as e:
                logger.error("{module}: {type(e).__name__}")
                self.errors.append({
                    'module': module,
                    'type': 'import_error',
                    'error': str(e)
                })
                
    def generate_complete_report(self):
        """Génère un rapport complet du diagnostic"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'backup_location': str(self.backup_dir),
            'python_version': sys.version,
            'total_files_scanned': len(list(self.project_root.rglob("*.py"))),
            'errors': self.errors,
            'warnings': self.warnings,
            'fixes_applied': self.fixes_applied,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_fixes': len(self.fixes_applied),
                'errors_by_type': self._count_by_type(self.errors),
                'warnings_by_type': self._count_by_type(self.warnings, 'type')
            }
        }
        
        # Sauvegarder le rapport
        report_file = self.project_root / f"diagnostic_complet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Afficher le résumé
        print("\n" + "="*80)
        logger.info("📊 RÉSUMÉ DU DIAGNOSTIC")
        print("="*80)
        logger.info("\n📁 Projet: {self.project_root}")
        logger.info("📦 Backup: {self.backup_dir}")
        logger.info("\n🔍 Fichiers scannés: {report['total_files_scanned']}")
        logger.error("Erreurs trouvées: {len(self.errors)}")
        logger.warning("Warnings: {len(self.warnings)}")
        logger.info("Corrections appliquées: {len(self.fixes_applied)}")
        
        if self.errors:
            logger.info("\n❌ Erreurs par type:")
            for error_type, count in report['summary']['errors_by_type'].items():
                logger.info("   - {error_type}: {count}")
                
        if self.fixes_applied:
            logger.info("\n✅ Corrections appliquées:")
            for fix in self.fixes_applied[:10]:  # Afficher max 10
                logger.info("   {fix}")
            if len(self.fixes_applied) > 10:
                logger.info("   ... et {len(self.fixes_applied) - 10} autres")
                
        logger.info("\n📄 Rapport détaillé sauvegardé: {report_file.name}")
        
        # Instructions finales
        print("\n" + "="*80)
        logger.info("🎯 PROCHAINES ÉTAPES:")
        print("="*80)
        logger.info("1. Vérifier le rapport détaillé pour les erreurs restantes")
        logger.info("2. Relancer: python automation_main.py")
        logger.info("3. Si erreurs persistent, exécuter ce diagnostic à nouveau")
        logger.info("4. Backup disponible dans: {self.backup_dir}")
        
    def _count_by_type(self, items: List[Dict], key: str = 'type') -> Dict[str, int]:
        """Compte les éléments par type"""
        counts = {}
        for item in items:
            item_type = item.get(key, 'unknown')
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts

def main():
    """Point d'entrée principal"""
    logger.info("🚀 MIA_IA_SYSTEM - DIAGNOSTIC COMPLET v2.0")
    print("="*80)
    
    # Configuration
    project_root = input("Chemin du projet (Enter pour D:\\MIA_IA_system): ").strip()
    if not project_root:
        project_root = "D:\\MIA_IA_system"
        
    if not Path(project_root).exists():
        logger.error("Le chemin {project_root} n'existe pas!")
        return
        
    # Confirmation
    logger.info("\n📁 Projet à diagnostiquer: {project_root}")
    response = input("⚠️  Un backup complet sera créé. Continuer? (o/n): ")
    
    if response.lower() != 'o':
        logger.error("Diagnostic annulé")
        return
        
    # Lancer le diagnostic
    diagnostic = CompleteProjectDiagnostic(project_root)
    diagnostic.run_complete_diagnostic()

if __name__ == "__main__":
    main()