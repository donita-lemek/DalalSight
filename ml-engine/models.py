import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pmdarima as pm
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Bidirectional # type: ignore
from sklearn.preprocessing import MinMaxScaler

class AutoARIMAModel:
    def __init__(self):
        self.model = None

    def fit(self, y):
        # Fit auto_arima to find best parameters and fit
        self.model = pm.auto_arima(y, seasonal=False, stepwise=True, suppress_warnings=True, error_action="ignore", max_p=3, max_q=3)
        return self

    def predict(self, steps=1):
        return self.model.predict(n_periods=steps)


class BiLSTMModel:
    def __init__(self, sequence_length=30):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()

    def _build_model(self, input_shape):
        model = Sequential()
        model.add(Bidirectional(LSTM(50, activation='relu', return_sequences=False), input_shape=input_shape))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        return model
        
    def _create_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)

    def fit(self, y: pd.Series, epochs=5, batch_size=16):
        # y should be the returns or prices to forecast
        scaled_data = self.scaler.fit_transform(y.values.reshape(-1, 1))
        X, y_seq = self._create_sequences(scaled_data)
        
        if len(X) == 0:
            return self # Not enough data
            
        self.model = self._build_model((self.sequence_length, 1))
        self.model.fit(X, y_seq, epochs=epochs, batch_size=batch_size, verbose=0)
        return self

    def predict(self, recent_data: pd.Series):
        if self.model is None or len(recent_data) < self.sequence_length:
            return 0.0 # Fallback
            
        scaled_recent = self.scaler.transform(recent_data.values[-self.sequence_length:].reshape(-1, 1))
        X_test = np.array([scaled_recent])
        pred_scaled = self.model.predict(X_test, verbose=0)
        pred = self.scaler.inverse_transform(pred_scaled)
        return pred[0][0]


class RFModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def fit(self, X, y):
        # Drop rows with NaN in features or target
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        self.model.fit(X[mask], y[mask])
        return self

    def predict(self, X):
        return self.model.predict(X)
