import sys
import json
import re
import io
from model.inference import predict_renewable_energy

# Force UTF-8 stdout on Windows so emoji/unicode pass through
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# ─────────────────────────────────────────────────────────────────────────────
# NLP EXTRACTION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_budget(text: str) -> float | None:
    """Extract budget value in INR or USD from natural language."""
    t = text.lower()

    # Handle crore (e.g. "2 crore", "1.5cr")
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:crore|cr)\b', t)
    if m:
        return float(m.group(1)) * 10_000_000

    # Handle lakh (e.g. "5 lakh", "3.5L", "2l")
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|l\b)', t)
    if m:
        return float(m.group(1)) * 100_000

    # Handle k suffix (e.g. "50k", "$15k")
    m = re.search(r'[₹$]?\s*(\d+(?:\.\d+)?)\s*k\b', t)
    if m:
        return float(m.group(1)) * 1000

    # INR with symbol (e.g. "₹50000", "₹ 2,50,000")
    m = re.search(r'₹\s*([\d,]+)', t)
    if m:
        return float(m.group(1).replace(',', ''))

    # USD (e.g. "$15000", "$ 20,000")
    m = re.search(r'\$\s*([\d,]+)', t)
    if m:
        usd = float(m.group(1).replace(',', ''))
        return usd * 83  # approx INR conversion

    # Plain number near budget keywords (expanded)
    m = re.search(r'(?:budget|cost|afford|invest|spend|have|around|approx|under|below)\s+(?:of\s+)?(?:₹|rs\.?|inr)?\s*([\d,]+)', t)
    if m:
        return float(m.group(1).replace(',', ''))

    # Plain number followed by budget keywords (e.g. "50000 budget")
    m = re.search(r'([\d,]+)\s*(?:budget|cost|investment|inr|rs\.?|rupees)', t)
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except:
            pass

    # Any big number fallback
    m = re.search(r'\b(\d{4,7})\b', t)
    if m:
        return float(m.group(1))

    return None


def _extract_temperature(text: str) -> float | None:
    t = text.lower()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:°\s*c|celsius|degrees?\s*c|°)', t)
    if m:
        return float(m.group(1))
    # Keyword-based
    if any(w in t for w in ['very hot', 'extremely hot', 'scorching', 'desert heat']):
        return 44.0
    if any(w in t for w in ['hot', 'warm', 'sunny and hot', 'tropical']):
        return 35.0
    if any(w in t for w in ['moderate', 'mild', 'pleasant', 'temperate']):
        return 23.0
    if any(w in t for w in ['cold', 'cool', 'chilly']):
        return 12.0
    if any(w in t for w in ['very cold', 'freezing', 'arctic', 'snowy']):
        return 3.0
    return None


def _extract_humidity(text: str) -> float | None:
    t = text.lower()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:%\s*humidity|% humid|humidity\s*%)', t)
    if m:
        return float(m.group(1))
    m = re.search(r'humidity\s+(?:of\s+)?(\d+(?:\.\d+)?)', t)
    if m:
        return float(m.group(1))
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', t)
    if m:
        val = float(m.group(1))
        if 0 < val <= 100:
            return val
    # Keyword-based
    if any(w in t for w in ['very humid', 'very damp', 'very wet', 'tropical humid']):
        return 88.0
    if any(w in t for w in ['humid', 'damp', 'wet', 'muggy', 'rainy']):
        return 72.0
    if any(w in t for w in ['moderate humidity', 'moderate moisture']):
        return 52.0
    if any(w in t for w in ['dry', 'arid', 'low humidity']):
        return 22.0
    if any(w in t for w in ['very dry', 'desert dry', 'bone dry']):
        return 8.0
    return None


def _extract_wind_speed(text: str) -> float | None:
    t = text.lower()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:m/?s|metres?\s*per\s*second|meters?\s*per\s*second)', t)
    if m:
        return float(m.group(1))
    m = re.search(r'wind\s+(?:speed\s+)?(?:of\s+)?(\d+(?:\.\d+)?)', t)
    if m:
        return float(m.group(1))
    # Keyword-based
    if any(w in t for w in ['very high wind', 'storm', 'gale', 'very windy']):
        return 13.0
    if any(w in t for w in ['high wind', 'strong wind', 'windy']):
        return 10.0
    if any(w in t for w in ['moderate wind', 'average wind', 'some wind']):
        return 7.0
    if any(w in t for w in ['low wind', 'light wind', 'light breeze']):
        return 3.5
    if any(w in t for w in ['no wind', 'calm', 'still air', 'very low wind']):
        return 1.0
    return None


def _extract_solar_irradiance(text: str) -> float | None:
    t = text.lower()
    m = re.search(r'solar\s+(?:irradiance|radiation)\s+(?:of\s+)?(\d+(?:\.\d+)?)', t)
    if m:
        return float(m.group(1))
    # Keyword-based
    if any(w in t for w in ['very sunny', 'extremely sunny', 'very high sun', 'desert sun', 'peak sun']):
        return 90.0
    if any(w in t for w in ['sunny', 'bright sun', 'high sun', 'good sunlight', 'lots of sun']):
        return 75.0
    if any(w in t for w in ['partly cloudy', 'moderate sun', 'average sunlight', 'some sun']):
        return 55.0
    if any(w in t for w in ['cloudy', 'overcast', 'low sun', 'little sun', 'less sun']):
        return 30.0
    if any(w in t for w in ['very cloudy', 'heavy cloud', 'no sun', 'no sunlight']):
        return 10.0
    return None


