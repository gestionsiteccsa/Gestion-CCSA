#!/usr/bin/env python3
"""
Script de vérification pré-commit pour projet Django
Mode STRICT - Bloque immédiatement sur erreur
Avec corrections automatiques et vérification conventional commits

Usage:
    python scripts/pre_commit_check.py
    python scripts/pre_commit_check.py --fix --yes
    python scripts/pre_commit_check.py --from-hook
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """Gestion des couleurs terminal"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        if enabled:
            self.RED = '\033[91m'
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
            self.BLUE = '\033[94m'
            self.MAGENTA = '\033[95m'
            self.CYAN = '\033[96m'
            self.WHITE = '\033[97m'
            self.BOLD = '\033[1m'
            self.UNDERLINE = '\033[4m'
            self.RESET = '\033[0m'
        else:
            self.RED = self.GREEN = self.YELLOW = self.BLUE = ''
            self.MAGENTA = self.CYAN = self.WHITE = ''
            self.BOLD = self.UNDERLINE = self.RESET = ''
    
    def success(self, text: str) -> str:
        return f"{self.GREEN}[OK] {text}{self.RESET}"
    
    def error(self, text: str) -> str:
        return f"{self.RED}[ERREUR] {text}{self.RESET}"
    
    def warning(self, text: str) -> str:
        return f"{self.YELLOW}[ATTENTION] {text}{self.RESET}"
    
    def info(self, text: str) -> str:
        return f"{self.BLUE}[INFO] {text}{self.RESET}"
    
    def header(self, text: str) -> str:
        return f"{self.BOLD}{self.CYAN}{text}{self.RESET}"
    
    def critical(self, text: str) -> str:
        return f"{self.BOLD}{self.RED}[CRITIQUE] {text}{self.RESET}"


