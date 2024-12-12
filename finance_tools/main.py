import pandas as pd
import json
import os
import logging

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
            indicator['ticker'] = ticker
            indicators_list.append(indicator)
        
        for anomaly in anomalies:
            anomaly['ticker'] = ticker
            anomalies_list.append(anomaly)
    
    return indicators_list, anomalies_list

def moving_averages(df):
    print("Calcul des moyennes mobiles...")
    df["MA_10"] = df["close_price"].rolling(window=10, min_periods=1).mean()
    df["MA_20"] = df["close_price"].rolling(window=20, min_periods=1).mean()
    return df

def rsi(df):
    print("Calcul du RSI...")
    delta = df["close_price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def bollinger_bands(df):
    print("Calcul des bandes de Bollinger...")
    df["MA_20"] = df["close_price"].rolling(window=20, min_periods=1).mean()
    df["Upper_Band"] = df["MA_20"] + 2 * df["close_price"].rolling(window=20, min_periods=1).std()
    df["Lower_Band"] = df["MA_20"] - 2 * df["close_price"].rolling(window=20, min_periods=1).std()
    return df

def macd(df):
    print("Calcul du MACD...")
    df["EMA_12"] = df["close_price"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["close_price"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

def stochastic(df):
    print("Calcul de l'oscillateur stochastique...")
    df["L14"] = df["close_price"].rolling(window=14, min_periods=1).min()
    df["H14"] = df["close_price"].rolling(window=14, min_periods=1).max()
    df["%K"] = 100 * (df["close_price"] - df["L14"]) / (df["H14"] - df["L14"])
    df["%D"] = df["%K"].rolling(window=3, min_periods=1).mean()
    return df

def calculate_adx(df, period=14):
    print("Calcul complet de l'ADX...")
    df['TR'] = df[['high_price', 'low_price', 'close_price']].apply(
        lambda x: max(x['high_price'] - x['low_price'],
                     abs(x['high_price'] - x['close_price']),
                     abs(x['low_price'] - x['close_price'])),
        axis=1
    )
    df['+DM'] = df['high_price'].diff().apply(lambda x: x if x > 0 else 0)
    df['-DM'] = df['low_price'].diff().apply(lambda x: -x if x < 0 else 0)

    df['ATR'] = df['TR'].rolling(window=period, min_periods=1).mean()
    df['+DI'] = 100 * (df['+DM'].rolling(window=period, min_periods=1).mean() / df['ATR'])
    df['-DI'] = 100 * (df['-DM'].rolling(window=period, min_periods=1).mean() / df['ATR'])
    df['DX'] = 100 * (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']))
    df['ADX'] = df['DX'].rolling(window=period, min_periods=1).mean()
    return df

def adx(df):
    print("Calcul de l'ADX...")
    df = calculate_adx(df)
    
    df['ADX_Signal'] = df.apply(
        lambda row: 'Buy' if row['ADX'] > 25 and row['+DI'] > row['-DI'] else
                    'Sell' if row['ADX'] > 25 and row['+DI'] < row['-DI'] else 'Hold', axis=1
    )
    return df

def generate_signals(df):
    print("Génération des signaux de trading...")
    df['MA_Signal'] = df.apply(
        lambda row: 'Buy' if row['MA_10'] > row['MA_20'] else 'Sell', axis=1
    )

    df['RSI_Signal'] = df["RSI"].apply(
        lambda x: 'Buy' if x < 30 else 'Sell' if x > 70 else 'Hold'
    )

    df['Bollinger_Signal'] = df.apply(
        lambda row: 'Buy' if row['close_price'] < row['Lower_Band'] else 'Sell' if row['close_price'] > row['Upper_Band'] else 'Hold', axis=1
    )

    df['MACD_Signal'] = df.apply(
        lambda row: 'Buy' if row['MACD'] > row['Signal_Line'] else 'Sell', axis=1
    )

    df['Stochastic_Signal'] = df.apply(
        lambda row: 'Buy' if row['%K'] < 20 else 'Sell' if row['%K'] > 80 else 'Hold', axis=1
    )
    return df

def detect_anomalies(df):
    print("Détection des anomalies croisées...")
    anomalies = []

    for i in range(1, len(df)):
        current = df.iloc[i]
        previous = df.iloc[i-1]

        if (current['MA_Signal'] == 'Buy' and current['RSI_Signal'] == 'Sell') or \
           (current['MA_Signal'] == 'Sell' and current['RSI_Signal'] == 'Buy'):
            anomalies.append({
                "Date": current['Date'],
                "Type": "Contradiction MA-RSI",
                "Details": {
                    "MA_Signal": current['MA_Signal'],
                    "RSI_Signal": current['RSI_Signal']
                }
            })

        if (current['MACD_Signal'] == 'Buy' and current['RSI_Signal'] == 'Sell') or \
           (current['MACD_Signal'] == 'Sell' and current['RSI_Signal'] == 'Buy'):
            anomalies.append({
                "Date": current['Date'],
                "Type": "Contradiction MACD-RSI",
                "Details": {
                    "MACD_Signal": current['MACD_Signal'],
                    "RSI_Signal": current['RSI_Signal']
                }
            })

        if (current['Bollinger_Signal'] == 'Buy' and current['RSI_Signal'] == 'Sell') or \
           (current['Bollinger_Signal'] == 'Sell' and current['RSI_Signal'] == 'Buy'):
            anomalies.append({
                "Date": current['Date'],
                "Type": "Contradiction Bollinger-RSI",
                "Details": {
                    "Bollinger_Signal": current['Bollinger_Signal'],
                    "RSI_Signal": current['RSI_Signal']
                }
            })

    return anomalies

def process_ticker(df, ticker):
    print(f"\n--- Traitement de l'ETF : {ticker} ---")
    df_ticker = df[df['ticker'] == ticker].copy()
    df_ticker = df_ticker.sort_values(by='Date')
    df_ticker = moving_averages(df_ticker)
    df_ticker = rsi(df_ticker)
    df_ticker = bollinger_bands(df_ticker)
    df_ticker = macd(df_ticker)
    df_ticker = stochastic(df_ticker)
    df_ticker = adx(df_ticker)
    df_ticker = generate_signals(df_ticker)
    anomalies = detect_anomalies(df_ticker)
    
    df_ticker['Date'] = df_ticker['Date'].dt.strftime('%Y-%m-%d')
    
    if 'date' in df_ticker.columns:
        df_ticker.drop(columns=['date'], inplace=True)
    
    return df_ticker, anomalies

def run_all_indicators(json_file, output_file):
    print("Lancement de tous les indicateurs...")
    data = load_data(json_file)
    if data is None:
        print("Erreur lors du chargement des données. Arrêt de l'exécution.")
        return

    indicators, anomalies = process_data(data)
    
    if indicators:
        save_csv(indicators, "indicators.csv", "indicateurs")
    else:
        print("Aucun indicateur à sauvegarder.")

    if anomalies:
        save_csv(anomalies, "anomalies.csv", "anomalies")
    else:
        print("Aucune anomalie à sauvegarder.")
    
    print("Conversion terminée.")

if __name__ == "__main__":
    input_json_file = "dataset_bigquery/economic_data/economic_data.json"
    output_json_file = "analysis_output.json"
    run_all_indicators(input_json_file, output_json_file)
