# quote_explainer.py
"""
Quote‑of‑the‑Day Explainer
=========================
A simple web app that fetches a random quote from the Quotable API and uses an LLM to explain it.

Usage:
    streamlit run main.py

Environment variables:
    OPENAI_API_KEY   – your OpenAI key (required for LLM explanation)

Dependencies (install with pip):
    pip install streamlit requests openai python-dotenv
"""
from __future__ import annotations

import os
import requests
import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path

# Disable InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
QUOTABLE_URL = "https://api.quotable.io/random"
DEFAULT_LLM_MODEL = "gpt-4o-mini"  # safer / cheaper default; change as needed.

# Set page config
st.set_page_config(
    page_title="Elegant Quote Insights",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Background image function
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1535682215715-c5c6c5f8e186?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        .block-container {{
            backdrop-filter: blur(10px);
            background-color: rgba(255, 255, 255, 0.85);
            padding: 3rem !important;
            border-radius: 20px;
            max-width: 800px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_url()

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 600;
    }
    
    .quote-container {
        background-color: rgba(245, 245, 245, 0.7);
        border-radius: 15px;
        padding: 30px 40px;
        margin: 30px 0;
        border-left: 8px solid #c9a959;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(5px);
    }
    
    .quote-text {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 32px;
        font-weight: 500;
        font-style: italic;
        color: #333;
        line-height: 1.4;
        margin-bottom: 20px;
    }
    
    .quote-author {
        font-family: 'Montserrat', sans-serif;
        font-size: 18px;
        text-align: right;
        color: #555;
        font-weight: 500;
        letter-spacing: 1px;
    }
    
    .explanation-container {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 30px 40px;
        margin: 30px 0;
        border: 1px solid #eaeaea;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    }
    
    .explanation-container h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 26px;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
        border-bottom: 1px solid #eaeaea;
        padding-bottom: 10px;
    }
    
    .explanation-container p {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        line-height: 1.8;
        color: #444;
    }
    
    .title {
        font-family: 'Cormorant Garamond', serif !important;
        color: #3a3a3a;
        font-size: 60px;
        text-align: center;
        margin-bottom: 10px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .subtitle {
        font-family: 'Montserrat', sans-serif;
        color: #666;
        font-size: 18px;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .stButton button {
        background-color: #c9a959 !important;
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500 !important;
        letter-spacing: 1.5px !important;
        padding: 15px 25px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(201, 169, 89, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(201, 169, 89, 0.4) !important;
    }
    
    .css-1544g2n {
        padding: 3rem 1rem 1.5rem !important;
    }
    
    .stSidebar {
        background-color: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .css-6qob1r {
        background-color: transparent !important;
    }
    
    .css-10trblm {
        font-family: 'Cormorant Garamond', serif !important;
        color: #333 !important;
        font-weight: 600 !important;
    }
    
    .css-81oif8 {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .footer {
        margin-top: 50px;
        text-align: center;
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        color: #888;
        letter-spacing: 1px;
    }
    
    .footer a {
        color: #c9a959;
        text-decoration: none;
        border-bottom: 1px dotted #c9a959;
    }
    
    .footer a:hover {
        color: #b08d3c;
        border-bottom: 1px solid #b08d3c;
    }
    
    .info {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px !important;
        padding: 20px !important;
        border-left: 5px solid #c9a959 !important;
    }
    
    .stSpinner > div {
        border-color: #c9a959 transparent transparent !important;
    }
</style>
""", unsafe_allow_html=True)

def fetch_random_quote() -> dict[str, str]:
    """Return a dict with keys: content, author."""
    resp = requests.get(QUOTABLE_URL, timeout=10, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return {"content": data["content"], "author": data["author"]}

def get_explanation(content: str, author: str, model: str) -> str:
    """Return explanation string using LLM."""
    system_prompt = (
        "You are a wise, eloquent philosopher with deep insights. When given a quote, explain its profound meaning "
        "in an elegant, thoughtful way using beautiful language. Keep it concise (120 words max) but make it sound sophisticated and profound."
    )
    user_prompt = f"Quote: \"{content}\" — {author}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=300
    )

    explanation = response.choices[0].message.content.strip()
    return explanation

# App UI
st.markdown("<h1 class='title'>Elegant Quote Insights</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Discover the profound wisdom behind timeless quotes</p>", unsafe_allow_html=True)

# Add a decorative divider
st.markdown("<div style='text-align:center; padding: 10px 0 30px 0;'><span style='display:inline-block; width:100px; height:2px; background-color:#c9a959;'></span></div>", unsafe_allow_html=True)

# Model selection
with st.sidebar:
    st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 28px; margin-bottom: 20px;'>Settings</h3>", unsafe_allow_html=True)
    model = st.selectbox(
        "AI Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0
    )
    
    st.markdown("<div style='margin-top: 40px;'><h4 style='font-family: \"Cormorant Garamond\", serif; font-size: 22px; margin-bottom: 10px;'>About</h4></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; color: #666; line-height: 1.6;'>This elegant app provides AI-powered insights into the profound meanings behind timeless quotes, helping you discover wisdom in the words of great thinkers.</p>", unsafe_allow_html=True)

# Button to fetch a new quote
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ Discover New Quote", use_container_width=True):
        with st.spinner("Fetching your quote..."):
            quote = fetch_random_quote()
            st.session_state.quote = quote
            
            # Get explanation if API key is available
            if os.getenv("OPENAI_API_KEY"):
                with st.spinner("Crafting an elegant explanation..."):
                    explanation = get_explanation(quote["content"], quote["author"], model)
                    st.session_state.explanation = explanation
            else:
                st.session_state.explanation = None

# Display quote and explanation if available
if "quote" in st.session_state:
    quote = st.session_state.quote
    st.markdown(
        f"""
        <div class="quote-container">
            <div class="quote-text">"{quote['content']}"</div>
            <div class="quote-author">— {quote['author']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display explanation if available
    if "explanation" in st.session_state and st.session_state.explanation:
        st.markdown(
            f"""
            <div class="explanation-container">
                <h3>Illumination</h3>
                <p>{st.session_state.explanation}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif "explanation" in st.session_state and st.session_state.explanation is None:
        st.warning("Set your OPENAI_API_KEY environment variable to receive an insightful explanation.")
else:
    with st.container():
        st.markdown("<div class='info'>Click the button above to discover a timeless quote and receive an elegant explanation of its deeper meaning.</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Crafted with elegance | Quotes from <a href='https://github.com/lukePeavey/quotable' target='_blank'>Quotable API</a></div>", unsafe_allow_html=True) 