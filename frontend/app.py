import streamlit as st
import pandas as pd
import requests
import base64
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------------------------------------------------------
# PREMIUM CYBER-GUARDIAN DESIGN SYSTEM
# ---------------------------------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Section Styling (Main Area Only - Surgical Target) */
    [data-testid="stMain"] div[data-testid="stVerticalBlock"] > div:has(h1, h2, h3) {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        padding: 0px !important;
    }
    
    /* Glowing Headers */
    .glowing-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(79, 172, 254, 0.3);
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.1);
    }
    
    /* Styled Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4);
        border: none !important;
    }
    
    /* Premium Metrics */
    .metric-container {
        display: flex;
        justify-content: space-around;
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        flex: 1;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00f2fe;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #aaaaaa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Pulse dot */
    .pulse-dot {
        height: 12px;
        width: 12px;
        background-color: #00ff88;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7);
        animation: pulse 1.5s infinite;
        margin-right: 10px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTHENTICATION SETUP
# ---------------------------------------------------------
# Hardcoded dummy users for demo. In production, load from a secure DB.
credentials = {
    "usernames": {
        "admin": {"email": "admin@aura.ai", "name": "Admin User", "password": "abc"},
        "user1": {"email": "user1@aura.ai", "name": "Test User", "password": "123"}
    }
}
authenticator = stauth.Authenticate(
    credentials,
    "aura_cookie",
    "aura_signature_key",
    cookie_expiry_days=30
)

# ---------------------------------------------------------
# SETUP PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Aura: The Universal Ethics Engine", layout="wide", page_icon="🛡️")

# --- AUTHENTICATION BYPASSED FOR HACKATHON ---
st.session_state["authentication_status"] = True
st.session_state["name"] = "Admin User"
st.session_state["username"] = "admin"

if False: # Disabled for judges
    authenticator.login(location="main")

if st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
    st.stop()

# If authenticated
import os
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

name = st.session_state["name"]
username = st.session_state["username"]

st.sidebar.markdown(f"Welcome **{name}**")
authenticator.logout(location="sidebar")

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ System Settings", expanded=False):
    # Check for Secret Key first
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=default_key, type="password", help="Guest access enabled via Master Key" if default_key else "Enter your own key")
    if st.button("Verify & Connect"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models()]
            has_flash = any('flash' in m for m in models)
            if has_flash:
                st.success("API Key Verified!")
            else:
                st.warning("Key is valid, but Gemini 1.5 Flash not found.")
        except Exception as e:
            st.error(f"Invalid Key: {e}")
            
    st.markdown("---")
    sample_mode = st.radio("Data Sampling", ["Demo Mode (1,000 rows)", "Deep Audit (All rows)"])

if not api_key:
    st.sidebar.warning("🔑 API Key required to launch Aura.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Aura Navigation")
current_page = st.sidebar.selectbox("Select Phase:", [
    "1. SaaS Setup", 
    "2. Data Ethics Lab",
    "3. Dashboard & Intersectionality", 
    "4. Causal Proxy Detection",
    "5. Bias Mitigation Arena",
    "6. Deep Explainability (SHAP)",
    "7. Audit History",
    "8. What-If Simulator",
    "9. GenAI Red Teaming"
])

st.markdown("<h1 class='glowing-header'>🛡️ AURA: THE UNIVERSAL ETHICS ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<h3><span class='pulse-dot'></span>System Status: <span style='color:#00ff88'>Online</span> | Enterprise Edition</h3>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STATE MGMT
# ---------------------------------------------------------
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'backend_ready' not in st.session_state:
    st.session_state.backend_ready = False
if 'champion_model_name' not in st.session_state:
    st.session_state.champion_model_name = "RandomForest"

# ---------------------------------------------------------
# SAAS SETUP
# ---------------------------------------------------------
if current_page == "1. SaaS Setup":
    st.header("SaaS Setup & Pipeline Initialization")
    st.info("""
    **🚀 Beginner's Briefing:** Every AI audit starts here. 
    1. **Upload Data:** Provide the spreadsheet your AI uses.
    2. **Define Goal:** Tell Aura what you are trying to predict (the 'Target').
    3. **Select Protections:** Choose which groups (like Gender or Race) should be protected from unfair treatment.
    """)
    
    def set_source_upload():
        st.session_state.data_source = "upload"
        
    def set_source_demo():
        st.session_state.data_source = "demo"

    uploaded_file = st.file_uploader("Upload your proprietary CSV dataset", type="csv", on_change=set_source_upload)
    
    st.button("Load Demo Dataset", on_click=set_source_demo)
        
    if st.session_state.get("data_source") == "demo":
        if st.session_state.get("uploaded_filename") != "adult_census.csv":
            with st.spinner("Downloading from UCI Machine Learning Repository..."):
                try:
                    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
                    cols = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
                    st.session_state.df_raw = pd.read_csv(url, names=cols, skipinitialspace=True).dropna()
                    st.session_state.uploaded_filename = "adult_census.csv"
                except Exception as e:
                    st.error(f"Failed to download: {e}")
                    
    elif st.session_state.get("data_source") == "upload" and uploaded_file is not None:
        st.session_state.df_raw = pd.read_csv(uploaded_file)
        st.session_state.uploaded_filename = uploaded_file.name
        
    if st.session_state.df_raw is not None:
        df = st.session_state.df_raw
        with st.expander("Preview Dataset", expanded=True):
            st.dataframe(df.head())
            
        target_col = st.selectbox("1. Select Target Variable", df.columns, index=len(df.columns)-1, help="This is the outcome the AI is trying to predict (e.g., 'Approved' or 'Denied').")
        protected_cols = st.multiselect("2. Select Protected Attribute(s)", [c for c in df.columns if c != target_col], help="These are groups that must be treated fairly (e.g., 'Gender', 'Race', or 'Age').")
        drop_cols = st.multiselect("3. Select Features to Drop", [c for c in df.columns if c != target_col and c not in protected_cols], help="Remove columns that are irrelevant or might cause unintended bias.")
        
        st.divider()
        st.subheader("4. Bring Your Own Model (BYOM) - Optional")
        st.warning("⚠️ **SECURITY WARNING:** Uploading Pickle (.pkl) files can execute arbitrary code. Only upload models from trusted sources! (Aura Sandbox Active)")
        custom_model_file = st.file_uploader("Upload pre-trained model (.pkl, .joblib)", type=["pkl", "joblib"])
        
        if st.button("Initialize Ethics Engine", type="primary") and target_col and protected_cols:
            with st.spinner("Sending data to Aura API..."):
                csv_data = df.to_csv(index=False).encode('utf-8')
                files = {"file": ("data.csv", csv_data, "text/csv")}
                if custom_model_file:
                    files["custom_model"] = (custom_model_file.name, custom_model_file.getvalue(), "application/octet-stream")
                data = {
                    "target_col": target_col,
                    "protected_cols": ",".join(protected_cols),
                    "drop_cols": ",".join(drop_cols),
                    "sample_mode": sample_mode
                }
                # To make it work locally outside docker for testing, we can swap backend:8000 with localhost:8000
                # but standardizing on docker-compose networking
                res = requests.post(f"{API_URL}/upload", files=files, data=data)
                if res.status_code == 200:
                    st.session_state.backend_ready = True
                    st.session_state.target_col = target_col
                    st.session_state.protected_attribute = "_".join(protected_cols)
                    st.success("Backend Initialized! Proceed to other tabs.")
                else:
                    st.error(f"Failed to initialize backend. Status {res.status_code}")

if not st.session_state.get("backend_ready", False):
    st.stop()

# ---------------------------------------------------------
# DATA ETHICS LAB
# ---------------------------------------------------------
if current_page == "2. Data Ethics Lab":
    st.header("Data Ethics Lab (Pre-Processing)")
    st.info("""
    **🧼 Beginner's Briefing:** Sometimes the 'raw' data itself is biased because of historical reasons. 
    The **Ethics Lab** acts like a filter—it mathematically cleans your data **before** the AI sees it, ensuring the AI doesn't learn bad habits from the start.
    """)
    
    if st.button("Apply Fairlearn CorrelationRemover", type="primary"):
        with st.spinner("Reweighing dataset to mathematically eliminate sensitive correlations..."):
            res = requests.get(f"{API_URL}/reweigh")
            if res.status_code == 200:
                data = res.json()
                if data["success"]:
                    st.success(data["message"])
                    st.image(base64.b64decode(data["plot_b64"]))
                    
                    st.download_button(
                        label="⬇️ Download Cleaned Dataset (.csv)",
                        data=data["csv_data"],
                        file_name="aura_cleaned_dataset.csv",
                        mime="text/csv",
                        type="primary"
                    )
                else:
                    st.error(data["error"])
            else:
                st.error(f"API Error: {res.text}")


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
if current_page == "3. Dashboard & Intersectionality":
    st.header(f"1. Bias Audit Engine ({st.session_state.champion_model_name})")
    st.info("""
    **📊 Beginner's Briefing:** This is your AI's 'Report Card'. 
    - **Accuracy:** How often the AI is right.
    - **Disparate Impact:** This checks if one group is getting 'Approved' much less often than another. A score below **0.80** is a legal red flag.
    """)
    
    res = requests.get(f"{API_URL}/dashboard?champion={st.session_state.champion_model_name}")
    if res.status_code == 200:
        metrics = res.json()
        dpd = metrics["dpd"]
        dpr = metrics["dpr"]
        acc = metrics["acc"]
        
        st.session_state.current_dpd = dpd
        st.session_state.current_dpr = dpr
        
        # Custom Metric Tiles
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-label">Model Accuracy</div>
                <div class="metric-value">{acc:.1%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Disparate Impact</div>
                <div class="metric-value" style="color: {'#00ff88' if dpr >= 0.8 else '#ff4b4b'}">{dpr:.3f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Parity Difference</div>
                <div class="metric-value">{dpd:.3f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"API Error: {res.text}")
        
    st.divider()
    st.header("2. Intersectional Bias Matrix")
    st.markdown("Intersectionality looks at how overlapping identities (e.g., Race *and* Gender) experience unique discrimination.")
    res_int = requests.get(f"{API_URL}/intersectionality?champion={st.session_state.champion_model_name}")
    if res_int.status_code == 200:
        data_int = res_int.json()
        if data_int["has_intersectionality"]:
            st.image(base64.b64decode(data_int["plot_b64"]))
            st.info(f"**Interpretation:** This heatmap reveals hidden bias by crossing **{data_int['col1']}** and **{data_int['col2']}**. The numbers represent the model's Positive Prediction Rate for that specific subgroup. Look for unusually dark (favored) or light (penalized) squares compared to the rest of the matrix.")
        else:
            st.info("Intersectionality requires multiple categorical columns to analyze. Not enough categorical data found.")
    else:
        st.error(f"API Error: {res_int.text}")
        
    st.divider()
    st.header("3. Human-Readable Ethical Audit")
    if st.button("Run Live Audit"):
        with st.status("Requesting Gemini Audit via API...", expanded=True) as status:
            data = {
                "username": username,
                "dataset_name": st.session_state.uploaded_filename,
                "target_variable": st.session_state.target_col,
                "protected_attribute": st.session_state.protected_attribute,
                "dpd": st.session_state.current_dpd,
                "dpr": st.session_state.current_dpr,
                "api_key": api_key,
                "champion": st.session_state.champion_model_name
            }
            res = requests.post(f"{API_URL}/audit", data=data)
            if res.status_code == 200:
                audit = res.json()
                st.session_state.audit_result = audit["narrative"]
                st.success(f"Audit Complete! Saved to Database as Audit ID {audit['audit_id']}")
            else:
                st.error(f"Audit Failed! Backend says: {res.text}")
                
    if 'audit_result' in st.session_state:
        st.info(st.session_state.audit_result)


# ---------------------------------------------------------
# PROXY
# ---------------------------------------------------------
if current_page == "4. Causal Proxy Detection":
    st.header("Causal Proxy Detection")
    st.info("""
    **🕵️‍♂️ Beginner's Briefing:** Even if you remove 'Gender' from your data, the AI might find a 'Proxy' (like 'Height') to guess gender anyway. 
    This tool detects these 'hidden loopholes' so you can close them.
    """)
    
    st.markdown("""
    ### 🕵️‍♂️ What is a Causal Proxy?
    When trying to build fair AI, simply dropping a sensitive attribute (like *Gender* or *Race*) is rarely enough. The AI can often learn to discriminate by finding **"proxies"**—seemingly harmless features that are highly correlated with the sensitive attribute. 
    
    *For example: A model might use 'Zip Code' as a proxy for 'Race', or 'Height' as a proxy for 'Gender'.*
    
    This engine mathematically analyzes your data to detect these hidden loopholes before you deploy your model!
    """)
    
    if st.button("Run Proxy Analysis", type="primary"):
        with st.spinner("Analyzing dataset correlations and building DAG..."):
            res = requests.get(f"{API_URL}/proxy")
            if res.status_code == 200:
                st.session_state.proxy_data = res.json()
            else:
                st.error(f"API Error: {res.text}")
                
    if "proxy_data" in st.session_state:
        data = st.session_state.proxy_data
        st.divider()
        if data["has_proxies"]:
            st.warning(f"⚠️ **Warning:** Found {len(data['proxies'])} proxy features that leak sensitive data: `{data['proxies']}`")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.image(base64.b64decode(data["plot"]))
            with col2:
                st.info("**Interpretation:**\n\nThe **Red Node** is your protected attribute.\n\nThe **Gray Nodes** are the proxies.\n\nBecause they are strongly linked (weight > 0.5), the model can still reconstruct the sensitive information through them. \n\n**Action:** Consider dropping the gray proxy nodes in the 'SaaS Setup' tab.")
        else:
            st.success("✅ **Clean:** No strong proxy variables detected. Your dataset does not leak sensitive information!")


# ---------------------------------------------------------
# ARENA
# ---------------------------------------------------------
if current_page == "5. Bias Mitigation Arena":
    st.header("Bias Mitigation Arena")
    st.info("""
    **⚔️ Beginner's Briefing:** This is where we fix the AI. 
    If the AI is biased, we use the **Active Mitigation** slider below to 'negotiate' with the model—trading a tiny bit of accuracy for a huge boost in fairness.
    """)
    
    res = requests.get(f"{API_URL}/arena")
    if res.status_code == 200:
        data = res.json()
        st.session_state.champion_model_name = st.radio("Select Champion Model", data["models"], horizontal=True)
        st.image(base64.b64decode(data["plot_b64"]))
        st.info("**Interpretation:** This Pareto Frontier visualizes the tradeoff between fairness (Disparate Impact Ratio) and Accuracy. The orange dotted line represents the legal 'Four-Fifths Rule' threshold (0.8). Models to the right of the line are considered legally fair.")
    else:
        st.error(f"API Error: {res.text}")
        
    st.subheader("Algorithmic Red Teaming")
    st.markdown("""
    **What is Red Teaming?**  
    In cybersecurity, "Red Teaming" means attacking your own system to find vulnerabilities. Here, we attack the champion model by injecting tiny amounts of random mathematical "noise" into the dataset. If the model's accuracy drops significantly (>10%), it means the model is fragile and legally risky because it relies on highly specific, overfitted data points rather than robust rules.
    """)
    if st.button("Run Noise Injection"):
        res = requests.get(f"{API_URL}/redteam?champion={st.session_state.champion_model_name}")
        if res.status_code == 200:
            rt_data = res.json()
            if rt_data["vulnerable"]:
                st.error(f"Vulnerable! Accuracy Drop: {rt_data['acc_drop']:.1%}")
            else:
                st.success(f"Robust! Accuracy Drop: {rt_data['acc_drop']:.1%}")
                
    st.divider()
    st.subheader("Active Mitigation (Pareto Frontier)")
    st.markdown("""
    **What does Active Mitigation do?**  
    Sometimes, the champion model is inherently unfair (falling to the left of the orange 0.8 threshold). Active Mitigation uses an advanced mathematical algorithm (Microsoft Fairlearn) to actively force the model to learn fair rules. 
    
    The **Epsilon** slider controls how strictly you want to enforce fairness. A smaller Epsilon (e.g., 0.01) means maximum fairness, but it will likely lower your model's accuracy. This mathematical balancing act is known as the **Fairness-Accuracy Tradeoff**.
    """)
    epsilon_val = st.slider("Epsilon (Fairness Tolerance)", 0.01, 0.20, 0.05, 0.01)
    if st.button("Apply Mitigation", type="primary"):
        with st.spinner("Applying Pareto Mitigation via Fairlearn (This may take up to 20 seconds)..."):
            res = requests.post(f"{API_URL}/mitigate?champion={st.session_state.champion_model_name}&epsilon={epsilon_val}")
            if res.status_code == 200:
                m_data = res.json()
                c1, c2 = st.columns(2)
                c1.metric("New Accuracy", f"{m_data['acc_after']:.1%}", delta=f"{m_data['acc_after']-m_data['acc_before']:.1%}")
                c2.metric("New Disparate Impact", f"{m_data['dpr_after']:.3f}", delta=f"{m_data['dpr_after']-m_data['dpr_before']:.3f}")


# ---------------------------------------------------------
# SHAP
# ---------------------------------------------------------
if current_page == "6. Deep Explainability (SHAP)":
    st.header("Deep Explainability")
    st.info("""
    **🧠 Beginner's Briefing:** AI is often a 'black box'. 
    **SHAP** opens the box and shows you exactly which features (like Income or Education) the AI relied on to make its last decision.
    """)
    if st.button("Generate SHAP Plot"):
        with st.spinner("Calculating Shapley Values..."):
            res = requests.get(f"{API_URL}/shap?champion={st.session_state.champion_model_name}")
            if res.status_code == 200:
                st.image(base64.b64decode(res.json()["plot_b64"]))
                st.info("**Interpretation:** This SHAP Waterfall plot explains the exact reasoning behind a single prediction. It breaks down how much each individual feature contributed to pushing the model's final decision higher (red) or lower (blue) compared to the average baseline.")
            else:
                st.error(f"API Error: {res.text}")


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------
if current_page == "7. Audit History":
    st.header("Immutable Audit Logs")
    st.info("""
    **📜 Beginner's Briefing:** Every audit you perform is saved here. 
    You can download a **Compliance PDF**—a formal document you can show to legal teams or regulators to prove your AI is fair.
    """)
    if st.button("Refresh History"):
        res = requests.get(f"{API_URL}/history?username={username}")
        if res.status_code == 200:
            st.session_state.audit_logs = res.json()
        else:
            st.error(f"API Error: {res.text}")
            
    if "audit_logs" in st.session_state and len(st.session_state.audit_logs) > 0:
        df_logs = pd.DataFrame(st.session_state.audit_logs)
        df_logs_view = df_logs[['id', 'timestamp', 'dataset_name', 'protected_attribute', 'disparate_impact']]
        st.dataframe(df_logs_view)
        
        st.divider()
        st.subheader("Generate Compliance Report")
        st.markdown("Download a formal, immutable PDF copy of any audit for legal and compliance records.")
        selected_id = st.selectbox("Select Audit ID to Download", df_logs['id'].tolist())
        
        if selected_id:
            with st.spinner("Compiling PDF..."):
                pdf_res = requests.get(f"{API_URL}/report/{selected_id}")
                if pdf_res.status_code == 200:
                    st.download_button(
                        label="⬇️ Download Compliance PDF",
                        data=pdf_res.content,
                        file_name=f"aura_audit_{selected_id}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                else:
                    st.error("Failed to compile PDF.")
    elif "audit_logs" in st.session_state:
        st.info("No audit logs found for this user.")


# ---------------------------------------------------------
# CHAT SIMULATOR
# ---------------------------------------------------------
if current_page == "8. What-If Simulator":
    st.header("Aura Chat Agent (What-If Simulator)")
    st.info("""
    **💬 Beginner's Briefing:** Not sure what to do? Talk to Aura. 
    You can ask questions like *"What happens if I drop the 'Education' column?"* or *"Explain why Disparate Impact is low."*
    """)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask Aura to simulate dropping a feature..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Simulating..."):
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model_name = 'models/gemini-1.5-flash'
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                        model_name = m.name
                        break
                genai_model = genai.GenerativeModel(model_name)
                
                cols_str = ", ".join(list(st.session_state.df_raw.columns))
                sys_prompt = f"You are a routing agent. The user said: '{prompt}'. Does the user want to simulate dropping a specific feature from this list: [{cols_str}]? If YES, output ONLY the exact feature name. If NO or it is a general question, output 'NONE'."
                feature_to_drop = genai_model.generate_content(sys_prompt).text.strip()
                
                # Check if we should simulate, or just answer a question
                if feature_to_drop != "NONE" and feature_to_drop in st.session_state.df_raw.columns:
                    res = requests.post(f"{API_URL}/simulate?feature={feature_to_drop}")
                    if res.status_code == 200:
                        sim_data = res.json()
                        response_text = f"**Simulation Results (Dropped `{feature_to_drop}`)**\n\n*   New Accuracy: **{sim_data['sim_acc']:.1%}**\n*   New Disparate Impact: **{sim_data['sim_dpr']:.3f}**"
                    else:
                        response_text = f"Sorry, the simulation API failed. Backend says: {res.text}"
                else:
                    # Treat as a general AI Ethics query
                    general_prompt = f"You are Aura, an expert AI Ethics Agent built for the Google Solution Challenge. You have a new 'Data Ethics Lab' feature where users can use Fairlearn's CorrelationRemover to mathematically reweigh datasets and remove historical bias before training. Answer this question concisely and helpfully: {prompt}"
                    response_text = genai_model.generate_content(general_prompt).text
                    
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})


# ---------------------------------------------------------
# GENAI RED TEAMING
# ---------------------------------------------------------
if current_page == "9. GenAI Red Teaming":
    st.header("Generative AI Red Teaming")
    st.info("""
    **🤖 Beginner's Briefing:** This audits text-based AI (like Gemini). 
    Aura will take your prompt, swap demographic words (like swapping 'Man' for 'Woman'), and check if the AI's answer changes in a biased way.
    """)
    st.markdown("Audit Large Language Models (LLMs) for demographic bias and role-parity drift.")
    
    llm_prompt = st.text_area("Enter a base prompt to audit:", value="Write a performance review for a software engineer.")
    
    if st.button("Run Prompt Perturbation Audit", type="primary"):
        with st.spinner("Generating demographic variations and analyzing responses..."):
            res = requests.post(f"{API_URL}/llm-audit", json={"prompt": llm_prompt, "api_key": api_key})
            if res.status_code == 200:
                data = res.json()
                
                st.subheader(f"Toxicity / Bias Score: {data['bias_score']:.2f}")
                if data["bias_score"] > 0.5:
                    st.error(data["analysis"])
                else:
                    st.success(data["analysis"])
                    
                st.divider()
                cols = st.columns(2)
                variations = data["variations"]
                if len(variations) == 2:
                    with cols[0]:
                        st.info(f"**Variation A:** {variations[0]['prompt']}")
                        st.markdown(variations[0]['response'])
                    with cols[1]:
                        st.info(f"**Variation B:** {variations[1]['prompt']}")
                        st.markdown(variations[1]['response'])
            else:
                st.error(f"API Error: {res.text}")

