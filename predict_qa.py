import os
import sys
import json
import joblib
import warnings
import io

# Force UTF-8 stdout on Windows so emoji/unicode pass through
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

def predict_answer(question):
    try:
        # Load the lightweight scikit-learn pipeline
        model_path = 'model/qa/qa_pipeline.joblib'
        if not os.path.exists(model_path):
            return "QA Engine Error: Model not found. Please train the model first."
            
        pipeline = joblib.load(model_path)
        
        with open('model/qa/metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        with open('model/qa/responses.json', 'r', encoding='utf-8') as f:
            responses = json.load(f)

            
        intents = metadata['intents']
        
        # Inference using the pipeline (Vectorization + Prediction)
        # pipeline.predict_proba returns a list of probabilities for each class
        probs = pipeline.predict_proba([question.lower()])[0]
        idx = probs.argmax()
        conf = probs[idx]
        
        # Confidence threshold
        if conf < 0.25:
            return "I'm not entirely sure about that specific detail, but I can tell you that renewable energy is the most sustainable choice for your environment. Could you try rephrasing your question?"
            
        intent = intents[idx]
        full_response = responses.get(intent, "I'm still learning about that topic.")
        
        # Language Detection: Check if the question contains Devanagari (Hindi) characters
        has_hindi = any('\u0900' <= char <= '\u097f' for char in question)
        
        # Split bilingual response if it exists
        if " / " in full_response:
            parts = full_response.split(" / ")
            if len(parts) == 2:
                # Return Hindi part if Hindi characters found, else English part
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
