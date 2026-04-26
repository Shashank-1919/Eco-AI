import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier

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

    # Build MLP Classifier (Neural Network)
    # Using a similar architecture to what was intended in Keras
    clf = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        verbose=True
    )

    print("Training Neural Network model...")
    clf.fit(X_train_scaled, y_train)

    # Evaluate
    acc = clf.score(X_test_scaled, y_test)
    print(f"Test Accuracy: {acc:.4f}")

    # Save model
    model_path = os.path.join(model_dir, 'energy_model.joblib')
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_model()
