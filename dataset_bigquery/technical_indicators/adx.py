# technical_indicators/adx.py

import logging
from .base_analysis import load_data, save_analysis, add_datetime_index
import numpy as np
import pandas as pd

def calculate_adx(data, window=14):
    """
    Calcule l'Indice Directionnel Moyen (ADX).
    """
    try:
        # Calcul du True Range (TR)
        high = data['high_price']
        low = data['low_price']
        close = data['close_price']
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        data['TR'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calcul des Directional Movements (+DM et -DM)
        data['+DM'] = np.where((high - high.shift(1)) > (low.shift(1) - low), 
                               np.maximum(high - high.shift(1), 0), 0)
        data['-DM'] = np.where((low.shift(1) - low) > (high - high.shift(1)), 
                               np.maximum(low.shift(1) - low, 0), 0)
        
        # Calcul des moyennes mobiles exponentielles des TR, +DM, -DM
        tr_avg = data['TR'].rolling(window=window).mean()
        plus_dm_avg = data['+DM'].rolling(window=window).mean()
        minus_dm_avg = data['-DM'].rolling(window=window).mean()
        
        # Calcul des DI
        data['+DI'] = 100 * (plus_dm_avg / tr_avg)
        data['-DI'] = 100 * (minus_dm_avg / tr_avg)
        
        # Calcul du DX et de l'ADX
        data['DX'] = 100 * (abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI']))
        data['ADX'] = data['DX'].rolling(window=window).mean()
        
        return data[['ticker', 'date', 'datetime', 'ADX']]
    
    except Exception as e:
        logging.error(f"Erreur lors du calcul de l'ADX: {e}")
        return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    json_file = '../economic_data/economic_data.json'
    output_file = 'adx_analysis.json'
    
    data = load_data(json_file)
    if data is not None:
        analyzed_data = calculate_adx(data)
        if analyzed_data is not None:
            save_analysis(analyzed_data, output_file)

if __name__ == "__main__":
    main()
