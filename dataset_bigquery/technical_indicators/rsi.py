import logging
from .base_analysis import load_data, save_analysis, add_datetime_index

def calculate_rsi(data, window=14):
    try:
        delta = data['close_price'].diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()

        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
        return data[['ticker', 'date', 'RSI']]
    except Exception as e:
        logging.error(f"Erreur lors du calcul du RSI: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = 'dataset_bigquery/economic_data/economic_data.json'
    output_file = 'dataset_bigquery/technical_indicators/results/rsi.json'

    data = load_data(json_file)
    if data is not None:
        data = add_datetime_index(data)
        analyzed_data = calculate_rsi(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)
