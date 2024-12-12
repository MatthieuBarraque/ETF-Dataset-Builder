import json
import logging
import pandas as pd

def load_data(json_file):
    try:
        with open(json_file, 'r') as file:
            data = pd.read_json(file)
        logging.info(f"Données chargées depuis {json_file}")
        return data
    except Exception as e:
        logging.error(f"Erreur lors du chargement des données : {e}")
        return None

def save_analysis(data, output_file):
    try:
        with open(output_file, 'w') as file:
            json.dump(data.to_dict(orient='records'), file)
        logging.info(f"Analyse sauvegardée dans {output_file}")
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde de l'analyse : {e}")

def add_datetime_index(data):
    try:
        data['datetime'] = pd.to_datetime(data['date'])
        data.set_index('datetime', inplace=True)
        return data
    except Exception as e:
        logging.error(f"Erreur lors de l'ajout de l'index datetime : {e}")
        return data
