import pandas as pd
import json
import os
import logging

# Configuration du logging pour enregistrer les événements du parsing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("json_parsing.log"),
        logging.StreamHandler()
    ]
)

def load_data(json_file):
    print("Chargement des données à partir du fichier JSON...")
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Erreur : Le fichier {json_file} n'a pas été trouvé.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur : Le fichier {json_file} n'est pas un JSON valide. {e}")
        return None

def save_csv(data, output_file, data_type):
    print(f"Sauvegarde des {data_type} dans {output_file}...")
    try:
        df = pd.DataFrame(data)
        # Remplacer les NaN par None pour une meilleure compatibilité
        df = df.where(pd.notnull(df), None)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Les {data_type} ont été sauvegardés avec succès dans {output_file}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des {data_type} : {e}")

def process_data(data):
    indicators_list = []
    anomalies_list = []

    for ticker, content in data.items():
        indicators = content.get('indicators', [])
        anomalies = content.get('anomalies', [])

        for indicator in indicators:
            if 'date' in indicator:
                del indicator['date']  # Supprimer la colonne 'date' pour éviter la duplication
            indicator['ticker'] = ticker  # Ajouter le ticker pour référence
            indicators_list.append(indicator)
        
        for anomaly in anomalies:
            anomaly['ticker'] = ticker  # Ajouter le ticker pour référence
            anomalies_list.append(anomaly)
    
    return indicators_list, anomalies_list

def run_conversion(input_json, indicators_csv, anomalies_csv):
    data = load_data(input_json)
    if data is None:
        print("Erreur lors du chargement des données. Arrêt de l'exécution.")
        return
    
    indicators, anomalies = process_data(data)
    
    if indicators:
        save_csv(indicators, indicators_csv, "indicateurs")
    else:
        print("Aucun indicateur à sauvegarder.")
    
    if anomalies:
        save_csv(anomalies, anomalies_csv, "anomalies")
    else:
        print("Aucune anomalie à sauvegarder.")
    
    print("Conversion terminée.")

if __name__ == "__main__":
    # Chemin vers le fichier JSON d'entrée
    input_json_file = "analysis_output.json"
    # Chemins vers les fichiers CSV de sortie
    indicators_csv_file = "indicators.csv"
    anomalies_csv_file = "anomalies.csv"
    run_conversion(input_json_file, indicators_csv_file, anomalies_csv_file)
