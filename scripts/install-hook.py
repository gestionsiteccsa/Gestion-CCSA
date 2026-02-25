#!/usr/bin/env python3
"""
Script d'installation du hook git pre-commit
Installe automatiquement le vérificateur dans .git/hooks/pre-commit
"""

import os
import sys
from pathlib import Path

HOOK_CONTENT = """#!/bin/bash
# Hook pre-commit automatique pour Gestion CCSA
# Généré automatiquement par scripts/install-hook.py

echo "🔍 Exécution du vérificateur pré-commit..."
echo ""

# Exécuter le script Python
python scripts/pre_commit_check.py --from-hook

# Récupérer le code de retour
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Vérifications passées - Commit autorisé"
    exit 0
else
    echo ""
    echo "❌ Vérifications échouées - Commit bloqué"
    echo ""
    echo "Pour bypass en cas d'urgence (déconseillé):"
    echo "  git commit --no-verify"
    exit 1
fi
"""


def install_hook():
    """Installe le hook pre-commit"""

    # Vérifier qu'on est dans un repo git
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ Erreur: Pas un repository git")
        print("   Exécutez 'git init' d'abord")
        return False

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_path = hooks_dir / "pre-commit"

    # Vérifier si un hook existe déjà
    if hook_path.exists():
        print("⚠️  Un hook pre-commit existe déjà")
        response = input("   Le remplacer ? [o/N] : ").strip().lower()
        if response not in ("o", "oui", "y", "yes"):
            print("   Installation annulée")
            return False

        # Sauvegarder l'ancien hook
        backup_path = hooks_dir / "pre-commit.backup"
        hook_path.rename(backup_path)
        print(f"   Ancien hook sauvegardé: {backup_path}")

    # Créer le nouveau hook
    try:
        hook_path.write_text(HOOK_CONTENT, encoding="utf-8")

        # Rendre exécutable (Unix/Linux/Mac)
        if os.name != "nt":
            import stat

            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print("✅ Hook pre-commit installé avec succès!")
        print(f"   Emplacement: {hook_path}")
        print("")
        print("📋 Fonctionnement:")
        print("   - Le hook s'exécute automatiquement avant chaque 'git commit'")
        print("   - Il vérifie la qualité et la sécurité du code")
        print("   - Si des erreurs sont détectées, le commit est bloqué")
        print("")
        print("⚠️  En cas d'urgence (déconseillé):")
        print("   git commit --no-verify")
        print("")
        print("📝 Pour désinstaller:")
        print(f"   rm {hook_path}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False


def uninstall_hook():
    """Désinstalle le hook pre-commit"""

    hook_path = Path(".git/hooks/pre-commit")

    if not hook_path.exists():
        print("ℹ️  Aucun hook pre-commit trouvé")
        return True

    try:
        hook_path.unlink()
        print("✅ Hook pre-commit désinstallé")

        # Restaurer la sauvegarde si elle existe
        backup_path = Path(".git/hooks/pre-commit.backup")
        if backup_path.exists():
            backup_path.rename(hook_path)
            print("✅ Ancien hook restauré")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la désinstallation: {e}")
        return False


def main():
    """Point d'entrée principal"""

    if len(sys.argv) > 1:
        if sys.argv[1] in ("--uninstall", "-u", "remove", "uninstall"):
            uninstall_hook()
            return

    print("🚀 Installation du hook git pre-commit")
    print("=" * 50)
    print("")

    install_hook()


if __name__ == "__main__":
    main()
