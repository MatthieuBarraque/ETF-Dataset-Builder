#!/bin/bash

# Liste des tables
tables=("etf_market_data" "technical_indicators" "economic_data" "sector_data" "market_sentiment" "etf_specifics")

# Créer le répertoire principal du projet
mkdir -p dataset_bigquery
cd pdataset_bigquery

# Pour chaque table, créer un dossier et un script Python
for table in "${tables[@]}"
do
    mkdir -p "$table"
    cd "$table"

    # Créer un script Python main.py avec un squelette de code
    cat <<EOL > main.py
import sys

def main():
    print("Testing implementation for table: $table")
    # TODO: Implement data retrieval and processing for $table

if __name__ == "__main__":
    main()
EOL

    cd ..
done

echo "Architecture créée avec succès dans le dossier 'dataset_bigquery'."
