
import logging
from dataset_bigquery.technical_indicators.base_analysis import load_data, save_analysis, add_datetime_index
import pandas as pd

def calculate_stochastic(data, window=14, smooth_window=3):
    """
    Calcule l'oscillateur stochastique.
    """
    try:
        low_min = data['low_price'].rolling(window=window).min()
        high_max = data['high_price'].rolling(window=window).max()
        data['%K'] = 100 * ((data['close_price'] - low_min) / (high_max - low_min))
        data['%D'] = data['%K'].rolling(window=smooth_window).mean()
        return data[['ticker', 'date', 'datetime', '%K', '%D']]
    except Exception as e:
        logging.error(f"Erreur lors du calcul de l'oscillateur stochastique: {e}")
        return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = '../economic_data/economic_data.json'
    output_file = 'stochastic_analysis.json'
    
    data = load_data(json_file)
    if data is not None:
        analyzed_data = calculate_stochastic(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)

if __name__ == "__main__":
    main()
