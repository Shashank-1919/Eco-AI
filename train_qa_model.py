import os
import json
import joblib
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 1. MASSIVELY Expanded Dataset (English + Hindi Script + Hinglish)
data = {
    "greeting": [
        "hi", "hello", "namaste", "pranam", "kaise ho", "suno", "namaskar", 
        "hey there", "good morning", "good evening", "adaab", "satsriakal",
        "नमस्ते", "प्रणाम", "नमस्कार", "राम राम", "सत श्री अकाल", "hello ecoai",
        "yo", "what's up", "hey", "hola"
    ],
    "identity": [
        "who are you", "what is your name", "tum kaun ho", "tera naam kya hai", 
        "kaun hai tu", "introduce yourself", "tell me about yourself", "what is ecoai",
        "तुम कौन हो", "आपका नाम क्या है", "इको-एआई के बारे में बताओ",
        "who made you", "are you a bot", "what are you", "identity",
        "अपना परिचय दें", "आप क्या करते हैं"
    ],
    "how_it_works": [
        "how you works", "how do you work", "kaise kaam karte ho", "how does this app work",
        "mechanism", "your logic", "how do you recommend energy", "kaise batate ho",
        "काम कैसे करते हो", "आपकी कार्यप्रणाली क्या है", "ये ऐप कैसे चलता है"
    ],
    "help": [
        "help me", "i need help", "madad karo", "help chahiye", "kaise use kare", 
        "what can you do", "guide me", "support", "how to use this app",
        "मेरी मदद करो", "सहायता चाहिए", "इसका उपयोग कैसे करें",
        "instructions", "user manual", "tell me what to do"
    ],
    "status": [
        "how are you", "theek ho", "kaam kar rahe ho", "kya haal hai", "are you alive", 
        "कैसे हो", "ठीक हो", "sab badhiya", "kaise chal raha hai"
    ],
    "appreciation": [
        "thank you", "thanks", "shukriya", "dhanyawad", "bahut acche", "great job", 
        "helpful", "amazing", "good advisor", "shabaash", "धन्यवाद", "शुक्रिया", "बहुत बढ़िया",
        "love this", "brilliant", "excellent"
    ],
    "farewell": ["bye", "goodbye", "alvida", "phir milenge", "chalo bye", "see you later", "tata", "अलविदा", "फिर मिलेंगे"],
    "general_definition": [
        "renewable energy kya hai", "clean energy kya hoti hai", "green energy batao", 
        "what is renewable energy", "define clean energy", "benefits of green power",
        "नवीकरणीय ऊर्जा क्या है", "स्वच्छ ऊर्जा के बारे में बताओ", "renewable definition"
    ],
    "solar_details": [
        "solar panel kaise kaam karta hai", "solar lagana hai", "dhoop se bijli", 
        "how does solar work", "working of solar panels", "photovoltaic cell details", "solar efficiency",
        "सोलर पैनल कैसे काम करता है", "सोलर प्लेट की जानकारी", "धूप से बिजली कैसे बनती है",
        "solar science", "pv technology"
    ],
    "wind_details": [
        "pawan chakkee kaise kaam karti hai", "hawa se bijli", "wind turbine", 
        "how does wind energy work", "wind power benefits", "wind turbine setup",
        "पवन चक्की की जानकारी", "हवा से बिजली कैसे बनती है", "विंड टर्बाइन",
        "wind energy science"
    ],
    "subsidies_gov": [
        "sarkari subsidy milegi kya", "sarkar ki scheme batao", "subsidy kaise apply kare", 
        "government subsidies", "pm-kusum scheme", "solar subsidy in india", "mnre incentives",
        "सरकारी सब्सिडी", "सरकारी योजनाएं", "छूट कैसे मिलेगी", "पीएम-कुसुम योजना",
        "free solar", "government help for solar"
    ],
    "costs_roi": [
        "kitna kharcha aayega", "paisa kab vasool hoga", "kitna budget chahiye", 
        "is it expensive", "return on investment", "payback period", "installation cost",
        "कितना खर्चा आएगा", "पैसा कब वसूल होगा", "बजट कितना होना चाहिए",
        "price of solar", "cost of wind turbine"
    ],
    "maintenance": [
        "cleaning panels", "maintenance kaise kare", "care and repair", "service", 
        "how to clean", "how to maintain", "maintenance cost", "service interval",
        "maintain solar panels", "wind turbine maintenance",
        "सोलर पैनल की सफाई", "रखरखाव कैसे करें", "सफाई कैसे करें", "सर्विसिंग", "मेंटेनेंस",
        "panel cleaning guide", "dirty panels", "cleaning solar panels", "how to clean panels"
    ],
    "environmental_impact": [
        "environment par kya asar hoga", "global warming", "co2 reduction", 
        "is it eco friendly", "pollution reduction", "save earth", "impact on nature",
        "पर्यावरण पर प्रभाव", "प्रदूषण में कमी", "धुआं और प्रदूषण", "पर्यावरण को फायदा",
        "carbon footprint", "climate change"
    ],
    "safety": [
        "kya ye safe hai", "safety precautions", "danger", "is it risky", 
        "hazard", "lightning protection", "electrical safety", "safety guide",
        "क्या यह सुरक्षित है", "सुरक्षा के उपाय", "बिजली का खतरा",
        "shock hazard", "fire safety"
    ],
    "location_advice": [
        "best place to install", "kaha lagaye", "location guide", "roof or ground", 
        "shadow problem", "direction to face", "ideal site",
        "कहाँ लगवाएं", "सबसे अच्छी जगह", "छत या ज़मीन",
        "where to put panels", "ideal position"
    ],
    "battery_storage": [
        "battery backup", "night time power", "storage system", "can i store energy", 
        "off grid vs on grid", "battery life", "inverter details",
        "बैटरी बैकअप", "रात में बिजली", "एनर्जी स्टोरेज",
        "lithium battery", "lead acid battery"
    ],
    "weather_impact": [
        "rainy season solar", "cloudy day power", "winter performance", "what if no sun",
        "baarish me kya hoga", "winter me solar kaam karega", "storm safety",
        "बारिश में सोलर", "बादल होने पर क्या होगा", "सर्दियों में बिजली",
        "what if it rains", "heavy rain", "monsoon impact", "snow on panels", "night time"
    ],
    "lifespan": [
        "how long it lasts", "life of solar panel", "durability", "warranty period",
        "kitne saal chalega", "solar ki life", "expiry date",
        "कितने साल चलेगा", "सोलर की उम्र", "वारंटी कितनी है",
        "how many years", "longevity", "replacement time"
    ],
    "home_appliances": [
        "can i run ac", "fridge on solar", "heavy appliances", "washing machine",
        "ac chalega", "pankha light on solar", "load capacity",
        "क्या एसी चलेगा", "फ्रिज और वाशिंग मशीन", "कितना लोड उठाएगा",
        "television", "geyser", "microwave", "induction stove"
    ],
    "area_required": [
        "how much space", "square feet needed", "area for 5kw", "land required",
        "kitni jagah chahiye", "kitna area lagega", "jagah kitni honi chahiye",
        "कितनी जगह चाहिए", "एरिया कितना लगेगा",
        "roof size", "how many panels fit", "mounting space"
    ],
    "comparison": [
        "solar vs wind", "which is better", "best renewable source", "comparison",
        "kaun sa achha hai", "solar ya wind", "best option",
        "कौन सा अच्छा है", "सोलर या विंड में अंतर",
        "difference between solar and wind", "solar or hydro"
    ],
    "efficiency": [
        "increase output", "max efficiency", "power generation low", "improve performance",
        "efficiency kaise badhaye", "jyada bijli kaise banaye",
        "क्षमता कैसे बढ़ाएं", "ज्यादा बिजली कैसे मिलेगी",
        "get more power", "optimize system"
    ],
    "net_metering": [
        "what is net metering", "sell power to grid", "bijli bechna hai", "excess energy",
        "grid export", "bi-directional meter", "kaise beche bijli",
        "नेट मीटरिंग क्या है", "बिजली ग्रिड को कैसे बेचें"
    ],
    "mounting_structures": [
        "roof mounting", "ground mount", "panel structure", "stand for solar",
        "angle of installation", "gi structure", "solar stand",
        "माउंटिंग स्ट्रक्चर", "पैनल का स्टैंड"
    ],
    "inverter_types": [
        "string inverter", "micro inverter", "hybrid inverter", "inverter difference",
        "which inverter is best", "sinewave inverter",
        "इन्वर्टर के प्रकार", "सबसे अच्छा इन्वर्टर कौन सा है"
    ]
}

