import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping

def get_spy_data(start_date, end_date):
    print("Récupération des données historiques de l'ETF SPY...")
    spy = yf.download('SPY', start=start_date, end=end_date)
    spy.reset_index(inplace=True)
    
    spy['MA_10'] = spy['Close'].rolling(window=10).mean()
    spy['MA_20'] = spy['Close'].rolling(window=20).mean()

    delta = spy['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    spy['RSI'] = 100 - (100 / (1 + rs))

    spy['EMA_12'] = spy['Close'].ewm(span=12, adjust=False).mean()
    spy['EMA_26'] = spy['Close'].ewm(span=26, adjust=False).mean()
    spy['MACD'] = spy['EMA_12'] - spy['EMA_26']
    spy['Signal_Line'] = spy['MACD'].ewm(span=9, adjust=False).mean()

    spy['Stddev'] = spy['Close'].rolling(window=20).std()
    spy['Upper_Band'] = spy['Close'].rolling(window=20).mean() + (spy['Stddev'] * 2)
    spy['Lower_Band'] = spy['Close'].rolling(window=20).mean() - (spy['Stddev'] * 2)

    return spy[['Date', 'Close', 'MA_10', 'MA_20', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Lower_Band']]

def prepare_data(df, window_size=60):
    print("Préparation des données pour LSTM...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scaled = scaler.fit_transform(df[['Close', 'MA_10', 'MA_20', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Lower_Band']])

    X, y = [], []
    for i in range(window_size, len(df_scaled)):
        X.append(df_scaled[i-window_size:i])
        y.append(df_scaled[i, 0])
    
    X, y = np.array(X), np.array(y)
    return X, y, scaler

def build_lstm_model(input_shape):
    print("Construction du modèle LSTM optimisé...")
    model = Sequential()

    model.add(LSTM(units=100, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.3))

    model.add(LSTM(units=100, return_sequences=True))
    model.add(Dropout(0.3))

    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.3))

    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def predict_future(model, df, scaler, window_size=60, days_ahead=30):
    print(f"Prédiction pour les {days_ahead} jours à venir...")
    future_prices = []
    
    last_window = df[-window_size:]
    scaled_window = scaler.transform(last_window)
    
    for _ in range(days_ahead):
        scaled_window = np.array(scaled_window).reshape(1, -1, 8)  # 8 features
        predicted_price = model.predict(scaled_window)
        future_prices.append(predicted_price[0][0])
        
        scaled_window = np.append(scaled_window[0, 1:, :], predicted_price)
    
    future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))
    return future_prices

def train_and_evaluate_model(start_date, end_date):
    spy_data = get_spy_data(start_date, end_date)
    
    window_size = 60
    X_train, y_train, scaler = prepare_data(spy_data, window_size)
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
    
    print("Entraînement du modèle LSTM avec des epochs supplémentaires...")
    model.fit(X_train, y_train, epochs=150, batch_size=32, callbacks=[early_stopping])
    future_prices = predict_future(model, spy_data[['Close', 'MA_10', 'MA_20', 'RSI', 'MACD', 'Signal_Line', 'Upper_Band', 'Lower_Band']], scaler)
    return future_prices

if __name__ == "__main__":
    start_date = '2020-01-01'
    end_date = '2024-01-01'
    future_predictions = train_and_evaluate_model(start_date, end_date)
    print("Prédictions des 30 prochains jours:")
    print(future_predictions)
