# Configuration Cron pour Gestion CCSA

## Installation

1. Rendre le script exécutable :
```bash
chmod +x /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh
```

2. Créer le répertoire de logs :
```bash
mkdir -p /home/noro8560/backup-gestionccsa
```

3. Créer la crontab :
```bash
crontab -e
```

## Tâches Cron recommandées

### Sauvegarde quotidienne à 2h du matin
```
0 2 * * * /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh
```

### Sauvegarde hebdomadaire (dimanche à 3h)
```
0 3 * * 0 /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh
```

### Sauvegarde mensuelle (1er du mois à 4h)
```
0 4 1 * * /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh
```

## Exemple complet (toutes les sauvegardes)

```bash
# Éditer la crontab
crontab -e

# Ajouter ces lignes :
# Backup quotidien à 2h00
0 2 * * * /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh

# Backup hebdomadaire complet (dimanche 3h00)
0 3 * * 0 /home/noro8560/backup-gestionccsa/scripts/backup_cron.sh

# Nettoyage des vieux logs (1er de chaque mois)
0 5 1 * * find /home/noro8560/backup-gestionccsa -name "*.log" -type f -mtime +30 -delete
```

## Vérification

Vérifier que la tâche cron est bien enregistrée :
```bash
crontab -l
```

Voir les logs de la dernière exécution :
```bash
tail -f /home/noro8560/backup-gestionccsa/backup.log
```

## Variables d'environnement

Si nécessaire, ajouter ces variables au début du script ou dans la crontab :

```bash
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/noro8560
```

## Droits

Assurez-vous que l'utilisateur a les droits sur :
- Le répertoire du projet Django
- Le répertoire de sauvegarde
- Les commandes pg_dump/mysqldump (si applicable)

## Sauvegarde avec rotation

Le système conserve automatiquement les N dernières sauvegardes (configurable dans l'interface).
Par défaut : 10 sauvegardes.