def _extract_water_availability(text: str) -> float | None:
    t = text.lower()
    if any(w in t for w in ['river', 'waterfall', 'abundant water', 'stream nearby', 'lots of water']):
        return 88.0
    if any(w in t for w in ['stream', 'creek', 'high water', 'good water supply', 'near water']):
        return 70.0
    if any(w in t for w in ['moderate water', 'seasonal stream', 'some water', 'water available']):
        return 45.0
    if any(w in t for w in ['low water', 'scarce water', 'little water', 'dry land']):
        return 18.0
    if any(w in t for w in ['no water', 'desert', 'arid', 'no water source']):
        return 3.0
    return None


def _extract_biomass_availability(text: str) -> float | None:
    t = text.lower()
    if any(w in t for w in ['dense forest', 'thick forest', 'lots of farm waste', 'agricultural waste', 'abundant biomass']):
        return 88.0
    if any(w in t for w in ['forest', 'farmland', 'farm', 'agricultural land', 'crops', 'high biomass']):
        return 70.0
    if any(w in t for w in ['some trees', 'moderate biomass', 'partial forest', 'some farm']):
        return 45.0
    if any(w in t for w in ['low biomass', 'few trees', 'little vegetation', 'sparse']):
        return 18.0
    if any(w in t for w in ['no biomass', 'no trees', 'barren', 'no vegetation']):
        return 3.0
    return None


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION KNOWLEDGE DATABASE
# Each entry: location_type, temperature, humidity, wind_speed,
#             solar_irradiance, water_availability, biomass_availability
# ─────────────────────────────────────────────────────────────────────────────

