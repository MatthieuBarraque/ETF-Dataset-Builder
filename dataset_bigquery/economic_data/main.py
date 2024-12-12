import sys
import yfinance as yf
import json
from datetime import datetime

def main():
    print("Testing implementation for table: economic_data")
    etf_list = ['SPY', 'QQQ', 'EEM']
    start_date = '2020-01-01'
    end_date = datetime.today().strftime('%Y-%m-%d')
    all_data = []

    for ticker in etf_list:
        print(f"Récupération des données pour {ticker}")
        etf = yf.Ticker(ticker)
        historical_data = etf.history(start=start_date, end=end_date, interval='1d')
        if historical_data.empty:
            print(f"Aucune donnée trouvée pour {ticker}")
            continue
        historical_data = historical_data.reset_index()
        for index, row in historical_data.iterrows():
            data_point = {
                'ticker': ticker,
                'date': row['Date'].strftime('%Y-%m-%d'),
                'datetime': row['Date'].strftime('%Y-%m-%d %H:%M:%S'),
                'open_price': row['Open'],
                'close_price': row['Close'],
                'high_price': row['High'],
                'low_price': row['Low'],
                'volume': int(row['Volume'])
            }
            all_data.append(data_point)
    with open('economic_data.json', 'w') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False, default=str)

    print("Données enregistrées dans le fichier 'economic_data.json'.")

if __name__ == "__main__":
    main()
