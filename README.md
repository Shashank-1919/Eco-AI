# 🌿 Eco-AI: Advanced Renewable Energy Advisor

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange?logo=tensorflow)
![Node.js](https://img.shields.io/badge/Node.js-20.x-green?logo=node.js)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Eco-AI** is a state-of-the-art, bilingual (English & Hindi) conversational advisor designed to accelerate the transition to sustainable energy. It combines **Deep Learning (Keras)** with **Expert Knowledge (Fuzzy Logic)** to provide hyper-personalized recommendations for solar, wind, and hybrid energy systems.

---

## 🧠 The Hybrid Intelligence Engine

Unlike standard chatbots, Eco-AI uses a **Neuro-Fuzzy Architecture**:

1.  **Neural Layer (Keras)**: A deep neural network trained on thousands of environmental data points. It predicts energy potential based on complex non-linear patterns in temperature, solar irradiance, wind speed, and humidity.
2.  **Fuzzy Layer (Expert Rules)**: A Mamdani-style fuzzy logic controller that applies human-expert constraints (e.g., location-based feasibility, budget limits, and safety overrides).
3.  **NLP Core**: A custom Keras Embedding model trained for semantic intent recognition in both English and Hindi scripts.

---

## 🚀 Key Features

-   **Bilingual Intelligence**: Chat naturally in English, Hindi (हिन्दी), or Hinglish.
-   **Neuro-Fuzzy Recommendations**: Combines probabilistic ML with deterministic expert rules for 100% reliable advice.
-   **Parameter-Driven**: Analyzes budget, location type (Coastal, Desert, Urban, etc.), roof area, and appliances.
-   **ROI Calculation**: Automatically estimates payback periods and government subsidies (e.g., PM-KUSUM).
-   **Privacy First**: Runs 100% locally. No data leaves your machine; no expensive API keys required.

---

## 🛠️ Technology Stack

-   **AI Framework**: TensorFlow 2.15 (Keras API)
-   **Logic Engine**: Scikit-Fuzzy (Mamdani Inference)
-   **Backend**: Node.js & Express (Bridge to Python Engine)
-   **Frontend**: Professional Vanilla CSS3 & Interactive JS
-   **Data**: Pandas, NumPy, Scikit-Learn (Preprocessing)

---

## 📁 Project Structure

```text
├── model/
│   ├── qa/                 # NLP Keras artifacts (.keras, tokenizer.joblib)
│   ├── energy_model.keras  # Trained energy prediction weights
│   ├── inference.py        # THE HYBRID ENGINE (Neuro + Fuzzy blending)
│   └── train_keras_model.py# Energy ML training pipeline
├── train_qa_model.py       # NLP training pipeline (English/Hindi)
├── run_inference.py        # JSON-API bridge for the Node.js server
├── server.js               # Main Express application
└── static/                 # Modern UI assets and animations
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)

### 2. Setup Virtual Environment (Recommended)
To avoid dependency conflicts and long-path issues on Windows:

```powershell
# Create environment
python -m venv .venv

# Activate environment
# On Windows:
.\.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start the Server
```bash
npm install
node server.js
```

---

## 🏃 Training the Intelligence

If you wish to retrain the models with fresh data:

1.  **Generate Data**: `python model/generate_dataset.py`
2.  **Train Energy ML**: `python model/train_keras_model.py`
3.  **Train NLP Engine**: `python train_qa_model.py`

*Note: All models are automatically saved as `.keras` artifacts for fast inference.*

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

**Eco-AI — Empowering a Greener Tomorrow, One Conversation at a Time.**
