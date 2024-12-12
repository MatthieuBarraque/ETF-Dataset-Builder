# README: ETF LSTM Prediction Model

## Project Overview
This project provides a Python-based solution for predicting future prices of the SPY ETF (S&P 500) using advanced financial analysis techniques and a Long Short-Term Memory (LSTM) neural network. By combining technical indicators with machine learning, the model aims to deliver accurate insights into market trends.

---

## Features
- **Data Retrieval:** Automatically fetch historical SPY ETF data from Yahoo Finance using the `yfinance` library.
- **Technical Analysis Indicators:**
  - Moving Averages (10-day, 20-day)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Bollinger Bands
- **LSTM Model:** Build and train a robust LSTM network to predict future prices based on historical data and technical indicators.
- **Future Prediction:** Predict SPY ETF prices for the next 30 days based on current trends.
- **Early Stopping:** Prevent overfitting during model training using Keras callbacks.

---

## Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- Required libraries (install via `requirements.txt`):
  - `numpy`
  - `pandas`
  - `yfinance`
  - `scikit-learn`
  - `tensorflow`

---

## Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
1. **Run the Program:**
   ```bash
   python <script_name>.py
   ```
2. **Input Parameters:**
   - Modify the `start_date` and `end_date` variables in the script to specify the training period.
3. **Output:**
   - The script will output the predicted SPY ETF prices for the next 30 days.

---

## Key Components
1. **`get_spy_data(start_date, end_date)`**
   - Fetches historical SPY data and computes technical indicators.
   
2. **`prepare_data(df, window_size)`**
   - Scales the data and prepares it for LSTM training.
   
3. **`build_lstm_model(input_shape)`**
   - Constructs an LSTM model with dropout layers to prevent overfitting.
   
4. **`predict_future(model, df, scaler, days_ahead)`**
   - Predicts future ETF prices for the specified number of days.
   
5. **`train_and_evaluate_model(start_date, end_date)`**
   - Trains the model and evaluates its performance.

---

## Example Output
```plaintext
Fetching SPY historical data...
Training LSTM model with additional epochs...
Prediction for the next 30 days:
[[405.23]
 [407.65]
 ...
 [450.12]]
```