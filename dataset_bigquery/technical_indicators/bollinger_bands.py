
import logging
from .base_analysis import load_data, save_analysis, add_datetime_index

def calculate_bollinger_bands(data, window=20):
    try:
        sma = data['close_price'].rolling(window=window).mean()
        stddev = data['close_price'].rolling(window=window).std()
        data['Upper_Band'] = sma + (stddev * 2)
        data['Lower_Band'] = sma - (stddev * 2)
        return data[['ticker', 'date', 'datetime', 'Upper_Band', 'Lower_Band']]
    except Exception as e:
        logging.error(f"Erreur lors du calcul des bandes de Bollinger: {e}")
        return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = '../economic_data/economic_data.json'
    output_file = 'bollinger_bands_analysis.json'
    
    data = load_data(json_file)
    if data is not None:
        analyzed_data = calculate_bollinger_bands(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)

if __name__ == "__main__":
    main()
