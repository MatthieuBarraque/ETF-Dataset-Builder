import logging
from .base_analysis import load_data, save_analysis, add_datetime_index

def calculate_moving_averages(data, window_sma=20, window_ema=20):

    try:
        data['SMA'] = data['close_price'].rolling(window=window_sma).mean()
        data['EMA'] = data['close_price'].ewm(span=window_ema, adjust=False).mean()
        return data[['ticker', 'date', 'datetime', 'SMA', 'EMA']]
    except Exception as e:
        logging.error(f"Erreur lors du calcul des moyennes mobiles: {e}")
        return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = '../economic_data/economic_data.json'
    output_file = 'moving_averages_analysis.json'
    
    data = load_data(json_file)
    if data is not None:
        analyzed_data = calculate_moving_averages(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)

if __name__ == "__main__":
    main()
