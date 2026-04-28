import os
import sys
import json
import joblib
import warnings
import io
import numpy as np

# Force UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

# Global variables for caching models
MODEL = None
TOKENIZER = None
INTENTS = None
RESPONSES = None

def load_resources():
    global MODEL, TOKENIZER, INTENTS, RESPONSES
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        
        model_path = 'model/qa/qa_model.keras'
        tok_path = 'model/qa/tokenizer.joblib'
        meta_path = 'model/qa/metadata.json'
        resp_path = 'model/qa/responses.json'

        if not all(os.path.exists(p) for p in [model_path, tok_path, meta_path, resp_path]):
            return False

        MODEL = keras.models.load_model(model_path)
        TOKENIZER = joblib.load(tok_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            INTENTS = json.load(f)['intents']
        with open(resp_path, 'r', encoding='utf-8') as f:
            RESPONSES = json.load(f)
        return True
    except Exception as e:
        print(f"Load Error: {e}", file=sys.stderr)
        return False

def predict_answer(question):
    if MODEL is None:
        if not load_resources():
            return "QA Engine Error: Models not ready. Please train the system."

    try:
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        
        # Preprocess
        seq = TOKENIZER.texts_to_sequences([question.lower()])
        padded = pad_sequences(seq, maxlen=40, padding='post')
        
        # Predict
        probs = MODEL.predict(padded, verbose=0)[0]
        idx = np.argmax(probs)
        conf = probs[idx]
        
        # Lower threshold for better responsiveness given expanded data
        if conf < 0.25:
            return "I'm not entirely sure about that specific detail, but I can tell you that renewable energy is the most sustainable choice. Could you try rephrasing?"

        intent = INTENTS[idx]
        full_response = RESPONSES.get(intent, "I'm still learning about that topic.")
        
        # Language Detection
        has_hindi = any('\u0900' <= char <= '\u097f' for char in question)
        
        if " / " in full_response:
            parts = full_response.split(" / ")
            if len(parts) == 2:
                return parts[1] if has_hindi else parts[0]
        
        return full_response

    except Exception as e:
        return f"Error in QA engine: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No question provided")
        sys.exit(1)
        
    question = sys.argv[1]
    print(predict_answer(question))
