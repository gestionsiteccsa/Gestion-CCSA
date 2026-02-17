#!/bin/bash
# Script de sauvegarde automatique pour Gestion CCSA
# À placer dans /home/noro8560/backup-gestionccsa/scripts/

# Configuration
PROJECT_DIR="/home/noro8560/gestion-ccsa"
VENV_PATH="$PROJECT_DIR/env/bin/python"
LOG_FILE="/home/noro8560/backup-gestionccsa/backup.log"

# Date du jour
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Démarrage de la sauvegarde automatique" >> $LOG_FILE

# Aller dans le répertoire du projet
cd $PROJECT_DIR

# Activer l'environnement virtuel et exécuter la commande
$VENV_PATH manage.py create_backup --auto --type full >> $LOG_FILE 2>&1

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo "[$DATE] Sauvegarde terminée avec succès" >> $LOG_FILE
else
    echo "[$DATE] ERREUR lors de la sauvegarde" >> $LOG_FILE
fi

echo "----------------------------------------" >> $LOG_FILE