LOCATION_DB = {
    # ── INDIA ──────────────────────────────────────────────────────────────
    # Coastal cities
    'mumbai':     {'loc': 'coastal',    'temp': 30, 'hum': 80, 'wind': 6,  'irr': 65, 'water': 55, 'bio': 30},
    'mumbai':     {'loc': 'coastal',    'temp': 30, 'hum': 80, 'wind': 6,  'irr': 65, 'water': 55, 'bio': 30},
    'chennai':    {'loc': 'coastal',    'temp': 33, 'hum': 75, 'wind': 6,  'irr': 75, 'water': 45, 'bio': 30},
    'madras':     {'loc': 'coastal',    'temp': 33, 'hum': 75, 'wind': 6,  'irr': 75, 'water': 45, 'bio': 30},
    'kochi':      {'loc': 'coastal',    'temp': 29, 'hum': 85, 'wind': 5,  'irr': 60, 'water': 75, 'bio': 70},
    'cochin':     {'loc': 'coastal',    'temp': 29, 'hum': 85, 'wind': 5,  'irr': 60, 'water': 75, 'bio': 70},
    'trivandrum': {'loc': 'coastal',    'temp': 28, 'hum': 82, 'wind': 5,  'irr': 65, 'water': 70, 'bio': 65},
    'thiruvananthapuram': {'loc': 'coastal', 'temp': 28, 'hum': 82, 'wind': 5, 'irr': 65, 'water': 70, 'bio': 65},
    'visakhapatnam': {'loc': 'coastal', 'temp': 31, 'hum': 73, 'wind': 7,  'irr': 72, 'water': 50, 'bio': 40},
    'vizag':      {'loc': 'coastal',    'temp': 31, 'hum': 73, 'wind': 7,  'irr': 72, 'water': 50, 'bio': 40},
    'goa':        {'loc': 'coastal',    'temp': 29, 'hum': 80, 'wind': 6,  'irr': 68, 'water': 60, 'bio': 55},
    'mangalore':  {'loc': 'coastal',    'temp': 28, 'hum': 80, 'wind': 5,  'irr': 62, 'water': 65, 'bio': 60},
    'puri':       {'loc': 'coastal',    'temp': 30, 'hum': 78, 'wind': 7,  'irr': 68, 'water': 55, 'bio': 45},
    'kolkata':    {'loc': 'coastal',    'temp': 29, 'hum': 78, 'wind': 5,  'irr': 65, 'water': 60, 'bio': 50},
    'calcutta':   {'loc': 'coastal',    'temp': 29, 'hum': 78, 'wind': 5,  'irr': 65, 'water': 60, 'bio': 50},
    'surat':      {'loc': 'coastal',    'temp': 31, 'hum': 70, 'wind': 7,  'irr': 72, 'water': 45, 'bio': 30},
    'dwarka':     {'loc': 'coastal',    'temp': 30, 'hum': 65, 'wind': 9,  'irr': 78, 'water': 40, 'bio': 20},
    'pondicherry':{'loc': 'coastal',    'temp': 29, 'hum': 76, 'wind': 6,  'irr': 73, 'water': 48, 'bio': 35},
    # Desert cities
    'jaisalmer':  {'loc': 'desert',     'temp': 38, 'hum': 12, 'wind': 5,  'irr': 95, 'water': 5,  'bio': 8},
    'jodhpur':    {'loc': 'desert',     'temp': 36, 'hum': 18, 'wind': 5,  'irr': 90, 'water': 8,  'bio': 10},
    'jaipur':     {'loc': 'desert',     'temp': 33, 'hum': 25, 'wind': 5,  'irr': 85, 'water': 15, 'bio': 15},
    'bikaner':    {'loc': 'desert',     'temp': 37, 'hum': 14, 'wind': 5,  'irr': 92, 'water': 5,  'bio': 8},
    'barmer':     {'loc': 'desert',     'temp': 39, 'hum': 10, 'wind': 5,  'irr': 95, 'water': 3,  'bio': 5},
    'kutch':      {'loc': 'desert',     'temp': 35, 'hum': 22, 'wind': 7,  'irr': 88, 'water': 10, 'bio': 12},
    'rajasthan':  {'loc': 'desert',     'temp': 36, 'hum': 16, 'wind': 5,  'irr': 90, 'water': 7,  'bio': 10},
    # Mountain cities
    'shimla':     {'loc': 'mountainous','temp': 8,  'hum': 65, 'wind': 4,  'irr': 55, 'water': 70, 'bio': 65},
    'manali':     {'loc': 'mountainous','temp': 4,  'hum': 60, 'wind': 5,  'irr': 58, 'water': 82, 'bio': 55},
    'mussoorie':  {'loc': 'mountainous','temp': 10, 'hum': 68, 'wind': 4,  'irr': 52, 'water': 72, 'bio': 68},
    'nainital':   {'loc': 'mountainous','temp': 11, 'hum': 70, 'wind': 4,  'irr': 55, 'water': 75, 'bio': 70},
    'darjeeling': {'loc': 'mountainous','temp': 12, 'hum': 78, 'wind': 5,  'irr': 50, 'water': 80, 'bio': 72},
    'dehradun':   {'loc': 'mountainous','temp': 18, 'hum': 62, 'wind': 3,  'irr': 60, 'water': 68, 'bio': 65},
    'srinagar':   {'loc': 'mountainous','temp': 6,  'hum': 55, 'wind': 4,  'irr': 58, 'water': 75, 'bio': 55},
    'leh':        {'loc': 'mountainous','temp': 2,  'hum': 30, 'wind': 3,  'irr': 75, 'water': 55, 'bio': 20},
    'gangtok':    {'loc': 'mountainous','temp': 12, 'hum': 80, 'wind': 4,  'irr': 50, 'water': 85, 'bio': 75},
    'ooty':       {'loc': 'mountainous','temp': 14, 'hum': 70, 'wind': 4,  'irr': 58, 'water': 72, 'bio': 68},
    'coorg':      {'loc': 'mountainous','temp': 18, 'hum': 78, 'wind': 3,  'irr': 58, 'water': 80, 'bio': 80},
    'kodagu':     {'loc': 'mountainous','temp': 18, 'hum': 78, 'wind': 3,  'irr': 58, 'water': 80, 'bio': 80},
    'munnar':     {'loc': 'mountainous','temp': 15, 'hum': 80, 'wind': 4,  'irr': 55, 'water': 85, 'bio': 78},
    'arunachal':  {'loc': 'mountainous','temp': 14, 'hum': 82, 'wind': 4,  'irr': 52, 'water': 88, 'bio': 85},
    # Forest / Rural / Agricultural
    'assam':      {'loc': 'forest',     'temp': 25, 'hum': 85, 'wind': 3,  'irr': 55, 'water': 88, 'bio': 88},
    'meghalaya':  {'loc': 'forest',     'temp': 18, 'hum': 88, 'wind': 3,  'irr': 48, 'water': 90, 'bio': 88},
    'shillong':   {'loc': 'forest',     'temp': 16, 'hum': 82, 'wind': 3,  'irr': 50, 'water': 85, 'bio': 82},
    'kerala':     {'loc': 'forest',     'temp': 28, 'hum': 84, 'wind': 4,  'irr': 62, 'water': 82, 'bio': 80},
    'wayanad':    {'loc': 'forest',     'temp': 22, 'hum': 85, 'wind': 3,  'irr': 58, 'water': 85, 'bio': 88},
    'sundarbans': {'loc': 'forest',     'temp': 28, 'hum': 88, 'wind': 5,  'irr': 58, 'water': 90, 'bio': 88},
    'punjab':     {'loc': 'rural',      'temp': 25, 'hum': 55, 'wind': 5,  'irr': 72, 'water': 55, 'bio': 60},
    'haryana':    {'loc': 'rural',      'temp': 27, 'hum': 50, 'wind': 5,  'irr': 74, 'water': 48, 'bio': 55},
    'madhya pradesh': {'loc': 'rural',  'temp': 28, 'hum': 55, 'wind': 4,  'irr': 72, 'water': 50, 'bio': 55},
    'bhopal':     {'loc': 'rural',      'temp': 28, 'hum': 55, 'wind': 4,  'irr': 72, 'water': 48, 'bio': 50},
    'nagpur':     {'loc': 'rural',      'temp': 32, 'hum': 48, 'wind': 4,  'irr': 75, 'water': 42, 'bio': 45},
    'nashik':     {'loc': 'rural',      'temp': 26, 'hum': 55, 'wind': 4,  'irr': 70, 'water': 50, 'bio': 50},
    # Urban metros
    'delhi':      {'loc': 'urban',      'temp': 27, 'hum': 45, 'wind': 4,  'irr': 72, 'water': 30, 'bio': 15},
    'new delhi':  {'loc': 'urban',      'temp': 27, 'hum': 45, 'wind': 4,  'irr': 72, 'water': 30, 'bio': 15},
    'bangalore':  {'loc': 'urban',      'temp': 24, 'hum': 55, 'wind': 3,  'irr': 68, 'water': 35, 'bio': 20},
    'bengaluru':  {'loc': 'urban',      'temp': 24, 'hum': 55, 'wind': 3,  'irr': 68, 'water': 35, 'bio': 20},
    'hyderabad':  {'loc': 'urban',      'temp': 28, 'hum': 52, 'wind': 4,  'irr': 74, 'water': 35, 'bio': 20},
    'pune':       {'loc': 'urban',      'temp': 26, 'hum': 55, 'wind': 4,  'irr': 70, 'water': 35, 'bio': 25},
    'ahmedabad':  {'loc': 'urban',      'temp': 31, 'hum': 45, 'wind': 6,  'irr': 80, 'water': 25, 'bio': 15},
    'lucknow':    {'loc': 'urban',      'temp': 27, 'hum': 58, 'wind': 4,  'irr': 68, 'water': 40, 'bio': 25},
    'indore':     {'loc': 'urban',      'temp': 27, 'hum': 52, 'wind': 4,  'irr': 72, 'water': 35, 'bio': 25},
    'chandigarh': {'loc': 'urban',      'temp': 23, 'hum': 60, 'wind': 4,  'irr': 68, 'water': 42, 'bio': 28},
    'amritsar':   {'loc': 'rural',      'temp': 24, 'hum': 58, 'wind': 4,  'irr': 70, 'water': 48, 'bio': 55},
    # ── GLOBAL ─────────────────────────────────────────────────────────────
    'london':     {'loc': 'urban',      'temp': 11, 'hum': 75, 'wind': 8,  'irr': 35, 'water': 65, 'bio': 20},
    'new york':   {'loc': 'urban',      'temp': 13, 'hum': 62, 'wind': 9,  'irr': 55, 'water': 50, 'bio': 15},
    'tokyo':      {'loc': 'urban',      'temp': 16, 'hum': 65, 'wind': 6,  'irr': 60, 'water': 55, 'bio': 25},
    'dubai':      {'loc': 'desert',     'temp': 33, 'hum': 55, 'wind': 6,  'irr': 92, 'water': 10, 'bio': 5},
    'sydney':     {'loc': 'coastal',    'temp': 19, 'hum': 68, 'wind': 8,  'irr': 78, 'water': 55, 'bio': 35},
    'berlin':     {'loc': 'urban',      'temp': 10, 'hum': 70, 'wind': 7,  'irr': 45, 'water': 60, 'bio': 30},
    'patna':      {'loc': 'rural',      'temp': 27, 'hum': 65, 'wind': 4,  'irr': 65, 'water': 55, 'bio': 45},
    'bhubaneswar':{'loc': 'rural',      'temp': 30, 'hum': 72, 'wind': 5,  'irr': 68, 'water': 58, 'bio': 50},
    # ── INTERNATIONAL ──────────────────────────────────────────────────────
    # Middle East / Arabian Peninsula
    'abu dhabi':  {'loc': 'desert',     'temp': 37, 'hum': 52, 'wind': 5,  'irr': 93, 'water': 3,  'bio': 5},
    'riyadh':     {'loc': 'desert',     'temp': 38, 'hum': 15, 'wind': 4,  'irr': 94, 'water': 2,  'bio': 5},
    'jeddah':     {'loc': 'coastal',    'temp': 35, 'hum': 55, 'wind': 5,  'irr': 90, 'water': 15, 'bio': 8},
    'muscat':     {'loc': 'coastal',    'temp': 36, 'hum': 50, 'wind': 5,  'irr': 90, 'water': 8,  'bio': 5},
    'doha':       {'loc': 'coastal',    'temp': 36, 'hum': 58, 'wind': 5,  'irr': 90, 'water': 5,  'bio': 5},
    'kuwait':     {'loc': 'desert',     'temp': 38, 'hum': 30, 'wind': 5,  'irr': 90, 'water': 3,  'bio': 5},
    # Europe
    'london':     {'loc': 'urban',      'temp': 12, 'hum': 78, 'wind': 7,  'irr': 30, 'water': 40, 'bio': 35},
    'uk':         {'loc': 'rural',      'temp': 10, 'hum': 80, 'wind': 8,  'irr': 28, 'water': 45, 'bio': 40},
    'england':    {'loc': 'rural',      'temp': 10, 'hum': 80, 'wind': 8,  'irr': 28, 'water': 45, 'bio': 40},
    'scotland':   {'loc': 'mountainous','temp': 7,  'hum': 82, 'wind': 10, 'irr': 22, 'water': 78, 'bio': 65},
    'ireland':    {'loc': 'rural',      'temp': 9,  'hum': 82, 'wind': 9,  'irr': 25, 'water': 58, 'bio': 55},
    'paris':      {'loc': 'urban',      'temp': 14, 'hum': 72, 'wind': 5,  'irr': 45, 'water': 38, 'bio': 28},
    'france':     {'loc': 'rural',      'temp': 15, 'hum': 68, 'wind': 5,  'irr': 48, 'water': 45, 'bio': 45},
    'germany':    {'loc': 'rural',      'temp': 10, 'hum': 72, 'wind': 6,  'irr': 38, 'water': 48, 'bio': 40},
    'berlin':     {'loc': 'urban',      'temp': 10, 'hum': 70, 'wind': 6,  'irr': 38, 'water': 40, 'bio': 25},
    'amsterdam':  {'loc': 'urban',      'temp': 10, 'hum': 80, 'wind': 8,  'irr': 32, 'water': 45, 'bio': 30},
    'netherlands':{'loc': 'coastal',    'temp': 10, 'hum': 80, 'wind': 9,  'irr': 32, 'water': 50, 'bio': 32},
    'denmark':    {'loc': 'coastal',    'temp': 8,  'hum': 80, 'wind': 10, 'irr': 28, 'water': 52, 'bio': 35},
    'norway':     {'loc': 'mountainous','temp': 2,  'hum': 72, 'wind': 8,  'irr': 25, 'water': 85, 'bio': 60},
    'sweden':     {'loc': 'forest',     'temp': 5,  'hum': 72, 'wind': 7,  'irr': 28, 'water': 75, 'bio': 80},
    'finland':    {'loc': 'forest',     'temp': 2,  'hum': 72, 'wind': 6,  'irr': 25, 'water': 80, 'bio': 82},
    'spain':      {'loc': 'rural',      'temp': 18, 'hum': 50, 'wind': 6,  'irr': 70, 'water': 35, 'bio': 30},
    'madrid':     {'loc': 'urban',      'temp': 17, 'hum': 45, 'wind': 5,  'irr': 70, 'water': 25, 'bio': 15},
    'barcelona':  {'loc': 'coastal',    'temp': 19, 'hum': 60, 'wind': 6,  'irr': 72, 'water': 35, 'bio': 25},
    'italy':      {'loc': 'rural',      'temp': 17, 'hum': 62, 'wind': 5,  'irr': 65, 'water': 45, 'bio': 40},
    'rome':       {'loc': 'urban',      'temp': 17, 'hum': 60, 'wind': 4,  'irr': 65, 'water': 30, 'bio': 20},
    # Americas
    'new york':   {'loc': 'urban',      'temp': 13, 'hum': 62, 'wind': 6,  'irr': 50, 'water': 35, 'bio': 20},
    'usa':        {'loc': 'rural',      'temp': 15, 'hum': 60, 'wind': 6,  'irr': 55, 'water': 45, 'bio': 45},
    'california': {'loc': 'coastal',    'temp': 18, 'hum': 55, 'wind': 5,  'irr': 78, 'water': 30, 'bio': 30},
    'texas':      {'loc': 'rural',      'temp': 23, 'hum': 52, 'wind': 7,  'irr': 78, 'water': 35, 'bio': 35},
    'arizona':    {'loc': 'desert',     'temp': 32, 'hum': 20, 'wind': 5,  'irr': 92, 'water': 8,  'bio': 10},
    'nevada':     {'loc': 'desert',     'temp': 30, 'hum': 18, 'wind': 5,  'irr': 90, 'water': 5,  'bio': 8},
    'florida':    {'loc': 'coastal',    'temp': 26, 'hum': 74, 'wind': 7,  'irr': 72, 'water': 55, 'bio': 45},
    'seattle':    {'loc': 'coastal',    'temp': 11, 'hum': 80, 'wind': 6,  'irr': 32, 'water': 60, 'bio': 70},
    'chicago':    {'loc': 'urban',      'temp': 11, 'hum': 65, 'wind': 8,  'irr': 48, 'water': 40, 'bio': 20},
    'amazon':     {'loc': 'forest',     'temp': 27, 'hum': 90, 'wind': 2,  'irr': 58, 'water': 95, 'bio': 98},
    'brazil':     {'loc': 'forest',     'temp': 26, 'hum': 80, 'wind': 3,  'irr': 65, 'water': 80, 'bio': 85},
    'canada':     {'loc': 'forest',     'temp': 4,  'hum': 65, 'wind': 7,  'irr': 35, 'water': 75, 'bio': 78},
    # Asia Pacific
    'beijing':    {'loc': 'urban',      'temp': 13, 'hum': 45, 'wind': 5,  'irr': 58, 'water': 25, 'bio': 15},
    'shanghai':   {'loc': 'coastal',    'temp': 17, 'hum': 72, 'wind': 5,  'irr': 55, 'water': 48, 'bio': 30},
    'china':      {'loc': 'rural',      'temp': 15, 'hum': 60, 'wind': 5,  'irr': 60, 'water': 50, 'bio': 45},
    'tokyo':      {'loc': 'urban',      'temp': 16, 'hum': 68, 'wind': 5,  'irr': 50, 'water': 45, 'bio': 20},
    'japan':      {'loc': 'mountainous','temp': 13, 'hum': 70, 'wind': 5,  'irr': 50, 'water': 68, 'bio': 55},
    'singapore':  {'loc': 'coastal',    'temp': 30, 'hum': 84, 'wind': 3,  'irr': 60, 'water': 55, 'bio': 40},
    'malaysia':   {'loc': 'forest',     'temp': 28, 'hum': 85, 'wind': 3,  'irr': 62, 'water': 78, 'bio': 82},
    'indonesia':  {'loc': 'forest',     'temp': 27, 'hum': 82, 'wind': 3,  'irr': 62, 'water': 80, 'bio': 85},
    'philippines':{'loc': 'coastal',    'temp': 28, 'hum': 80, 'wind': 6,  'irr': 65, 'water': 65, 'bio': 65},
    'thailand':   {'loc': 'rural',      'temp': 28, 'hum': 75, 'wind': 4,  'irr': 68, 'water': 65, 'bio': 65},
    'bangkok':    {'loc': 'urban',      'temp': 29, 'hum': 74, 'wind': 3,  'irr': 68, 'water': 45, 'bio': 20},
    'vietnam':    {'loc': 'coastal',    'temp': 26, 'hum': 78, 'wind': 5,  'irr': 62, 'water': 70, 'bio': 65},
    'pakistan':   {'loc': 'rural',      'temp': 27, 'hum': 42, 'wind': 5,  'irr': 78, 'water': 38, 'bio': 30},
    'lahore':     {'loc': 'urban',      'temp': 27, 'hum': 48, 'wind': 4,  'irr': 75, 'water': 32, 'bio': 20},
    'karachi':    {'loc': 'coastal',    'temp': 30, 'hum': 65, 'wind': 6,  'irr': 78, 'water': 15, 'bio': 10},
    'bangladesh': {'loc': 'rural',      'temp': 27, 'hum': 82, 'wind': 5,  'irr': 62, 'water': 80, 'bio': 65},
    'nepal':      {'loc': 'mountainous','temp': 10, 'hum': 68, 'wind': 4,  'irr': 58, 'water': 75, 'bio': 65},
    'kathmandu':  {'loc': 'mountainous','temp': 15, 'hum': 65, 'wind': 3,  'irr': 60, 'water': 68, 'bio': 55},
    'sri lanka':  {'loc': 'coastal',    'temp': 28, 'hum': 80, 'wind': 6,  'irr': 66, 'water': 65, 'bio': 65},
    'colombo':    {'loc': 'coastal',    'temp': 29, 'hum': 80, 'wind': 5,  'irr': 65, 'water': 60, 'bio': 55},
    # Africa
    'nigeria':    {'loc': 'forest',     'temp': 28, 'hum': 78, 'wind': 3,  'irr': 68, 'water': 65, 'bio': 72},
    'kenya':      {'loc': 'rural',      'temp': 22, 'hum': 58, 'wind': 5,  'irr': 75, 'water': 48, 'bio': 50},
    'nairobi':    {'loc': 'urban',      'temp': 19, 'hum': 60, 'wind': 4,  'irr': 72, 'water': 35, 'bio': 25},
    'egypt':      {'loc': 'desert',     'temp': 30, 'hum': 35, 'wind': 5,  'irr': 92, 'water': 5,  'bio': 5},
    'cairo':      {'loc': 'urban',      'temp': 28, 'hum': 38, 'wind': 4,  'irr': 90, 'water': 8,  'bio': 5},
    'sahara':     {'loc': 'desert',     'temp': 38, 'hum': 8,  'wind': 4,  'irr': 97, 'water': 1,  'bio': 2},
    'south africa':{'loc': 'rural',     'temp': 18, 'hum': 52, 'wind': 6,  'irr': 72, 'water': 38, 'bio': 38},
    'australia':  {'loc': 'rural',      'temp': 22, 'hum': 48, 'wind': 6,  'irr': 80, 'water': 30, 'bio': 35},
    'sydney':     {'loc': 'coastal',    'temp': 19, 'hum': 65, 'wind': 7,  'irr': 70, 'water': 42, 'bio': 35},
    'outback':    {'loc': 'desert',     'temp': 32, 'hum': 18, 'wind': 5,  'irr': 90, 'water': 5,  'bio': 8},
}


