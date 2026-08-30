import streamlit as st
import google.generativeai as genai
import os
import json
import re

st.set_page_config(page_title="AI Resilience Matrix", layout="centered")

if "GOOGLE_API_KEY" not in os.environ:
    st.error("GOOGLE_API_KEY ist nicht gesetzt. Bitte in den Streamlit Secrets anlegen.")
    st.stop()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

GENERIC_HYPOS = {
    "Commodity Trap": [
        "Differenzierung durch überlegene Service-Layer oder Nischenpositionierung entwickeln.",
        "Direkte Kundenkanäle aufbauen — weg von reiner Plattform- und Handelsabhängigkeit.",
        "Community oder vertikale Expertise als Moat nutzen, um Preisdruck zu entkommen.",
    ],
    "Fragile Fortress": [
        "Produktdifferenzierung stärken, bevor KI-Transparenz den Kanal-Vorteil erodiert.",
        "Bestehende Kanalstärke nutzen, um First-Party-Daten und Lock-ins aufzubauen.",
        "Wechselkosten durch tiefere Prozessintegration oder Community-Bindung erhöhen.",
    ],
    "Hidden Champion": [
        "Direktzugang zum Endkunden aufbauen — DTC-Kanal, eigene App oder Community.",
        "Trust-Signale und digitale Sichtbarkeit stärken, damit KI-Agenten das Angebot validieren.",
        "First-Party-Daten über Produktregistrierung, Service-App oder Content-Plattform erschließen.",
    ],
    "Category Controller": [
        "Ökosystem-Tiefe ausbauen — API-Integrationen, Partner-Netzwerk, eigene Plattformlogik.",
        "KI-Resilienz durch strukturelle Präsenz in Trainingsdaten und LLM-Empfehlungen absichern.",
        "Efficiency Leakage verhindern — KI-gestützte Prozesse schneller einsetzen als Wettbewerb.",
    ],
}

QUADRANT_COLORS = {
    "Category Controller": "#e8f5e9",
    "Hidden Champion": "#e3f2fd",
    "Fragile Fortress": "#fff8e1",
    "Commodity Trap": "#ffebee",
}

st.title("AI Resilience Matrix")
st.markdown("Name und URL eingeben — die KI analysiert Moat und Channel Control vollautomatisch.")

brand = st.text_input("Unternehmens- oder Produktname")
url = st.text_input("Website-URL")

if st.button("Analyse starten"):
    if not brand or not url:
        st.warning("Bitte Name und URL eingeben.")
        st.stop()

    prompt = f"""Du bist ein strategischer Berater und analysierst Geschäftsmodelle mit der AI Resilience Matrix.

Die Matrix hat zwei Dimensionen:
- Competitive Moat (1-5): Wie stark differenziert und unersetzbar ist das Angebot? (Produktdifferenzierung, Switching Costs, Marke/Trust, Problem-Solution-Fit, Erwartungsmanagement)
- Channel Control (1-5): Wie stark ist der direkte Kundenzugang? (Wiederkaufmodell, First-Party-Daten, Advocacy, organische Akquise, Unabhängigkeit von Paid Media)

Daraus ergeben sich vier Quadranten:
- Category Controller: Moat >= 3, Control >= 3
- Hidden Champion: Moat >= 3, Control < 3
- Fragile Fortress: Moat < 3, Control >= 3
- Commodity Trap: Moat < 3, Control < 3

Analysiere das folgende Unternehmen anhand öffentlich verfügbarer Informationen, Geschäftsmodell-Logik und strukturellen Ableitungen:

Unternehmen: {brand}
URL: {url}

Leite Moat und Control aus dem Geschäftsmodell, der Branche, dem erkennbaren Vertriebsmodell und der digitalen Präsenz ab. Kennzeichne unsichere Ableitungen mit "vermutlich" oder "strukturell typisch für diesen Typ".

Antworte NUR als JSON ohne Markdown-Backticks:
{{
  "moat_score": 3.2,
  "control_score": 2.1,
  "quadrant": "Hidden Champion",
  "moat_confidence": "high",
  "control_confidence": "medium",
  "summary": "3-4 Sätze Analyse warum dieser Quadrant",
  "hypotheses": ["Hypothese 1", "Hypothese 2", "Hypothese 3"]
}}"""

    with st.spinner("KI analysiert Geschäftsmodell..."):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            r = json.loads(raw)
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {e}")
            st.stop()

    quadrant = r.get("quadrant", "Commodity Trap")
    moat = float(r.get("moat_score", 2.5))
    control = float(r.get("control_score", 2.5))
    moat_conf = r.get("moat_confidence", "medium")
    ctrl_conf = r.get("control_confidence", "medium")

    st.markdown(f"### {quadrant}")
    st.markdown(f"`{brand}` · {url}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Competitive Moat", f"{moat:.1f} / 5")
        st.progress(moat / 5)
        st.caption(f"Konfidenz: {'hoch' if moat_conf == 'high' else 'mittel'}")
    with col2:
        st.metric("Channel Control", f"{control:.1f} / 5")
        st.progress(control / 5)
        st.caption(f"Konfidenz: {'hoch' if ctrl_conf == 'high' else 'mittel'}")

    st.markdown("---")

    quadrants = {
        "Category Controller": (True, True),
        "Hidden Champion": (True, False),
        "Fragile Fortress": (False, True),
        "Commodity Trap": (False, False),
    }

    col_left, col_right = st.columns(2)
    labels = [
        ("Hidden Champion", col_left, True),
        ("Category Controller", col_right, True),
        ("Commodity Trap", col_left, False),
        ("Fragile Fortress", col_right, False),
    ]

    for name, col, is_top in labels:
        color = QUADRANT_COLORS[name]
        border = "3px solid #333" if name == quadrant else f"1px solid #ccc"
        with col:
            st.markdown(
                f'<div style="background:{color};border:{border};border-radius:8px;padding:12px;margin-bottom:8px;">'
                f'<strong>{name}</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("**Analyse**")
    st.write(r.get("summary", ""))

    st.markdown("**Generische Hebel**")
    for h in GENERIC_HYPOS.get(quadrant, []):
        st.markdown(f"→ {h}")

    st.markdown("**Kontextspezifische Hypothesen**")
    for h in r.get("hypotheses", []):
        st.markdown(f"→ {h}")