texts, labels = [], []
intent_names = sorted(data.keys())
label_map = {name: i for i, name in enumerate(intent_names)}

for intent, sentences in data.items():
    for s in sentences:
        texts.append(s.lower())
        labels.append(label_map[intent])

# 2. Training Pipeline (Keras Deep Learning)
max_words = 2000
max_len = 40

tokenizer = Tokenizer(num_words=max_words, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
padded = pad_sequences(sequences, maxlen=max_len, padding='post')

labels = np.array(labels)

model = keras.Sequential([
    keras.layers.Embedding(max_words, 32, input_length=max_len),
    keras.layers.GlobalAveragePooling1D(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(len(intent_names), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print(f"Training Keras NLP model on {len(texts)} samples...")
model.fit(padded, labels, epochs=300, verbose=0)

# 3. Save Artifacts
os.makedirs('model/qa', exist_ok=True)
model.save('model/qa/qa_model.keras')
joblib.dump(tokenizer, 'model/qa/tokenizer.joblib')

with open('model/qa/metadata.json', 'w', encoding='utf-8') as f:
    json.dump({"intents": intent_names}, f, ensure_ascii=False)

# 4. Responses Mapping (Comprehensive & Bilingual)
responses = {
    "greeting": "Namaste! I am Eco-AI. How can I assist you today? / नमस्ते! मैं इको-एआई हूँ। मैं आज आपकी कैसे मदद कर सकता हूँ?",
    "identity": "I am Eco-AI, your advanced sustainable energy advisor. I help you choose the best renewable energy for your needs. / मैं इको-एआई हूँ, आपका हरित ऊर्जा सलाहकार। मैं आपको सही ऊर्जा स्रोत चुनने में मदद करता हूँ।",
    "how_it_works": "I use a hybrid Neuro-Fuzzy logic. I analyze your environmental data (wind, sun, water) using Keras deep learning and then apply expert fuzzy rules to give you the most reliable recommendation. / मैं एक हाइब्रिड न्यूरो-फजी लॉजिक का उपयोग करता हूँ। मैं आपके डेटा का विश्लेषण करता हूँ और आपको सटीक सलाह देता हूँ।",
    "help": "You can ask about solar, wind, subsidies, costs, maintenance, or appliance compatibility. / आप सोलर, पवन, सब्सिडी, लागत, रखरखाव या उपकरणों के बारे में पूछ सकते हैं।",
    "status": "I am operating at full capacity and ready to analyze your energy needs! / मैं पूरी क्षमता से काम कर रहा हूँ और आपकी ऊर्जा जरूरतों का विश्लेषण करने के लिए तैयार हूँ!",
    "appreciation": "You're very welcome! I'm glad I could provide clarity on your green energy journey. / आपका बहुत-बहुत स्वागत है! मुझे खुशी है कि मैं आपकी मदद कर सका।",
    "farewell": "Goodbye! Remember, every watt of clean energy helps our planet. / अलविदा! याद रखें, स्वच्छ ऊर्जा का हर वाट हमारे ग्रह की मदद करता है।",
    "general_definition": "Renewable energy is derived from natural processes that are replenished constantly, such as sunlight, wind, and water flow. / नवीकरणीय ऊर्जा उन प्राकृतिक प्रक्रियाओं से प्राप्त होती है जो लगातार नवीनीकृत होती हैं, जैसे सूर्य और हवा।",
    "solar_details": "Solar PV systems use semiconductor materials to convert sunlight photons directly into DC electricity via the photovoltaic effect. / सोलर पैनल अर्धचालक पदार्थों का उपयोग करके सूर्य के प्रकाश को सीधे बिजली में बदलते हैं।",
    "wind_details": "Wind turbines convert the kinetic energy of wind into mechanical power, which an internal generator then turns into electricity. / पवन चक्कियां हवा की गतिज ऊर्जा को बिजली में बदल देती हैं।",
    "subsidies_gov": "In India, schemes like PM-KUSUM and Rooftop Solar Yojana provide 30-40% subsidies for residential and agricultural setups. / भारत में पीएम-कुसुम जैसी योजनाएं 30-40% तक की सब्सिडी प्रदान करती हैं।",
    "costs_roi": "While initial costs can be high (e.g., 1-3 Lakhs for 3kW solar), the payback period is usually 5-8 years with 25 years of free energy. / शुरुआती लागत अधिक हो सकती है, लेकिन 5-8 साल में पैसा वसूल हो जाता है।",
    "maintenance": "Solar panels need water cleaning every 3 months. Wind turbines require annual bearing lubrication and structural checks. / सोलर पैनलों को हर 3 महीने में पानी से साफ करें। पवन चक्कियों की सालाना जांच जरूरी है।",
    "environmental_impact": "Switching to renewables eliminates CO2, SO2, and NOx emissions, significantly reducing your household's carbon footprint. / नवीकरणीय ऊर्जा अपनाने से कार्बन उत्सर्जन कम होता है और पर्यावरण सुरक्षित रहता है।",
    "safety": "Always use high-quality DC cables, proper earthing (grounding), and lightning arrestors to protect your equipment from surges. / सुरक्षा के लिए हमेशा अच्छी क्वालिटी के केबल और अर्थिंग का उपयोग करें।",
    "location_advice": "Solar needs an unshaded south-facing roof. Wind requires high ground away from trees or buildings that cause turbulence. / सोलर के लिए दक्षिण मुखी छत और विंड के लिए ऊंची, खुली जगह सबसे अच्छी होती है।",
    "battery_storage": "Off-grid systems use Lithium-ion or Lead-acid batteries to store energy for night use, while on-grid systems sell excess power back. / बैटरी स्टोरेज आपको रात में बिजली उपयोग करने की सुविधा देता है।",
    "weather_impact": "Solar works on light, not heat, so it still produces power on cloudy days (at lower efficiency). Modern panels are hail-resistant. / सोलर बादलों में भी काम करता है, हालांकि बिजली कम बनती है।",
    "lifespan": "Solar panels typically have a 25-year performance warranty. Wind turbines last 20-25 years with regular maintenance. / सोलर पैनल 25 साल तक चलते हैं और विंड टर्बाइन की उम्र 20-25 साल होती है।",
    "home_appliances": "A 5kW solar system can easily run ACs, Fridges, and Washing Machines. Always check your inverter's peak load capacity. / 5kW का सिस्टम एसी और फ्रिज जैसे भारी उपकरण आसानी से चला सकता है।",
    "area_required": "A standard 1kW solar setup requires approximately 100 sq. ft. of shadow-free area. Larger systems need proportional space. / 1kW सोलर के लिए लगभग 100 वर्ग फुट जगह की आवश्यकता होती है।",
    "comparison": "Solar is best for consistent sun and rooftops. Wind is superior in coastal or mountainous areas with speeds above 5m/s. / सोलर धूप वाले इलाकों के लिए और विंड तटीय इलाकों के लिए बेहतर है।",
    "efficiency": "Keep panels clean and ensure they are tilted at the optimal angle (usually 15-30 degrees in India) to maximize energy harvest. / पैनलों को साफ रखें और सही कोण पर लगाएं ताकि अधिकतम बिजली मिल सके।",
    "net_metering": "Net Metering allows you to export excess solar power to the grid and get credits on your electricity bill. / नेट मीटरिंग आपको ग्रिड को अतिरिक्त बिजली बेचने और बिल में छूट पाने की सुविधा देती है।",
    "mounting_structures": "Hot-dip galvanized (GI) or aluminum structures are best for mounting panels. They must be tilted at the local latitude angle. / माउंटिंग के लिए जीआई या एल्युमिनियम स्ट्रक्चर सबसे अच्छे होते हैं।",
    "inverter_types": "On-grid inverters are for saving bills, Off-grid for backup, and Hybrid inverters do both. Micro-inverters offer panel-level optimization. / ग्रिड इन्वर्टर बिल बचाने के लिए और ऑफ-ग्रिड बैकअप के लिए होते हैं।"
}

with open('model/qa/responses.json', 'w', encoding='utf-8') as f:
    json.dump(responses, f, ensure_ascii=False)

print("Keras NLP Training Success - Robust Model Saved.")