def _lookup_location(text: str) -> dict:
    """
    Scan the text for any known location name and return its environmental profile.
    Returns a dict with keys: loc, temp, hum, wind, irr, water, bio
    or an empty dict if no match found.
    """
    t = text.lower()
    # Sort keys longest-first so "new delhi" matches before "delhi"
    for name in sorted(LOCATION_DB.keys(), key=len, reverse=True):
        # Match as whole word to avoid false positives
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, t):
            return dict(LOCATION_DB[name])
    return {}


def _extract_location_type(text: str) -> str:
    """Extract location type from explicit keywords, then from known city names."""
    t = text.lower()
    # Explicit geographic keywords take priority
    if any(w in t for w in ['coastal', 'coast', 'seaside', 'shore', 'beach', 'ocean', 'sea', 'bay', 'gulf', 'island', 'estuary', 'marine']):
        return 'coastal'
    if any(w in t for w in ['mountain', 'hill', 'highland', 'elevated', 'hilly', 'mountainous', 'hillside', 'valley', 'peak', 'ridge', 'altitude']):
        return 'mountainous'
    if any(w in t for w in ['desert', 'arid land', 'dry land', 'barren land', 'sahara', 'thar', 'hot dry']):
        return 'desert'
    if any(w in t for w in ['forest', 'jungle', 'woodland', 'agri', 'agricultural', 'plantation', 'orchard', 'grove', 'trees']):
        return 'forest'
    if any(w in t for w in ['rural', 'village', 'countryside', 'farmland', 'farm', 'outskirts', 'nature']):
        return 'rural'
    if any(w in t for w in ['urban', 'city', 'town', 'suburb', 'metro', 'rooftop', 'apartment', 'building', 'residential']):
        return 'urban'
    # Fall back to location DB
    loc_data = _lookup_location(text)
    if loc_data:
        return loc_data.get('loc', 'rural')
    return 'rural'


