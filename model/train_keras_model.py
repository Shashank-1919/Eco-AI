import pandas as pd
import numpy as np
import os
import joblib
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def train_model():
    # Load dataset
    model_dir = os.path.dirname(__file__)
    data_path = os.path.join(model_dir, 'energy_dataset.csv')
    if not os.path.exists(data_path):
        print("Dataset not found. Please run generate_dataset.py first.")
        return

    df = pd.read_csv(data_path)
    X = df.drop('target', axis=1)
    y = df['target']

    # Split and Scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler for inference
    scaler_path = os.path.join(model_dir, 'scaler.joblib')
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")

    # Build Keras Model
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(6, activation='softmax') # 6 classes: Solar, Wind, Hydro, Biomass, Geothermal, Tidal
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    print("Training Keras model...")
    model.fit(X_train_scaled, y_train, epochs=10, batch_size=32, validation_split=0.1, verbose=1)

    # Evaluate
    loss, acc = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"Test Accuracy: {acc:.4f}")

    # Save model
    model_path = os.path.join(model_dir, 'energy_model.keras')
    model.save(model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_model()
