import sys
import time
import yfinance as yf
import json
import logging
import threading
from datetime import datetime
from pytz import timezone
from requests.exceptions import HTTPError, ConnectionError, Timeout
import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("etf_real_time_data.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

ETF_LIST = ['SPY', 'QQQ', 'EEM']
FETCH_INTERVAL = 60
MARKET_TIMEZONE = timezone('America/New_York')

file_lock = threading.Lock()

def is_market_open():
    """
    Vérifie si le marché est ouvert actuellement.
    """
    now = datetime.now(MARKET_TIMEZONE)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

def fetch_real_time_data(ticker, retries=3, delay=5):
    """
    Récupère les données en temps réel pour un ETF donné avec des retraits en cas de volume nul.
    """
    logging.info(f"Début de la récupération des données pour {ticker}")
    attempt = 0
    while attempt < retries:
        try:
            if not is_market_open():
                logging.info("Le marché est fermé. Aucune donnée en temps réel disponible.")
                return None

            etf = yf.Ticker(ticker)
            data = etf.history(period='1d', interval='1m')
            if data.empty:
                logging.warning(f"Aucune donnée en temps réel disponible pour {ticker}")
                return None
            latest_data = data.tail(1).iloc[0]

            data_point = {
                'ticker': ticker,
                'date': latest_data.name.tz_convert(MARKET_TIMEZONE).strftime('%Y-%m-%d'),
                'datetime': latest_data.name.tz_convert(MARKET_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
                'open_price': float(latest_data['Open']),
                'close_price': float(latest_data['Close']),
                'high_price': float(latest_data['High']),
                'low_price': float(latest_data['Low']),
                'volume': int(latest_data['Volume']) if not pd.isna(latest_data['Volume']) else 0
            }

            logging.info(f"Données récupérées pour {ticker}: {data_point}")

            return data_point

        except (HTTPError, ConnectionError, Timeout) as e:
            logging.error(f"Erreur de connexion lors de la récupération des données pour {ticker}: {e}")
            attempt += 1
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Erreur inattendue lors de la récupération des données pour {ticker}: {e}")
            return None

    logging.error(f"Échec de la récupération des données pour {ticker} après {retries} tentatives.")
    return None

def save_data(data_point):
    """
    Sauvegarde les données dans un fichier JSON sans duplications.
    Utilise un verrou pour éviter les accès concurrents au fichier.
    """
    if data_point is None:
        return

    try:
        filename = f"real_time_data_{datetime.now(MARKET_TIMEZONE).strftime('%Y%m%d')}.json"

        with file_lock:
            try:
                with open(filename, 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                existing_data = []
            except json.JSONDecodeError as e:
                logging.error(f"Erreur de décodage JSON lors de la lecture du fichier {filename}: {e}")
                existing_data = []

            if any(d['ticker'] == data_point['ticker'] and d['datetime'] == data_point['datetime'] for d in existing_data):
                logging.info(f"Données déjà présentes pour {data_point['ticker']} à {data_point['datetime']}. Ignorées.")
                return

            existing_data.append(data_point)

            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

            logging.info(f"Données sauvegardées dans le fichier {filename}")

    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde des données: {e}")

def process_ticker(ticker):
    data_point = fetch_real_time_data(ticker)
    if data_point:
        save_data(data_point)

def main():
    logging.info("Démarrage du programme de récupération des données en temps réel")

    while True:
        if not is_market_open():
            logging.info("Le marché est fermé. En attente de l'ouverture du marché.")
            time.sleep(60)
            continue

        threads = []
        for ticker in ETF_LIST:
            thread = threading.Thread(target=process_ticker, args=(ticker,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        logging.info(f"Attente de {FETCH_INTERVAL} secondes avant la prochaine récupération")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Arrêt du programme par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erreur critique dans le programme principal: {e}")
        sys.exit(1)