def _extract_currency_symbol(text: str) -> str:
    if '₹' in text or 'inr' in text.lower() or 'rupee' in text.lower():
        return '₹'
    if '€' in text:
        return '€'
    if '£' in text:
        return '£'
    if '¥' in text:
        return '¥'
    if '$' in text:
        return '$'
    return '₹'  # default to INR


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATIONAL RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

# Strong single-signal keywords that alone are enough to trigger analysis
STRONG_ENERGY_KEYWORDS = [
    'budget', 'lakh', 'crore', '₹', 'inr', 'invest', 'afford',
    'solar', 'wind energy', 'wind power', 'hydro', 'geothermal', 'tidal', 'biomass',
    'renewable', 'energy source', 'irradiance', 'solar panel', 'turbine',
    'coastal', 'desert', 'mountainous', 'rural area', 'urban area',
    'temperature is', 'humidity is', 'wind speed', 'm/s', '°c', 'celsius'
]

# Supporting keywords — need 2+ to trigger analysis
SUPPORTING_ENERGY_KEYWORDS = [
    'sun', 'sunny', 'wind', 'water', 'rain', 'farm', 'forest', 'roof', 'arid',
    'hot', 'cold', 'warm', 'cool', 'dry', 'humid', 'wet', 'cloudy',
    'energy', 'power', 'electricity', 'climate', 'weather',
    'location', 'region', 'area', 'place', 'city', 'village', 'mountain', 'coast',
    'install', 'setup', 'system', 'panel', 'generator'
]

