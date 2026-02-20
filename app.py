"""
AgSaathi — Smart Farming Assistant
Student: zene sophie anand  | Wacp no: 1000414
Assessment: FA-2 | Course: Generative AI | School: Aspee Nutan Academy
"""

import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AgSaathi — Smart Farming Assistant", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# ── GEMINI SETUP ────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3-flash-preview" 
MODEL_TEMPERATURE = 0.3

@st.cache_resource
def get_model():
    return genai.GenerativeModel(model_name=MODEL_NAME, generation_config=genai.GenerationConfig(temperature=MODEL_TEMPERATURE))

# ── GEO DATA ────────────────────────────────────────────────────────────────
GEO = {
    'India 🇮🇳': {'languages': ['English', 'Hindi'], 'states': ['Uttar Pradesh', 'Punjab', 'Bihar', 'Madhya Pradesh', 'Maharashtra', 'Gujarat']},
    'Canada 🇨🇦': {'languages': ['English', 'French'], 'states': ['Ontario', 'Quebec', 'Saskatchewan', 'Alberta']},
    'Ghana 🇬🇭': {'languages': ['English'], 'states': ['Ashanti', 'Northern', 'Greater Accra', 'Volta']},
}

# ── SESSION STATE ───────────────────────────────────────────────────────────
DEFAULTS = {'page': 'hero', 'country': None, 'state': None, 'language': 'Hindi', 'nav': 'home', 'stats': {'queries': 0}, 'onboarding_complete': False}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ── AI HELPER ───────────────────────────────────────────────────────────────
def call_ai(prompt: str) -> Optional[Dict]:
    try:
        resp = get_model().generate_content(prompt).text
        text = re.sub(r'```json|```', '', resp).strip()
        start, end = text.find('{'), text.rfind('}') + 1
        if start != -1:
            st.session_state.stats['queries'] += 1
            return json.loads(text[start:end])
    except Exception as e:
        st.error(f"⚠️ AI Parsing Error. Please try again.")
    return None

def render_confidence_bar(score: int):
    color = "#27AE60" if score >= 80 else "#E67E22" if score >= 50 else "#C0392B"
    st.markdown(f"""
    <div style='margin-top:15px;'>
        <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:5px; color:var(--wheat);'>
            <span>AI Confidence Score</span><span>{score}%</span>
        </div>
        <div style='width:100%; background:rgba(255,255,255,0.1); border-radius:5px; height:8px;'>
            <div style='width:{score}%; background:{color}; height:100%; border-radius:5px; transition:1s;'></div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── CSS ─────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Nunito+Sans:wght@300;400;600;700&display=swap');
    :root { --soil: #1A0F07; --wheat: #E8C97A; --cream: #FDF6E3; --sage: #4A7C59; }
    [data-testid="stSidebarNav"] + div { display: none !important; }
    button[title="Collapse sidebar"] { color: var(--wheat) !important; }
    html, body, [data-testid="stAppViewContainer"] { background: #121212 !important; color: var(--cream) !important; font-family: 'Nunito Sans', sans-serif;}
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--wheat) !important; }
    
    .hero-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; min-height: 50vh; margin-top: 5vh; }
    .hero-title { font-family: 'Playfair Display', serif !important; font-size: 4.5rem !important; color: var(--wheat) !important; margin: 0 !important; }
    
    .card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; margin-bottom: 15px; }
    .feature-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; text-align: center; transition: 0.3s; height: 100%; }
    .feature-card:hover { border-color: var(--wheat); transform: translateY(-5px); background: rgba(232,201,122,0.05); }
    
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 5px; }
    .risk-LOW { background: #27AE60; color: #fff; } .risk-MEDIUM { background: #E67E22; color: #fff; } .risk-HIGH { background: #C0392B; color: #fff; }
    
    .stButton>button { background: transparent !important; border: 2px solid var(--wheat) !important; color: var(--wheat) !important; border-radius: 50px !important; font-weight: 700 !important; transition: 0.3s; }
    .stButton>button:hover { background: var(--wheat) !important; color: var(--soil) !important; box-shadow: 0 0 15px rgba(232,201,122,0.3); }
    </style>
    """, unsafe_allow_html=True)

