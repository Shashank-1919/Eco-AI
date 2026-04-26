# 🌍 Eco-AI: Renewable Energy Advisor

Eco-AI is a professional, bilingual (English & Hindi) conversational assistant designed to help users navigate the transition to sustainable energy. Leveraging advanced Machine Learning algorithms, it provides tailored recommendations for solar, wind, and other renewable sources based on user needs, budget, and location.

---

## 🚀 Key Features

- **Intelligent Prediction Engine**: Uses a custom-trained Keras Neural Network to analyze environmental data and provide energy recommendations.
- **Bilingual Support**: Full support for English and Hindi queries, making green energy accessible to a wider audience.
- **Interactive Dashboard**: A modern, responsive UI that visualizes energy recommendations and cost-benefit analyses.
- **Parameter-Aware Analysis**: Considers roof area, budget, location, and energy requirements to provide highly accurate suggestions.
- **Persistent Chat History**: Keeps track of your energy journey across sessions.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Backend**: Node.js, Express
- **AI/ML Engine**: Python, TensorFlow/Keras, Scikit-Learn
- **NLP Engine**: Custom Python-based natural language processing
- **Data Processing**: Pandas, Joblib

---

## 📁 Project Structure

```text
├── model/                  # AI Model and Training Scripts
│   ├── qa/                 # NLP Response Mappings and Weights (Ignored)
│   ├── energy_dataset.csv  # Training Data (Ignored)
│   └── inference.py        # Core Logic for Energy Recommendations
├── static/                 # Frontend Assets (CSS, JS, Images)
├── templates/              # HTML Templates
├── server.js               # Node.js Express Server
├── run_inference.py        # Python Bridge for AI Predictions
└── requirements.txt        # Python Dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- Gemini API Key

### 2. Environment Configuration
Create a `.env` file in the root directory (refer to `.env.example`):
```env
PORT=3000
```

### 3. Install Dependencies
**Backend (Node.js):**
```bash
npm install
```

**AI Engine (Python):**
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

1. Start the server:
   ```bash
   node server.js
   ```
2. Open your browser and navigate to `http://localhost:3000`.

---

## 🧠 Training the Models

If you wish to retrain the underlying models with new data:
1. Update `model/energy_dataset.csv`.
2. Run the training script:
   ```bash
   python train_qa_model.py
   ```
   *Note: Training scripts require additional dependencies listed in requirements.txt.*

---

## 📄 License
This project is licensed under the MIT License.

---

*Eco-AI — Empowering a Greener Tomorrow.*