GREETINGS     = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'howdy', 'greetings', 'what is up', 'sup', 'assalamualaikum', 'namaste']
THANKS        = ['thank you', 'thanks', 'appreciate', 'cheers', 'great', 'awesome', 'nice', 'helpful']
HOW_ARE_YOU   = ['how are you', 'how do you do', 'how are things', 'hows it going', 'how are u']
WHO_ARE_YOU   = ['what are you', 'who are you', 'what is your name', 'your name', 'tell me about yourself', 'identify']
CAPABILITIES  = ['what can you do', 'how do you work', 'what do you know', 'features', 'capabilities', 'how does this work', 'help me']
EXAMPLES      = ['example', 'show me', 'demo', 'sample', 'give me an example', 'case study']
GOODBYE       = ['bye', 'goodbye', 'see you', 'take care', 'adios', 'exit', 'quit']
ECO_TIPS      = ['tip', 'eco tip', 'sustainability', 'green energy', 'clean energy', 'environment', 'save earth', 'advise']


def _is_energy_query(text: str, nlp_data: dict = None) -> bool:
    """Return True only if the message has a clear energy/environmental intent."""
    
    # If analysis already confirmed it's an energy query, trust it
    if nlp_data and nlp_data.get('is_energy_query') is True:
        return True

    tl = text.lower()

    # A strong keyword alone is enough
    if any(kw in tl for kw in STRONG_ENERGY_KEYWORDS):
        return True

    # Check for "how much", "what is the best", "describe", "recommend" combined with supporting
    if any(w in tl for w in ['recommend', 'best', 'suit', 'work', 'calculate', 'analyse', 'setup']) and any(kw in tl for kw in SUPPORTING_ENERGY_KEYWORDS):
        return True

    # Check if a known location from DB is mentioned — location + 1 supporting = enough
    has_location = bool(_lookup_location(text))
    supporting_matches = sum(1 for kw in SUPPORTING_ENERGY_KEYWORDS if kw in tl)

    if has_location and supporting_matches >= 1:
        return True

    # Without a location, require at least 2 supporting signals
    if supporting_matches >= 2:
        return True

    return False


