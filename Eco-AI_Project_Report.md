# LOVELY PROFESSIONAL UNIVERSITY
## Department of Computer Science & Engineering

**ACADEMIC TASK – 3**
**INT428 (ARTIFICIAL INTELLIGENCE)**

# Eco-AI: Advanced Renewable Energy Advisor

**Submitted by:**
Mahesh Raj
**Registration No.:** 12414465
**Roll No.:** 05
**Section:** 324ZN

**Submitted to:**
Dr. Jimmy Sighla

**Session:** 2025–26

---

## TABLE OF CONTENTS
1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Project Architecture & Files](#3-project-architecture--files)
4. [The Hybrid Intelligence Engine (Neuro-Fuzzy)](#4-the-hybrid-intelligence-engine-neuro-fuzzy)
5. [Key Features & System Logic](#5-key-features--system-logic)
6. [Current Project Status](#6-current-project-status)
7. [How to Run](#7-how-to-run)
8. [Challenges Faced](#8-challenges-faced)
9. [Planned Next Steps](#9-planned-next-steps)
10. [References](#10-references)
11. [System Snapshots](#11-system-snapshots)
12. [Appendix: Evaluation Questionnaire](#12-appendix-evaluation-questionnaire)

---

## 1. INTRODUCTION
**Eco-AI** is a sophisticated, bilingual (English & Hindi) conversational advisor designed to accelerate the global transition to sustainable energy. Unlike traditional recommendation systems, Eco-AI leverages a **Neuro-Fuzzy Architecture** that combines the predictive power of Deep Learning with the transparency of Expert Rule-based systems. 

The system allows users to interact naturally via a chat interface, providing details such as their location, budget, and energy requirements. It then performs a deep analysis of environmental parameters (temperature, solar irradiance, wind speed) and financial constraints to recommend the most optimal renewable energy solution (Solar, Wind, Hydro, Biomass, Geothermal, or Tidal).

## 2. PROBLEM STATEMENT
Transitioning to renewable energy is a complex decision-making process involving multiple variables:
- **Environmental Feasibility**: Different regions have varying potentials for solar, wind, or hydro power.
- **Financial Constraints**: Initial investment costs and payback periods are critical for users.
- **Expert Knowledge Gap**: Most users lack the technical expertise to calculate ROI, subsidies, and system suitability.
- **Language Barrier**: Many potential users in regions like India prefer communicating in their native language (Hindi).

Eco-AI bridges this gap by providing an intuitive, AI-driven platform that simplifies technical data into actionable advice.

## 3. PROJECT ARCHITECTURE & FILES
The project is built using a modern full-stack architecture, integrating a Node.js/Express backend with a Python-based AI engine.

| File/Directory | Purpose | Status |
| :--- | :--- | :--- |
| `server.js` | Main Express server handling authentication, routing, and AI bridge. | Complete |
| `models/` | MongoDB schemas for User management and Chat history persistence. | Complete |
| `templates/` | EJS/HTML templates (Index, Login, Result Dashboard). | Complete |
| `static/` | Frontend assets (CSS animations, Client-side JavaScript). | Complete |
| `run_inference.py` | Python bridge that executes the Hybrid AI Engine. | Complete |
| `train_qa_model.py` | Training script for the Bilingual NLP Intent Recognition model. | Complete |
| `model/` | Contains trained Keras models and metadata (tokenizer, weights). | Complete |
| `requirements.txt` | Python dependencies (TensorFlow, Scikit-Fuzzy, etc.). | Complete |

## 4. THE HYBRID INTELLIGENCE ENGINE (NEURO-FUZZY)
Eco-AI does not rely on a single model. It uses a **Hybrid Neuro-Fuzzy System**:

1. **Neural Layer (Keras)**: A Deep Neural Network trained on thousands of samples to predict energy potential based on non-linear environmental patterns.
2. **Fuzzy Layer (Expert Rules)**: A Mamdani-style Fuzzy Logic controller that applies expert constraints (e.g., location-specific safety, budget overrides, and ROI thresholds).
3. **NLP Core**: A custom Keras Embedding model for semantic intent recognition, supporting English, Hindi, and "Hinglish".

## 5. KEY FEATURES & SYSTEM LOGIC
- **Bilingual Interaction**: Users can chat in English or Hindi. The system uses a trained NLP model to extract parameters from natural language.
- **Parameter-Driven Analysis**: Considers temperature, humidity, wind speed, solar irradiance, water availability, biomass feedstock, and budget.
- **ROI & Subsidy Estimation**: Calculates payback periods and government subsidies (e.g., PM-KUSUM) based on the user's budget and location.
- **Interactive Dashboard**: A premium UI that visualizes suitability scores, environmental impact, and cost-benefit analysis.
- **Authentication & Persistence**: Secure login (including Google OAuth) and persistence of chat history using MongoDB.

## 6. CURRENT PROJECT STATUS
The project has evolved from a simple data generator into a **fully functional full-stack web application**. 
- [x] Backend API & Server Logic
- [x] MongoDB Integration (Auth & Chats)
- [x] Hybrid AI Engine (Neuro + Fuzzy)
- [x] Bilingual NLP Model
- [x] Interactive Frontend & Result Dashboard
- [x] Persistent Chat History & Session Management

## 7. HOW TO RUN
### Step 1 – Environment Setup
1. Create a Python virtual environment: `python -m venv .venv`
2. Activate it: `.\.venv\Scripts\activate` (Windows)
3. Install Python dependencies: `pip install -r requirements.txt`

### Step 2 – Backend Setup
1. Install Node dependencies: `npm install`
2. Configure `.env` file with MongoDB URI and Port.

### Step 3 – Run the Application
1. Start the server: `node server.js`
2. Open `http://localhost:3000` in your browser.

## 8. CHALLENGES FACED
- **Bilingual Tokenization**: Handling Hindi script and English interchangeably required a custom tokenizer and robust embedding layer.
- **Hybrid Blending**: Balancing the probabilistic output of the Neural Network with the deterministic rules of Fuzzy Logic to ensure "expert-level" reliability.
- **Performance**: Optimizing the bridge between Node.js and Python to ensure real-time chat responses.

## 9. PLANNED NEXT STEPS
1. **IoT Integration**: Fetching real-time environmental data from local sensors or APIs.
2. **Enhanced Visualization**: Integrating 3D maps to visualize energy potential in specific geographical coordinates.
3. **Mobile App**: Porting the interface to a React Native application for wider accessibility.

## 10. REFERENCES
- **TensorFlow Documentation**: https://www.tensorflow.org/
- **Scikit-Fuzzy Library**: https://pythonhosted.org/scikit-fuzzy/
- **Mongoose (MongoDB) Documentation**: https://mongoosejs.com/
- **Ministry of New and Renewable Energy (MNRE)**: https://mnre.gov.in

---

## 11. SYSTEM SNAPSHOTS
*(Note: These are descriptions of the screens provided in the actual application)*

- **Figure 1: User Login**: A premium login screen with glassmorphism effects and animated background.
- **Figure 2: AI Chat Interface**: A clean, conversational UI supporting bilingual queries.
- **Figure 3: Result Dashboard**: A detailed breakdown of the recommended energy source with ROI charts and suitability scores.
- **Figure 4: Environmental Impact**: Visualization of CO2 reduction and trees saved by adopting the recommended system.

---

## 12. APPENDIX: EVALUATION QUESTIONNAIRE
**INT428 – Project Evaluation Questionnaire**

| Field | Detail |
| :--- | :--- |
| **Student Name** | Mahesh Raj |
| **Roll Number** | 05 |
| **Branch & Semester** | CSE – Semester IV |
| **Project Title** | Eco-AI: Advanced Renewable Energy Advisor |
| **Faculty Name** | Dr. Jimmy Sighla |
| **Section** | 324ZN |

### Section A – Project Overview
**Q1. Type of system developed:**
A full-stack, AI-driven web application using a Neuro-Fuzzy hybrid architecture for renewable energy recommendations.

**Q2. Platform:**
Web-based (Node.js/Express) with a Python AI backend.

**Q3. Deployment link:**
Running locally (Production-ready).

### Section B – Model and API Details
**Q4. API used:**
Custom internal API bridge between Node.js and Python. No paid external AI APIs (OpenAI/Gemini) are used for core logic to ensure privacy and zero-cost operation.

**Q5. Model name:**
Custom Neuro-Fuzzy Hybrid Model (Keras + Scikit-Fuzzy).

**Q6. Model version:**
v2.0 (Bilingual Support Integrated).

### Section C – Data Handling
**Q7. Memory or session handling:**
MongoDB is used to persist user profiles and chat sessions.

**Q8. Data flow:**
User Input (Chat) → Node.js Server → Python AI Engine (NLP + Hybrid Model) → Results Dashboard (JSON) → MongoDB (Save).

### Section D – Technology Stack
- **Language**: Python 3.10+, JavaScript (Node.js)
- **AI/ML**: TensorFlow/Keras, Scikit-Fuzzy, NumPy, Pandas
- **Database**: MongoDB (Mongoose)
- **Frontend**: EJS, HTML5, CSS3 (Glassmorphism), Vanilla JS

---
**Declaration**
I confirm that all information in this report is accurate and that this is my original work submitted for INT428.

**Student Signature:** _______________________________          **Date:** 28th April 2026

-- End of Report --
