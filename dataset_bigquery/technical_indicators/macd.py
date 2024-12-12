
import logging
from .base_analysis import load_data, save_analysis, add_datetime_index

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    try:
        ema_short = data['close_price'].ewm(span=short_window, adjust=False).mean()
        ema_long = data['close_price'].ewm(span=long_window, adjust=False).mean()
        data['MACD'] = ema_short - ema_long
        data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
        return data[['ticker', 'date', 'datetime', 'MACD', 'Signal_Line']]
    except Exception as e:
        logging.error(f"Erreur lors du calcul du MACD: {e}")
        return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = '../economic_data/economic_data.json'
    output_file = 'macd_analysis.json'
    
    data = load_data(json_file)
    if data is not None:
        analyzed_data = calculate_macd(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)

if __name__ == "__main__":
    main()