def _generate_conversational_reply(text: str) -> dict | None:
    tl = text.lower().strip()

    if any(tl.startswith(g) or tl == g for g in GREETINGS):
        return {"reply": "Hello! I'm **Eco-AI**, your premium renewable energy advisor. I can help you find the best clean energy source for your home or business based on your location and budget. How can I assist you today?"}

    if any(t in tl for t in THANKS) and len(tl) < 30:
        return {"reply": "You're very welcome! I'm glad I could help. Do you have any more questions about renewable energy or environmental conditions?"}

    if any(h in tl for h in HOW_ARE_YOU):
        return {"reply": "I'm functioning perfectly and ready for some environmental data! Is there a specific location or budget you'd like me to analyze for energy potential?"}

    if any(w in tl for w in WHO_ARE_YOU):
        return {"reply": "I'm **Eco-AI** — a fuzzy logic-powered renewable energy advisor. I evaluate Solar, Wind, Hydro, Biomass, Geothermal, and Tidal energy for your specific conditions and rank them by suitability!"}

    if any(c in tl for c in CAPABILITIES):
        return {"reply": "I analyse 8 environmental factors to rank renewable energy sources:\n\nTemperature, Humidity, Budget, Wind Speed, Solar Irradiance, Water Availability, Biomass, Location Type\n\nTry: *\"Coastal area, 10 m/s wind, ₹8 lakh budget, humid\"*"}

    if any(e in tl for e in EXAMPLES):
        return {"reply": "Here are some example queries you can try:\n\n• *\"Coastal area, windy, ₹5 lakh budget, temperature 28°C, humidity 75%\"*\n• *\"Rural farm with forest nearby, ₹2 lakh, moderate sun\"*\n• *\"Mountain location, river nearby, ₹10 lakh budget\"*\n• *\"Desert area, very sunny, ₹3 lakh\"*"}

    return None


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _format_inputs_summary(inputs: dict, currency: str) -> str:
    loc   = inputs.get('location_type', 'rural').capitalize()
    bud   = inputs.get('budget', 0)
    temp  = inputs.get('temperature', 0)
    hum   = inputs.get('humidity', 0)
    wind  = inputs.get('wind_speed', 0)
    irr   = inputs.get('solar_irradiance', 0)
    water = inputs.get('water_availability', 0)
    bio   = inputs.get('biomass_availability', 0)

    # Format budget in lakhs if INR
    if currency == '₹':
        if bud >= 100000:
            bud_str = f"₹{bud/100000:.1f}L"
        else:
            bud_str = f"₹{int(bud):,}"
    else:
        bud_str = f"{currency}{int(bud):,}"

    return (
        f"Location: {loc} | Budget: {bud_str} | Temp: {temp:.0f}°C | "
        f"Humidity: {hum:.0f}% RH | Wind: {wind:.1f} m/s | "
        f"Solar Irradiance: {irr:.0f}/100 | Water: {water:.0f}/100 | Biomass: {bio:.0f}/100"
    )


def _apply_currency(details: dict, currency: str) -> dict:
    if currency != '₹':
        # Convert estimated cost display from ₹ to requested currency
        conversion = {'$': 0.012, '€': 0.011, '£': 0.0095, '¥': 1.78}
        rate = conversion.get(currency, 0.012)
        cost = details.get('estimated_cost', '')
        # Replace ₹ amounts with converted values (rough)
        def convert_match(m):
            num_str = m.group(1).replace(',', '')
            mult = 1000 if 'L' in num_str else 1
            try:
                val = float(num_str.replace('L', '').replace('l', '')) * mult * rate
                return f"{currency}{val:,.0f}"
            except Exception:
                return m.group(0)
        details = dict(details)
        details['estimated_cost'] = re.sub(r'₹([\d,L]+)', convert_match, cost)
    return details


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CHAT HANDLER
# ─────────────────────────────────────────────────────────────────────────────