# ── ONBOARDING PAGES ────────────────────────────────────────────────────────
def page_hero():
    st.markdown("<div class='hero-container'><div style='font-size:6rem;'>🌿</div><h1 class='hero-title'>AgSaathi</h1><p style='font-size:1.4rem; opacity:0.7;'>Your Intelligent Agricultural Companion</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 GET STARTED", use_container_width=True):
            st.session_state.page = 'country'; st.rerun()

def page_country():
    st.markdown("<h1 style='text-align:center; padding-top:50px;'>Where is your farm?</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, c in enumerate(['India 🇮🇳', 'Canada 🇨🇦', 'Ghana 🇬🇭']):
        with cols[i]:
            if st.button(c, use_container_width=True):
                st.session_state.country, st.session_state.page = c, 'state'; st.rerun()

def page_state():
    st.markdown(f"<h1 style='text-align:center; padding-top:50px;'>Region in {st.session_state.country}</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sel = st.selectbox("Search State/Province", options=GEO[st.session_state.country]['states'], index=None)
        if st.button("CONFIRM LOCATION", disabled=not sel, use_container_width=True):
            st.session_state.state, st.session_state.page = sel, 'language'; st.rerun()

def page_language():
    st.markdown("<h1 style='text-align:center; padding-top:50px;'>Preferred Language</h1>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])
    for i, lang in enumerate(GEO[st.session_state.country]['languages']):
        with cols[i % 3]:
            if st.button(lang, use_container_width=True):
                st.session_state.update({'language': lang, 'onboarding_complete': True, 'nav': 'home'}); st.rerun()

def sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:var(--wheat); margin-bottom:0;'>🌿 AgSaathi</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; opacity:0.6;'>📍 {st.session_state.state} | 🌐 {st.session_state.language}</p><hr>", unsafe_allow_html=True)
        navs = [('home','⌂','Dashboard'), ('crop_rec','🌾','Crop Rec'), ('pest','🐛','Pest'), ('weather','🌦','Weather'), ('soil','🧪','Soil'), ('sustainable','♻️','Sustainable')]
        for k, i, l in navs:
            if st.button(f"{i} {l}", key=f"nav_{k}", use_container_width=True):
                st.session_state.nav = k; st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True); st.caption("Aditya Sahani | Reg 1000414")

def render_home():
    sidebar()
    st.markdown(f"<h1 style='text-align:center;'>Welcome, Farmer</h1><p style='text-align:center; opacity:0.6;'>Hyper-local tools for <b>{st.session_state.state}</b></p><br>", unsafe_allow_html=True)
    f_cols = st.columns(5)
    feats = [('crop_rec','🌾','Crop Rec'), ('pest','🐛','Pest & Disease'), ('weather','🌦','Weather Alerts'), ('soil','🧪','Soil Health'), ('sustainable','♻️','Sustainable')]
    for i, (k, icon, l) in enumerate(feats):
        with f_cols[i]:
            st.markdown(f"<div class='feature-card'><div style='font-size:2.5rem;'>{icon}</div><b>{l}</b></div>", unsafe_allow_html=True)
            if st.button("OPEN", key=f"go_{k}", use_container_width=True): st.session_state.nav = k; st.rerun()

# ── 1. CROP RECOMMENDATION TAB ──────────────────────────────────────────────
def render_crop_rec():
    sidebar()
    st.markdown("<h1>🌾 Crop Recommendation</h1><p style='opacity:0.7;'>Get region-specific crop suggestions based on your resources.</p>", unsafe_allow_html=True)
    
    with st.form("crop_form"):
        c1, c2, c3, c4 = st.columns(4)
        budget = c1.text_input("Budget (e.g. $1000 or ₹50000)")
        water = c2.selectbox("Water Availability", ["Low", "Medium", "High"])
        soil = c3.selectbox("Soil Type", ["Loamy", "Clay", "Sandy", "Silty", "Peaty", "Saline"])
        season = c4.selectbox("Season", ["Auto-detect", "Summer", "Monsoon/Rainy", "Winter", "Spring"])
        goal = st.text_input("Describe your goal", placeholder="e.g. High profit crop for 1 acre in 3 months")
        submitted = st.form_submit_button("Get Recommendations")

    if submitted and goal:
        prompt = f"""Language: {st.session_state.language}. Location: {st.session_state.state}. Task: Crop Recommendation.
        Inputs: Budget: {budget}, Water: {water}, Soil: {soil}, Season: {season}, Goal: "{goal}".
        JSON format exactly: {{"location_analysis": "string", "suggestions": [{{"crop_name": "string", "reason": "string", "risk_level": "LOW/MEDIUM/HIGH", "market_potential": "string"}}], "confidence_score": 0-100}}"""
        
        with st.spinner("Analyzing soil, climate, and market data..."):
            res = call_ai(prompt)
            if res:
                st.markdown(f"<div class='card'><b>📍 Location & Resource Analysis:</b> {res.get('location_analysis')}</div>", unsafe_allow_html=True)
                for crop in res.get('suggestions', [])[:3]:
                    st.markdown(f"""
                    <div class='card'>
                        <span class='badge risk-{crop.get('risk_level','LOW')}'>{crop.get('risk_level')} Risk</span>
                        <h3 style='margin-top:5px;'>🌾 {crop.get('crop_name')}</h3>
                        <p><b>Why:</b> {crop.get('reason')}</p>
                        <p style='color:var(--wheat);'><b>📈 Market Potential:</b> {crop.get('market_potential')}</p>
                    </div>""", unsafe_allow_html=True)
                render_confidence_bar(res.get('confidence_score', 80))

# ── 2. PEST & DISEASE TAB ───────────────────────────────────────────────────
def render_pest():
    sidebar()
    st.markdown("<h1>🐛 Pest & Disease Diagnosis</h1>", unsafe_allow_html=True)
    
    with st.form("pest_form"):
        c1, c2 = st.columns([1, 1])
        crop_name = c1.text_input("Crop Name", placeholder="e.g. Tomatoes")
        duration = c2.selectbox("How long since symptoms appeared?", ["Just noticed (1-2 days)", "A few days (3-7 days)", "Over a week", "Several weeks"])
        symptoms = st.text_area("Describe Symptoms", placeholder="e.g. Yellowing leaves with black spots on the bottom")
        st.file_uploader("📸 Upload Image (Coming Soon - Future Upgrade)", disabled=True)
        submitted = st.form_submit_button("Diagnose Issue")

    if submitted and symptoms:
        prompt = f"""Language: {st.session_state.language}. Location: {st.session_state.state}. Task: Pest/Disease Diagnosis.
        Crop: {crop_name}. Symptoms: {symptoms}. Duration: {duration}.
        JSON exactly: {{"diagnosis_result": "string", "treatment_steps": ["step1", "step2"], "organic_option": "string", "prevention_tip": "string", "safety_warning": "string"}}"""
        
        with st.spinner("Consulting agricultural pathology database..."):
            res = call_ai(prompt)
            if res:
                st.markdown(f"<div class='card'><h3 style='color:#E67E22;'>🩺 Diagnosis: {res.get('diagnosis_result')}</h3></div>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='card'><h4>🧪 Treatment Steps</h4><ul>" + "".join([f"<li>{s}</li>" for s in res.get('treatment_steps',[])]) + "</ul></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='card'><h4>🌿 Organic Option</h4><p>{res.get('organic_option')}</p></div>", unsafe_allow_html=True)
                
                st.info(f"🛡️ **Prevention:** {res.get('prevention_tip')}")
                st.error(f"⚠️ **Safety Warning:** {res.get('safety_warning')}")

# ── 3. WEATHER ALERTS TAB ───────────────────────────────────────────────────
def render_weather():
    sidebar()
    st.markdown("<h1>🌦 Smart Weather Alerts</h1>", unsafe_allow_html=True)
    
    with st.form("weather_form"):
        c1, c2, c3 = st.columns(3)
        current_weather = c1.text_input("Current Weather", placeholder="e.g. Cloudy, Humid")
        temp = c2.slider("Temperature (°C)", -10, 50, 30)
        forecast = c3.selectbox("Upcoming Forecast Risk", ["Heatwave", "Heavy Rain / Flood", "Frost", "Drought / Dry Spell", "High Winds"])
        crop = st.text_input("Primary Crop Affected", placeholder="e.g. Flowering Wheat")
        submitted = st.form_submit_button("Generate Action Plan")

    if submitted and crop:
        prompt = f"""Language: {st.session_state.language}. Location: {st.session_state.state}. Task: Weather Crisis Management.
        Weather: {current_weather} at {temp}C. Risk: {forecast}. Crop: {crop}.
        JSON exactly: {{"risk_level": "LOW/MEDIUM/HIGH", "yield_impact_estimate": "string", "immediate_actions": ["24h step1", "24h step2"], "short_term_actions": ["7day step1", "7day step2"]}}"""
        
        with st.spinner("Calculating climatic impact..."):
            res = call_ai(prompt)
            if res:
                st.markdown(f"<div class='card'><span class='badge risk-{res.get('risk_level','HIGH')}'>{res.get('risk_level')} RISK TO {crop.upper()}</span><h3>📉 Yield Impact Estimate</h3><p>{res.get('yield_impact_estimate')}</p></div>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='card' style='border-left:4px solid #C0392B;'><h4>🚨 Immediate Actions (Next 24 Hrs)</h4><ul>" + "".join([f"<li>{s}</li>" for s in res.get('immediate_actions',[])]) + "</ul></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown("<div class='card' style='border-left:4px solid #E67E22;'><h4>📅 Short-term Actions (Next 7 Days)</h4><ul>" + "".join([f"<li>{s}</li>" for s in res.get('short_term_actions',[])]) + "</ul></div>", unsafe_allow_html=True)

# ── 4. SOIL HEALTH TAB ──────────────────────────────────────────────────────
def render_soil():
    sidebar()
    st.markdown("<h1>🧪 Soil Health & Nutrients</h1>", unsafe_allow_html=True)
    
    with st.form("soil_form"):
        c1, c2 = st.columns(2)
        ph = c1.slider("Soil pH", 0.0, 14.0, 6.5, 0.1)
        om = c1.slider("Organic Matter (%)", 0.0, 10.0, 2.5, 0.1)
        target_crop = c1.text_input("Target Crop", placeholder="e.g. Potatoes")
        
        n = c2.select_slider("Nitrogen (N)", ["Very Low", "Low", "Medium", "High", "Excessive"], value="Medium")
        p = c2.select_slider("Phosphorus (P)", ["Very Low", "Low", "Medium", "High", "Excessive"], value="Medium")
        k = c2.select_slider("Potassium (K)", ["Very Low", "Low", "Medium", "High", "Excessive"], value="Medium")
        submitted = st.form_submit_button("Analyze Soil Profile")

    if submitted:
        prompt = f"""Language: {st.session_state.language}. Location: {st.session_state.state}. Task: Soil Analysis.
        Data: pH: {ph}, OM: {om}%, N: {n}, P: {p}, K: {k}. Target Crop: {target_crop}.
        JSON exactly: {{"classification": "Acidic/Neutral/Alkaline", "nutrient_balance_summary": "string", "crop_compatibility_score": 0-100, "amendment_recommendations": ["rec1", "rec2"]}}"""
        
        with st.spinner("Processing chemical profile..."):
            res = call_ai(prompt)
            if res:
                score = res.get('crop_compatibility_score', 50)
                color = "#27AE60" if score > 75 else "#E67E22" if score > 40 else "#C0392B"
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='card' style='text-align:center;'><h4>Classification</h4><h2 style='color:var(--wheat);'>{res.get('classification')}</h2></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='card' style='text-align:center;'><h4>Compatibility for {target_crop}</h4><h2 style='color:{color};'>{score}/100</h2></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='card' style='text-align:center;'><h4>Organic Matter</h4><h2>{om}%</h2></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='card'><h4>⚖️ Nutrient Balance Summary</h4><p>{res.get('nutrient_balance_summary')}</p></div>", unsafe_allow_html=True)
                st.markdown("<div class='card'><h4>💊 Amendment Recommendations</h4><ul>" + "".join([f"<li>{s}</li>" for s in res.get('amendment_recommendations',[])]) + "</ul></div>", unsafe_allow_html=True)

# ── 5. SUSTAINABLE FARMING TAB ──────────────────────────────────────────────
def render_sustainable():
    sidebar()
    st.markdown("<h1>♻️ Forward-Thinking Sustainability</h1><p style='opacity:0.7;'>Modernize your farm for the future.</p>", unsafe_allow_html=True)
    
    with st.form("sus_form"):
        c1, c2, c3 = st.columns(3)
        practice = c1.selectbox("Select Innovation Practice", ["Drip/Precision Irrigation", "Organic Composting System", "Crop Rotation & Cover Crops", "Zero Tillage Farming", "Solar Water Pumps"])
        farm_size = c2.text_input("Farm Size", placeholder="e.g. 5 Acres")
        budget = c3.text_input("Available Budget", placeholder="e.g. $2000")
        submitted = st.form_submit_button("Generate Implementation Plan")

    if submitted:
        prompt = f"""Language: {st.session_state.language}. Location: {st.session_state.state}. Task: Sustainable Farm Implementation.
        Practice: {practice}. Farm Size: {farm_size}. Budget: {budget}.
        JSON exactly: {{"vision_statement": "string", "implementation_steps": ["step1", "step2", "step3"], "expected_roi_time": "string", "environmental_impact": "string", "confidence_score": 0-100}}"""
        
        with st.spinner("Designing sustainable architecture..."):
            res = call_ai(prompt)
            if res:
                st.markdown(f"<div class='card' style='border: 1px solid var(--sage); background:rgba(74,124,89,0.1);'><h3 style='color:var(--sage);'>🌍 Vision</h3><p>{res.get('vision_statement')}</p></div>", unsafe_allow_html=True)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown("<div class='card'><h4>⚙️ Step-by-Step Implementation</h4><ol>" + "".join([f"<li style='margin-bottom:10px;'>{s}</li>" for s in res.get('implementation_steps',[])]) + "</ol></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='card'><h4>⏳ Expected ROI Time</h4><p style='font-size:1.2rem; color:var(--wheat); font-weight:bold;'>{res.get('expected_roi_time')}</p></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='card'><h4>🌱 Environmental Impact</h4><p>{res.get('environmental_impact')}</p></div>", unsafe_allow_html=True)

# ── MAIN ROUTER ─────────────────────────────────────────────────────────────
def main():
    inject_css()
    if not st.session_state.onboarding_complete:
        pages = {'hero': page_hero, 'country': page_country, 'state': page_state, 'language': page_language}
        pages.get(st.session_state.page, page_hero)()
    else:
        nav = st.session_state.nav
        if nav == 'home': render_home()
        elif nav == 'crop_rec': render_crop_rec()
        elif nav == 'pest': render_pest()
        elif nav == 'weather': render_weather()
        elif nav == 'soil': render_soil()
        elif nav == 'sustainable': render_sustainable()

if __name__ == "__main__":
    main()
