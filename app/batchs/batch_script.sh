
# shellcheck disable=SC1128
#!/bin/bash

# Chemin vers le répertoire du projet
PROJECT_DIR="/Users/ddiop/dataScientest/DataScientest-project-DEC23"

# Activer l'environnement virtuel
source $PROJECT_DIR/dataScientest-projet-dec23-env/bin/activate

# Exécuter le script Python
python $PROJECT_DIR/batchs/batch.py