def generate_chat_response(input_data: str | dict) -> dict:
    # 1. Normalize input
    if isinstance(input_data, str):
        try:
            # Try to see if it's a JSON string from the server
            data = json.loads(input_data)
            user_message = data.get('message', input_data)
            nlp_data = data
        except:
            user_message = input_data
            nlp_data = {}
    else:
        user_message = input_data.get('message', '')
        nlp_data = input_data

    # NEW: Proactive Local Extraction
    local_budget = _extract_budget(user_message)
    local_loc_defaults = _lookup_location(user_message)

    # 2. Extract Location Type
    location_type = nlp_data.get('location_type') or _extract_location_type(user_message)

    # 3. Decision: Conversational vs. Prediction
    # We provide a result if:
    # - If we match our local energy keywords
    # - OR we found a clear budget/location in the message
    is_prediction = _is_energy_query(user_message, nlp_data) or local_budget or local_loc_defaults

    if not is_prediction:
        conv = _generate_conversational_reply(user_message)
        if conv:
            return conv

    # 4. Extract parameters (Hierarchy: JSON > Local Regex > DB Defaults)
    budget = nlp_data.get('budget') or local_budget

    temperature = nlp_data.get('temperature')
    if temperature is None:
        temperature = _extract_temperature(user_message) or (local_loc_defaults.get('temp') if local_loc_defaults else None)

    humidity = nlp_data.get('humidity')
    if humidity is None:
        humidity = _extract_humidity(user_message) or (local_loc_defaults.get('hum') if local_loc_defaults else None)

    wind_speed = nlp_data.get('wind_speed')
    if wind_speed is None:
        wind_speed = _extract_wind_speed(user_message) or (local_loc_defaults.get('wind') if local_loc_defaults else None)

    solar_irradiance = nlp_data.get('solar_irradiance')
    if solar_irradiance is None:
        solar_irradiance = _extract_solar_irradiance(user_message) or (local_loc_defaults.get('irr') if local_loc_defaults else None)

    water_availability = nlp_data.get('water_availability')
    if water_availability is None:
        water_availability = _extract_water_availability(user_message) or (local_loc_defaults.get('water') if local_loc_defaults else None)

    biomass_availability = nlp_data.get('biomass_availability')
    if biomass_availability is None:
        biomass_availability = _extract_biomass_availability(user_message) or (local_loc_defaults.get('bio') if local_loc_defaults else None)

    location_type = nlp_data.get('location_type')
    if not location_type:
        location_type = _extract_location_type(user_message)

    currency = _extract_currency_symbol(user_message)

    # 5. Run fuzzy prediction
    try:
        result = predict_renewable_energy(
            description_text       = user_message,
            user_budget               = budget,
            user_temp                 = temperature,
            user_hum                  = humidity,
            user_wind_speed           = wind_speed,
            user_solar_irradiance     = solar_irradiance,
            user_water_availability   = water_availability,
            user_biomass_availability = biomass_availability,
            user_location_type        = location_type
        )
    except Exception as e:
        return {"reply": f"I encountered an error during analysis: {str(e)}"}

    # 4. Apply currency to details
    best_details        = _apply_currency(result['best']['details'],        currency)
    second_best_details = _apply_currency(result['second_best']['details'], currency)
    hybrid_details      = _apply_currency(result['hybrid']['details'],      currency)

    inputs_summary = _format_inputs_summary(result['inputs_used'], currency)

    return {
        "is_result": True,
        "prediction_data": {
            "inputs_summary":  inputs_summary,
            "all_scores":      result['all_scores'],

            "best": {
                "type":        result['best']['type'],
                "confidence":  result['best']['confidence'],
                "name":        best_details.get('name_of_instrument', result['best']['type']),
                "sub_type":    best_details.get('sub_type', ''),
                "advantage":   best_details.get('advantage', ''),
                "estimated_cost": best_details.get('estimated_cost', ''),
                "payback_duration": best_details.get('payback_duration', ''),
                "area_required":    best_details.get('area_required', ''),
                "installation_location": best_details.get('installation_location', ''),
                "environmental_impact":  best_details.get('environmental_impact', ''),
                "roi":         best_details.get('roi', ''),
                "precaution":  best_details.get('precaution', ''),
                "care":        best_details.get('care', ''),
                "installation_guide": best_details.get('installation_guide', ''),
                "safety_plan":   best_details.get('safety_plan', ''),
                "detailed_impact": best_details.get('detailed_impact', ''),
                "financial_roi":  best_details.get('financial_roi', ''),
                "government_subsidy": best_details.get('government_subsidy', ''),
                "government_subsidy_detailed": best_details.get('government_subsidy_detailed', '')
            },

            "second_best": {
                "type":        result['second_best']['type'],
                "confidence":  result['second_best']['confidence'],
                "name":        second_best_details.get('name_of_instrument', result['second_best']['type']),
                "sub_type":    second_best_details.get('sub_type', ''),
                "advantage":   second_best_details.get('advantage', ''),
                "estimated_cost": second_best_details.get('estimated_cost', ''),
                "payback_duration": second_best_details.get('payback_duration', '')
            },

            "hybrid": {
                "type":   result['hybrid']['type'],
                "emoji":  hybrid_details.get('emoji', '⚡'),
                "name":   hybrid_details.get('name_of_instrument', result['hybrid']['type']),
                "estimated_cost": hybrid_details.get('estimated_cost', ''),
                "advantage":      hybrid_details.get('advantage', '')
            }
        },
        "temperature": temperature
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing message argument"}, ensure_ascii=True))
        sys.exit(1)

    input_arg = sys.argv[1]
    try:
        response = generate_chat_response(input_arg)
        # ensure_ascii=True makes all unicode safe for Windows cmd pipes
        print(json.dumps(response, ensure_ascii=True))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=True))
        sys.exit(1)


if __name__ == "__main__":
    main()