class CheckResult:
    """Résultat d'une vérification"""
    
    def __init__(self, name: str, passed: bool, message: str = "", 
                 can_fix: bool = False, fix_command: str = "", 
                 details: Optional[List[str]] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.can_fix = can_fix
        self.fix_command = fix_command
        self.details: List[str] = details if details is not None else []
    
    def __bool__(self):
        return self.passed


class PreCommitChecker:
    """Classe principale de vérification pré-commit"""
    
    def __init__(self, config_path: str = "scripts/pre-commit-config.json"):
        self.config = self._load_config(config_path)
        self.colors = Colors(self.config.get("colors", {}).get("enabled", True))
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        self.strict_mode = self.config.get("strict_mode", True)
        self.auto_fix = self.config.get("auto_fix", True)
        self.interactive = self.config.get("interactive", True)
        self.project_root = Path.cwd()
    
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ATTENTION] Fichier de configuration non trouvé: {config_path}")
            print("Utilisation de la configuration par défaut")
            return self._default_config()
        except json.JSONDecodeError as e:
            print(f"[ERREUR] Erreur dans le fichier de configuration: {e}")
            sys.exit(1)
    
    def _default_config(self) -> Dict:
        """Configuration par défaut"""
        return {
            "strict_mode": True,
            "auto_fix": True,
            "interactive": True,
            "checks": {
                "linter": {"enabled": True},
                "tests": {"enabled": True},
                "django": {"enabled": True},
                "security": {"enabled": True},
                "files": {"enabled": True},
                "git": {"enabled": True, "conventional_commits": True}
            }
        }
    
    def _run_command(self, command, capture_output: bool = True, 
                     timeout: int = 60, shell: bool = False) -> Tuple[int, str, str]:
        """Exécute une commande shell et retourne le résultat
        
        Args:
            command: Commande à exécuter (str ou list)
            capture_output: Capturer la sortie
            timeout: Timeout en secondes
            shell: Utiliser le shell (dangereux, éviter si possible)
        """
        try:
            result = subprocess.run(  # nosec B602
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Commande expirée après {timeout}s"
        except Exception as e:
            return -1, "", str(e)
    
    def _confirm(self, message: str) -> bool:
        """Demande confirmation à l'utilisateur"""
        if not self.interactive:
            return self.auto_fix
        
        try:
            response = input(f"{message} [O/n] : ").strip().lower()
            return response in ('', 'o', 'oui', 'y', 'yes')
        except (EOFError, KeyboardInterrupt):
            print("\nInterrompu par l'utilisateur")
            return False
    
    def _print_header(self, text: str):
        """Affiche un en-tête de section"""
        print(f"\n{self.colors.header('=' * 60)}")
        print(self.colors.header(text.center(60)))
        print(self.colors.header('=' * 60))
    
    def _print_step(self, number: int, text: str):
        """Affiche une étape"""
        print(f"\n{self.colors.BOLD}{number}. {text}{self.colors.RESET}")
    
    def check_tool_installed(self, tool: str) -> bool:
        """Vérifie si un outil est installé"""
        cmd = ["which", tool] if os.name != 'nt' else ["where", tool]
        return_code, _, _ = self._run_command(cmd)
        if return_code != 0:
            return_code, _, _ = self._run_command(["pip", "show", tool])
        return return_code == 0
    
    def install_tool(self, tool: str) -> bool:
        """Installe un outil manquant"""
        print(self.colors.warning(f"{tool} n'est pas installé"))
        if self._confirm(f"Installer {tool} ?"):
            return_code, stdout, stderr = self._run_command(["pip", "install", tool])
            if return_code == 0:
                print(self.colors.success(f"{tool} installé avec succès"))
                return True
            else:
                print(self.colors.error(f"Échec de l'installation de {tool}"))
                print(stderr)
                return False
        return False

    def check_linter(self) -> CheckResult:
        """Vérification du linter (Flake8)"""
        if not self.config["checks"]["linter"]["enabled"]:
            return CheckResult("Linter", True, "Désactivé")
        
        print("   Vérification avec Flake8...")
        
        if not self.check_tool_installed("flake8"):
            if not self.install_tool("flake8"):
                return CheckResult("Linter", False, "Flake8 non installé", 
                                 can_fix=False)
        
        exclude = ",".join(self.config["checks"]["linter"]["exclude"])
        max_line_length = self.config["checks"]["linter"]["max_line_length"]
        
        # Ignorer les erreurs de docstrings (D100-D104, D400, D401)
        returncode, stdout, stderr = self._run_command([
            "flake8", ".",
            "--exclude", exclude,
            "--max-line-length", str(max_line_length),
            "--ignore", "D100,D101,D102,D103,D104,D400,D401"
        ])
        
        if returncode == 0:
            return CheckResult("Linter", True, "Aucune erreur détectée")
        
        # Erreurs détectées
        errors = stdout.strip().split('\n') if stdout else []
        error_count = len([e for e in errors if e.strip()])
        
        details = [
            f"{error_count} erreur(s) de style détectée(s)",
            "Exemples d'erreurs :"
        ]
        details.extend(errors[:5])  # Limiter à 5 erreurs
        
        # Proposer correction avec Black
        if self.check_tool_installed("black"):
            return CheckResult(
                "Linter", False, 
                f"{error_count} erreurs de style",
                can_fix=True,
                fix_command="black .",
                details=details
            )
        
        return CheckResult("Linter", False, f"{error_count} erreurs de style", 
                         details=details)
    
    def fix_linter(self) -> bool:
        """Corrige les erreurs de linter avec Black et isort"""
        print("   Tentative de correction automatique...")
        
        fixed = False
        
        # Black
        if self.check_tool_installed("black"):
            print("   Formatage avec Black...")
            returncode, _, _ = self._run_command([
                "black", ".",
                "--exclude", "/(env|venv|__pycache__|migrations|scripts|logs)/"
            ])
            if returncode == 0:
                print(self.colors.success("   [OK] Black a formaté le code"))
                fixed = True
        
        # isort
        if self.check_tool_installed("isort"):
            print("   Tri des imports avec isort...")
            returncode, _, _ = self._run_command([
                "isort", ".",
                "--skip", "env", "--skip", "venv", "--skip", "__pycache__",
                "--skip", "migrations", "--skip", "scripts", "--skip", "logs"
            ])
            if returncode == 0:
                print(self.colors.success("   [OK] isort a trié les imports"))
                fixed = True
        
        return fixed
    
    def check_tests(self) -> CheckResult:
        """Vérification des tests Django"""
        if not self.config["checks"]["tests"]["enabled"]:
            return CheckResult("Tests", True, "Désactivés")
        
        print("   Exécution des tests Django...")
        
        test_module = self.config["checks"]["tests"].get("test_module", "")
        cmd = ["python", "manage.py", "test", test_module, "--verbosity=1"] if test_module else ["python", "manage.py", "test", "--verbosity=1"]
        
        returncode, stdout, stderr = self._run_command(cmd, timeout=120)
        
        if returncode == 0:
            # Compter les tests passés
            test_count = 0
            for line in stdout.split('\n'):
                if 'test' in line.lower() and 'ok' in line.lower():
                    test_count += 1
            
            return CheckResult("Tests", True, f"Tous les tests passent ({test_count} tests)")
        
        # Tests échoués
        details = []
        if "FAIL" in stdout or "ERROR" in stdout:
            lines = stdout.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("FAIL:") or line.startswith("ERROR:"):
                    details.append(line)
                    if i + 1 < len(lines):
                        details.append(lines[i + 1])
        
        return CheckResult("Tests", False, "Certains tests ont échoué", 
                         details=details[:10])
    
    def check_django(self) -> CheckResult:
        """Vérification Django (check + migrations)"""
        if not self.config["checks"]["django"]["enabled"]:
            return CheckResult("Django", True, "Désactivé")
        
        print("   Vérification de la configuration Django...")
        
        # Check standard
        returncode, stdout, stderr = self._run_command(["python", "manage.py", "check", "--verbosity=1"])
        
        if returncode != 0:
            return CheckResult("Django", False, "Erreurs dans la configuration", 
                             details=[stderr or stdout])
        
        print(self.colors.success("   [OK] Configuration Django OK"))
        
        # Check production si activé
        if self.config["checks"]["django"].get("check_deploy", False):
            print("   Vérification de la configuration de production...")
            returncode, stdout, stderr = self._run_command(["python", "manage.py", "check", "--deploy", "--verbosity=1"])
            
            if returncode != 0:
                warnings = [line for line in (stdout + stderr).split('\n') if 'WARNING' in line or 'ERROR' in line]
                return CheckResult("Django", False, "Problèmes de configuration production", 
                                 details=warnings[:5])
            
            print(self.colors.success("   [OK] Configuration production OK"))
        
        # Vérifier les migrations
        if self.config["checks"]["django"].get("check_migrations", True):
            print("   Vérification des migrations...")
            returncode, stdout, stderr = self._run_command(["python", "manage.py", "makemigrations", "--check", "--dry-run"])
            
            if returncode != 0:
                # Migrations manquantes
                if self.config["checks"]["django"].get("auto_migrate", False):
                    if self._confirm("   Des migrations sont manquantes. Les créer ?"):
                        returncode, stdout, stderr = self._run_command(["python", "manage.py", "makemigrations"])
                        if returncode == 0:
                            self.fixes_applied.append("Migrations créées")
                            print(self.colors.success("   [OK] Migrations créées"))
                            return CheckResult("Django", True, "Configuration OK, migrations créées")
                
                return CheckResult("Django", False, "Migrations manquantes", 
                                 can_fix=True,
                                 details=["Exécutez: python manage.py makemigrations"])
        
        return CheckResult("Django", True, "Configuration Django OK")
    
    def check_security(self) -> CheckResult:
        """Vérification de sécurité (Bandit, Safety, secrets)"""
        if not self.config["checks"]["security"]["enabled"]:
            return CheckResult("Sécurité", True, "Désactivée")
        
        print("   Scan de sécurité...")
        
        results = []
        
        # Bandit
        if "bandit" in self.config["checks"]["security"]["tools"]:
            print("   - Analyse avec Bandit...")
            if not self.check_tool_installed("bandit"):
                self.install_tool("bandit")
            
            if self.check_tool_installed("bandit"):
                exclude = ",".join(["./tests", "./migrations", "./env", "./venv", 
                                   "./.git", "__pycache__"])
                returncode, stdout, stderr = self._run_command([
                    "bandit", "-r", ".", "-x", exclude, "-ll", "--quiet"
                ])
                
                if returncode != 0:
                    results.append(("Bandit", False, stdout or stderr))
                else:
                    results.append(("Bandit", True, "Aucune vulnérabilité détectée"))
        
        # Safety
        if "safety" in self.config["checks"]["security"]["tools"]:
            print("   - Vérification des dépendances avec Safety...")
            if not self.check_tool_installed("safety"):
                self.install_tool("safety")
            
            if self.check_tool_installed("safety"):
                returncode, stdout, stderr = self._run_command(["safety", "check", "--json"], timeout=120)
                
                if returncode != 0:
                    # Parser le JSON pour obtenir les détails
                    try:
                        vulnerabilities = json.loads(stdout) if stdout else []
                        details = [f"{v.get('package', 'N/A')}: {v.get('vulnerability', 'N/A')}" 
                                  for v in vulnerabilities[:5]]
                    except:
                        details = [stdout or "Vulnérabilités détectées"]
                    
                    results.append(("Safety", False, "Vulnérabilités dans les dépendances", details))
                else:
                    results.append(("Safety", True, "Aucune vulnérabilité détectée"))
        
        # Détection de secrets
        if self.config["checks"]["security"].get("check_secrets", True):
            print("   - Détection de secrets...")
            
            # Vérifier si .secrets.baseline existe
            if not Path(".secrets.baseline").exists():
                print(self.colors.warning("   [ATTENTION]  Fichier .secrets.baseline non trouvé"))
                print("   Création du baseline...")
                self._run_command(["detect-secrets", "scan", "--all-files", "--baseline", ".secrets.baseline"])
            
            if Path(".secrets.baseline").exists():
                returncode, stdout, stderr = self._run_command(
                    ["detect-secrets", "scan", "--all-files", "--baseline", ".secrets.baseline"]
                )
                
                if returncode != 0 or "secrets" in stdout.lower():
                    results.append(("Secrets", False, "Secrets potentiels détectés", 
                                  ["Vérifiez le fichier .secrets.baseline"]))
                else:
                    results.append(("Secrets", True, "Aucun secret détecté"))
        
        # Vérification manuelle des patterns dangereux
        print("   - Vérification des patterns dangereux...")
        dangerous_patterns = self._check_dangerous_patterns()
        if dangerous_patterns:
            results.append(("Patterns", False, "Patterns dangereux détectés", dangerous_patterns))
        else:
            results.append(("Patterns", True, "Aucun pattern dangereux"))
        
        # Agréger les résultats
        failed = [r for r in results if not r[1]]
        if failed:
            details = []
            for name, _, msg, *extra in failed:
                details.append(f"{name}: {msg}")
                if extra and extra[0]:
                    details.extend(extra[0])
            
            return CheckResult("Sécurité", False, "Problèmes de sécurité détectés", 
                             details=details)
        
        return CheckResult("Sécurité", True, "Aucun problème de sécurité détecté")
    
    def _check_dangerous_patterns(self) -> List[str]:
        """Vérifie les patterns dangereux dans le code"""
        patterns = []
        
        # Patterns à rechercher
        dangerous = {
            r'SECRET_KEY\s*=\s*["\'][^"\']+["\']': "SECRET_KEY en dur dans le code",
            r'DEBUG\s*=\s*True': "DEBUG = True (vérifiez que c'est intentionnel)",
            r'ALLOWED_HOSTS\s*=\s*\[\s*\*\s*\]': "ALLOWED_HOSTS = ['*'] (trop permissif)",
            r'eval\s*\(': "Utilisation d'eval() (dangereux)",
            r'exec\s*\(': "Utilisation d'exec() (dangereux)",
            r'password\s*=\s*["\'][^"\']+["\']': "Mot de passe en dur dans le code",
            r'api_key\s*=\s*["\'][^"\']+["\']': "API key en dur dans le code",
        }
        
        exclude_dirs = ['env', 'venv', '__pycache__', 'migrations', '.git', 'scripts']
        
        for py_file in Path('.').rglob('*.py'):
            # Ignorer les dossiers exclus
            if any(excluded in str(py_file) for excluded in exclude_dirs):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern, description in dangerous.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        patterns.append(f"{py_file}: {description}")
            except:
                continue
        
        return patterns[:10]  # Limiter à 10 résultats
    
    def check_files(self) -> CheckResult:
        """Vérification des fichiers sensibles"""
        if not self.config["checks"]["files"]["enabled"]:
            return CheckResult("Fichiers", True, "Désactivé")
        
        print("   Vérification des fichiers sensibles...")
        
        forbidden_files = self.config["checks"]["files"]["forbidden_files"]
        found = []
        
        for file in forbidden_files:
            if Path(file).exists():
                # Vérifier si c'est un fichier suivi par git
                returncode, _, _ = self._run_command(["git", "ls-files", "--error-unmatch", file])
                if returncode == 0:
                    found.append(f"{file} (suivi par git - DANGER!)")
                else:
                    found.append(f"{file} (non suivi - OK)")
        
        if found:
            dangerous = [f for f in found if "DANGER" in f]
            if dangerous:
                return CheckResult("Fichiers", False, 
                                 "Fichiers sensibles commités!", 
                                 details=dangerous)
            else:
                print(self.colors.success("   [OK] Fichiers sensibles non commités"))
        
        # Vérifier .gitignore
        if self.config["checks"]["files"].get("check_gitignore", True):
            print("   Vérification du .gitignore...")
            if not Path(".gitignore").exists():
                return CheckResult("Fichiers", False, 
                                 "Fichier .gitignore manquant")
            
            gitignore_content = Path(".gitignore").read_text()
            required = ['.env', 'db.sqlite3', '__pycache__/', '*.pyc']
            missing = [item for item in required if item not in gitignore_content]
            
            if missing:
                return CheckResult("Fichiers", False, 
                                 ".gitignore incomplet",
                                 details=[f"Manquant: {', '.join(missing)}"])
        
        return CheckResult("Fichiers", True, "Aucun fichier sensible détecté")
    
    def check_git(self) -> CheckResult:
        """Vérification Git (message de commit, fichiers staged)"""
        if not self.config["checks"]["git"]["enabled"]:
            return CheckResult("Git", True, "Désactivé")
        
        print("   Vérification Git...")
        
        # Vérifier les fichiers staged
        if self.config["checks"]["git"].get("check_staged_files", True):
            returncode, stdout, _ = self._run_command(["git", "diff", "--cached", "--name-only"])
            staged_files = stdout.strip().split('\n') if stdout else []
            
            if not staged_files or staged_files == ['']:
                return CheckResult("Git", False, 
                                 "Aucun fichier staged", 
                                 details=["Utilisez 'git add' avant de committer"])
            
            print(f"   {len(staged_files)} fichier(s) staged")
        
        # Vérification conventional commits
        if self.config["checks"]["git"].get("conventional_commits", True):
            # Récupérer le dernier message de commit (pour hook) ou demander
            returncode, stdout, _ = self._run_command(["git", "log", "-1", "--pretty=%B"])
            last_message = stdout.strip() if stdout else ""
            
            # Si on est dans un hook pre-commit, le message n'est pas encore créé
            # On vérifie juste que le dernier commit suit la convention
            allowed_types = self.config["checks"]["git"].get("allowed_types", 
                            ["feat", "fix", "docs", "style", "refactor", "test", "chore"])
            
            pattern = r'^(' + '|'.join(allowed_types) + r')(\(.+\))?: .+'
            
            if last_message and not re.match(pattern, last_message, re.IGNORECASE):
                # C'est un warning, pas une erreur bloquante
                self.warnings.append(
                    f"Le dernier commit ne suit pas la convention: '{last_message[:50]}...'\n"
                    f"Format attendu: type: description\n"
                    f"Types autorisés: {', '.join(allowed_types)}"
                )
        
        return CheckResult("Git", True, "Git OK")
    
    def run_all_checks(self) -> bool:
        """Exécute toutes les vérifications"""
        self._print_header("[VERIFICATION] VÉRIFICATION PRÉ-COMMIT - MODE STRICT")
        
        print(f"\n{self.colors.BOLD}Mode: STRICT (arrêt immédiat sur erreur){self.colors.RESET}")
        print(f"Auto-correction: {'Oui' if self.auto_fix else 'Non'}")
        print(f"Interactif: {'Oui' if self.interactive else 'Non'}")
        
        checks = [
            ("Linter", self.check_linter, self.fix_linter),
            ("Tests", self.check_tests, None),
            ("Django", self.check_django, None),
            ("Sécurité", self.check_security, None),
            ("Fichiers", self.check_files, None),
            ("Git", self.check_git, None),
        ]
        
        all_passed = True
        
        for i, (name, check_func, fix_func) in enumerate(checks, 1):
            self._print_step(i, name)
            
            result = check_func()
            
            if result.passed:
                print(self.colors.success(f"   [OK] {result.message}"))
                if result.details:
                    for detail in result.details[:3]:
                        print(f"      {self.colors.info(detail)}")
            else:
                print(self.colors.error(f"   [X] {result.message}"))
                
                if result.details:
                    print(f"\n   {self.colors.BOLD}Détails:{self.colors.RESET}")
                    for detail in result.details[:5]:
                        print(f"      - {detail}")
                
                # Tentative de correction
                if result.can_fix and fix_func and self.auto_fix:
                    print(f"\n   {self.colors.warning('Correction automatique possible')}")
                    if self._confirm(f"   Corriger automatiquement ?"):
                        if fix_func():
                            # Revérifier
                            print(f"\n   {self.colors.info('Revérification...')}")
                            result = check_func()
                            if result.passed:
                                print(self.colors.success(f"   [OK] Correction réussie - {result.message}"))
                                self.fixes_applied.append(name)
                                continue
                            else:
                                print(self.colors.error(f"   [X] Correction insuffisante - {result.message}"))
                
                # Mode strict : arrêt immédiat
                if self.strict_mode:
                    print(f"\n{self.colors.critical('[BLOQUE] COMMIT BLOQUÉ')}")
                    print(f"{self.colors.RED}Corrigez les erreurs ci-dessus avant de recommencer.{self.colors.RESET}")
                    self._print_summary(False)
                    return False
                else:
                    all_passed = False
                    self.errors.append(f"{name}: {result.message}")
        
        self._print_summary(all_passed)
        return all_passed
    
    def _print_summary(self, success: bool):
        """Affiche le résumé final"""
        print(f"\n{self.colors.header('=' * 60)}")
        
        if success:
            print(self.colors.success("[SUCCES] SUCCÈS - Toutes les vérifications passées !"))
            print(self.colors.GREEN + "Vous pouvez committer en toute sécurité." + self.colors.RESET)
        else:
            print(self.colors.error("[ERREUR] ÉCHEC - Certaines vérifications ont échoué"))
        
        if self.fixes_applied:
            print(f"\n{self.colors.BLUE}Corrections automatiques appliquées :{self.colors.RESET}")
            for fix in self.fixes_applied:
                print(f"  [OK] {fix}")
        
        if self.warnings:
            print(f"\n{self.colors.YELLOW}Avertissements :{self.colors.RESET}")
            for warning in self.warnings:
                print(f"  [ATTENTION]  {warning}")
        
        if self.errors:
            print(f"\n{self.colors.RED}Erreurs :{self.colors.RESET}")
            for error in self.errors:
                print(f"  [X] {error}")
        
        print(self.colors.header('=' * 60))


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Vérification pré-commit pour projet Django",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    python scripts/pre_commit_check.py
    python scripts/pre_commit_check.py --fix --yes
    python scripts/pre_commit_check.py --from-hook
    python scripts/pre_commit_check.py --only=security,tests
        """
    )
    
    parser.add_argument('--config', '-c', default='scripts/pre-commit-config.json',
                       help='Chemin vers le fichier de configuration')
    parser.add_argument('--fix', '-f', action='store_true',
                       help='Activer les corrections automatiques')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Répondre oui à toutes les questions (non-interactif)')
    parser.add_argument('--from-hook', action='store_true',
                       help='Mode hook git (non-interactif)')
    parser.add_argument('--only', type=str,
                       help='Vérifications spécifiques uniquement (séparées par virgule)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mode verbose')
    
    args = parser.parse_args()
    
    # Créer le checker
    checker = PreCommitChecker(args.config)
    
    # Appliquer les arguments
    if args.fix:
        checker.auto_fix = True
    if args.yes or args.from_hook:
        checker.interactive = False
        checker.auto_fix = True
    
    # Exécuter les vérifications
    try:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{checker.colors.YELLOW}Interrompu par l'utilisateur{checker.colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{checker.colors.RED}Erreur inattendue: {e}{checker.colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
