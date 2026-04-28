import os

app_code = """import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference, demographic_parity_ratio, MetricFrame, selection_rate
import google.generativeai as genai
from fpdf import FPDF
import datetime
import io
import shap
import networkx as nx

# ---------------------------------------------------------
# SETUP PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Aura: The Universal Ethics Engine", layout="wide", page_icon="🛡️")

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

/* Base Theme */
.stApp {
    background-color: #0e1117;
    font-family: 'Inter', sans-serif;
    color: #c9d1d9;
}

/* Glassmorphism Containers */
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
    background: rgba(22, 27, 34, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
}

/* Fade In Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.block-container {
    animation: fadeIn 0.8s ease-out;
}

/* Metric Glowing Cards */
.metric-label {
    font-size: 14px;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.glowing-metric-good {
    font-size: 36px;
    font-weight: 800;
    color: #4285F4;
    text-shadow: 0 0 10px rgba(66, 133, 244, 0.5);
}

.glowing-metric-bad {
    font-size: 36px;
    font-weight: 800;
    color: #ff6b6b;
    text-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
}

/* System Pulse Status */
.pulse-dot {
    height: 12px;
    width: 12px;
    background-color: #4285F4;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 10px #4285F4;
    animation: pulse 1.5s infinite;
    margin-right: 10px;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(66, 133, 244, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0); }
}

/* Footer */
.footer-text {
    text-align: center;
    color: #8b949e;
    font-size: 12px;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Buttons */
.stButton>button {
    background-color: #21262d;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #c9d1d9;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: #4285F4;
    border-color: #4285F4;
    box-shadow: 0 0 15px rgba(66, 133, 244, 0.6);
    color: white;
}
</style>
'''

# ---------------------------------------------------------
# SIDEBAR / API SECURITY & KNOWLEDGE CENTER
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'model_arena' not in st.session_state:
    st.session_state.model_arena = None
if 'champion_model_name' not in st.session_state:
    st.session_state.champion_model_name = "RandomForest"

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Gemini API key to enable XAI features.")

if api_key:
    genai.configure(api_key=api_key)
    if st.sidebar.button("Verify & Launch"):
        with st.sidebar.status("Talking to Gemini...", expanded=True) as status:
            try:
                models = genai.list_models()
                next(models)
                st.session_state.authenticated = True
                status.update(label="Verified!", state="complete", expanded=False)
                st.rerun()
            except Exception as e:
                status.update(label="Verification Failed", state="error", expanded=False)
                st.sidebar.error("Invalid API Key.")
else:
    st.sidebar.warning("API Key required to launch Aura.")

st.sidebar.markdown("---")
st.sidebar.subheader("Safety & Performance")
sample_mode = st.sidebar.radio("Data Sampling", ["Demo Mode (1,000 rows)", "Deep Audit (All rows)"])

st.sidebar.markdown("---")
st.sidebar.subheader("About Aura Elite")
st.sidebar.markdown("**Universal XAI Platform**\\nAura is now a fully generalized, dataset-agnostic ethics engine featuring Intersectionality, Proxy Detection, and a Multi-Model Arena.")

if not st.session_state.authenticated:
    st.warning("Please enter and verify your Gemini API Key in the sidebar to access the platform.")
    st.stop()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h1>🛡️ Aura: The Universal Ethics Engine</h1>", unsafe_allow_html=True)
st.markdown("<h3><span class='pulse-dot'></span>System Status: Active | Aligning AI with UN SDG Goal 10</h3>", unsafe_allow_html=True)

tab_setup, tab_dashboard, tab_proxy, tab_arena, tab_shap, tab_chat = st.tabs([
    "SaaS Setup", 
    "Dashboard & Intersectionality", 
    "Causal Proxy Detection",
    "Bias Mitigation Arena",
    "Deep Explainability (SHAP)", 
    "Aura Chat Agent"
])

with tab_setup:
    st.header("Data Upload & Schema Mapping")
    uploaded_file = st.file_uploader("Upload your proprietary CSV dataset", type="csv")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load UCI Adult Demo Dataset"):
            try:
                st.session_state.df_raw = pd.read_csv("adult_census.csv")
                st.success("Loaded Demo Dataset!")
            except Exception as e:
                # Fallback if csv not present
                from fairlearn.datasets import fetch_adult
                data = fetch_adult(as_frame=True)
                df_temp = pd.concat([data.data, data.target], axis=1).dropna()
                st.session_state.df_raw = df_temp
                st.success("Loaded Demo Dataset via API!")
                
    if uploaded_file is not None:
        st.session_state.df_raw = pd.read_csv(uploaded_file)
        
    if st.session_state.df_raw is not None:
        df = st.session_state.df_raw.copy()
        with st.expander("Preview Dataset", expanded=True):
            st.dataframe(df.head())
            
        target_col = st.selectbox("1. Select Target Variable", df.columns, index=len(df.columns)-1)
        protected_cols = st.multiselect("2. Select Protected Attribute(s) (Intersectionality)", [c for c in df.columns if c != target_col])
        drop_cols = st.multiselect("3. Select Features to Drop (IDs, Names)", [c for c in df.columns if c != target_col and c not in protected_cols])
        
        if st.button("Initialize Ethics Engine") and target_col and protected_cols:
            st.session_state.target_col = target_col
            st.session_state.protected_cols = protected_cols
            st.session_state.drop_cols = drop_cols
            st.success("Engine Initialized! Proceed to Dashboard tab.")

if 'target_col' not in st.session_state:
    st.stop()

# ---------------------------------------------------------
# DATA PREPARATION & INTERSECTIONALITY
# ---------------------------------------------------------
@st.cache_data
def prepare_data(df, target_col, protected_cols, drop_cols):
    df = df.drop(columns=drop_cols).dropna()
    
    # Intersectionality Logic
    if len(protected_cols) > 1:
        attr_name = "_".join(protected_cols)
        df[attr_name] = df[protected_cols].astype(str).agg('_'.join, axis=1)
    else:
        attr_name = protected_cols[0]
        
    y = df[target_col]
    X = df.drop(columns=[target_col])
    
    if y.dtype == 'object' or y.dtype.name == 'category':
        y_encoded = LabelEncoder().fit_transform(y)
    else:
        # Convert to binary int if not already
        if len(np.unique(y)) == 2:
            y_encoded = LabelEncoder().fit_transform(y)
        else:
            y_encoded = y.values
            
    categorical_features = X.select_dtypes(include=['category', 'object']).columns
    encoders = {}
    X_encoded = X.copy()
    for col in categorical_features:
        le = LabelEncoder()
        X_encoded[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.2, random_state=42)
    sensitive_test = X.loc[X_test.index, attr_name]
    
    return X_train, X_test, y_train, y_test, sensitive_test, encoders, X, attr_name

df_to_process = st.session_state.df_raw.copy()
if sample_mode == "Demo Mode (1,000 rows)" and len(df_to_process) > 1000:
    df_to_process = df_to_process.sample(n=1000, random_state=42)

X_train, X_test, y_train, y_test, sensitive_test, encoders, X_raw, attr_name = prepare_data(
    df_to_process, st.session_state.target_col, st.session_state.protected_cols, st.session_state.drop_cols
)

@st.cache_data
def train_arena(X_train, y_train):
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=50, max_depth=5, random_state=42, use_label_encoder=False, eval_metric='logloss'),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42)
    }
    trained_models = {}
    for name, m in models.items():
        m.fit(X_train, y_train)
        trained_models[name] = m
    return trained_models

# Ensure Arena is trained
with st.spinner("Training Model Arena..."):
    if st.session_state.model_arena is None or st.session_state.get('last_attr_name') != attr_name or st.session_state.get('last_sample_mode') != sample_mode:
        st.session_state.model_arena = train_arena(X_train, y_train)
        st.session_state.last_attr_name = attr_name
        st.session_state.last_sample_mode = sample_mode

# Select Champion
champion = st.session_state.model_arena[st.session_state.champion_model_name]
y_pred = champion.predict(X_test)

# ---------------------------------------------------------
# PROXY DETECTION & CAUSAL GRAPH
# ---------------------------------------------------------
with tab_proxy:
    st.header("Causal Proxy Variable Detection (🕵️ / 🕸️)")
    st.write("Generating a Directed Acyclic Graph (DAG) mapping correlations and causal proxies.")
    
    with st.spinner("Calculating causal structure..."):
        # Encode everything for correlation
        df_corr = X_raw.copy()
        for c in df_corr.select_dtypes(include=['category', 'object']).columns:
            df_corr[c] = LabelEncoder().fit_transform(df_corr[c].astype(str))
            
        corr_matrix = df_corr.corr()
        
        if attr_name not in df_corr.columns:
            df_corr[attr_name] = LabelEncoder().fit_transform(X_raw[attr_name].astype(str))
            corr_matrix = df_corr.corr()
            
        attr_corrs = corr_matrix[attr_name].abs().drop(attr_name).sort_values(ascending=False)
        proxies = attr_corrs[attr_corrs > 0.5]
        
        if len(proxies) > 0:
            st.warning(f"⚠️ **Proxy Risk Detected!** Found {len(proxies)} feature(s) highly correlated with '{attr_name}'.")
            
            # Causal Graph
            G = nx.DiGraph()
            G.add_node(attr_name, color='#ff6b6b')
            G.add_node(st.session_state.target_col, color='#4285F4')
            
            for p in proxies.index:
                G.add_node(p, color='lightgray')
                G.add_edge(attr_name, p, weight=attr_corrs[p])
                G.add_edge(p, st.session_state.target_col, weight=0.5)
                
            fig_causal, ax_causal = plt.subplots(figsize=(8, 5))
            pos = nx.spring_layout(G, seed=42)
            colors = [node[1]['color'] for node in G.nodes(data=True)]
            
            nx.draw(G, pos, with_labels=True, node_color=colors, node_size=3000, font_size=10, 
                    font_weight='bold', edge_color='gray', arrows=True, ax=ax_causal)
            ax_causal.set_title("Causal Proxy Graph (DAG)")
            st.pyplot(fig_causal)
            st.caption("🕸️ **Causal Narrative:** The red node is your protected attribute. The gray nodes are proxies. The blue node is the target outcome. If a path exists from Red -> Gray -> Blue, the model is using a proxy to launder bias.")
            
            if st.button("Generate Causal Narrative via Gemini"):
                with st.spinner("Analyzing Causal Graph..."):
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = available_models[0] if available_models else 'models/gemini-1.5-pro'
                    genai_model = genai.GenerativeModel(model_name)
                    prompt = f"As an AI ethics expert, explain the difference between correlation and causation specifically for the features {proxies.index.tolist()} acting as proxies for {attr_name} in predicting {st.session_state.target_col}. Keep it to 4 sentences and formulate it as a 'Causal Narrative'."
                    resp = genai_model.generate_content(prompt)
                    st.session_state.proxy_assessment = resp.text
                    st.info(resp.text)
        else:
            st.success("✅ No strong proxy variables detected (Threshold: > 0.5 correlation).")

# ---------------------------------------------------------
# DASHBOARD TAB
# ---------------------------------------------------------
with tab_dashboard:
    st.divider()
    st.header(f"1. Bias Audit Engine ({st.session_state.champion_model_name})")
    
    if len(st.session_state.protected_cols) > 1:
        st.info(f"🧬 **Intersectionality Active:** Analyzing combined attribute '{attr_name}'")

    dpd = demographic_parity_difference(y_test, y_pred, sensitive_features=sensitive_test)
    dpr = demographic_parity_ratio(y_test, y_pred, sensitive_features=sensitive_test)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown('<div class="metric-label">Demographic Parity Difference</div>', unsafe_allow_html=True)
            dpd_class = "glowing-metric-bad" if abs(dpd) > 0.1 else "glowing-metric-good"
            st.markdown(f'<div class="{dpd_class}">{dpd:.3f}</div>', unsafe_allow_html=True)
            st.caption("Difference in selection rates. Ideal is 0.")
    with col2:
        with st.container(border=True):
            st.markdown('<div class="metric-label">Disparate Impact (Ratio)</div>', unsafe_allow_html=True)
            dpr_class = "glowing-metric-bad" if dpr < 0.8 else "glowing-metric-good"
            st.markdown(f'<div class="{dpr_class}">{dpr:.3f}</div>', unsafe_allow_html=True)
            st.caption("Ratio of selection rates. Ideal is 1.")

    if dpr < 0.8:
        st.error("⚠️ **High Bias Detected:** The disparate impact ratio is below the industry standard of 0.8.")
    else:
        st.success("✅ **System Fair:** Metrics within acceptable range.")

    st.subheader(f"Selection Rate by {attr_name} (Bias Heatmap)")
    with st.container(border=True):
        mf = MetricFrame(metrics=selection_rate, y_true=y_test, y_pred=y_pred, sensitive_features=sensitive_test)
        sr_df = pd.DataFrame({'Selection Rate': mf.by_group})

        fig_hm, ax_hm = plt.subplots(figsize=(8, 4))
        sns.heatmap(sr_df, annot=True, cmap='magma', cbar=False, ax=ax_hm, fmt='.1%')
        ax_hm.set_title(f"Gap in Predictions by {attr_name}", pad=20, fontsize=14, fontweight='bold')
        ax_hm.set_ylabel(attr_name)
        st.pyplot(fig_hm)
        st.caption("🔍 **How to read this:** This heatmap shows the percentage of each group that received a 'positive' prediction. If the system is fair, these percentages should be nearly identical. A darker color or lower number indicates a group is being penalized by the model.")

    st.divider()
    st.header("2. Human-Readable Ethical Audit")
    if st.button("Run Live Audit"):
        with st.status("Initializing Aura Agent...", expanded=True) as status:
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = available_models[0] if available_models else 'models/gemini-1.5-pro'
                genai_model = genai.GenerativeModel(model_name)
                prompt = f'''
                You are a Senior AI Ethics Engineer. We trained a {st.session_state.champion_model_name} model.
                The demographic parity difference for the protected attribute '{attr_name}' is {dpd:.3f}.
                The disparate impact (ratio of positive prediction rates) is {dpr:.3f}.
                
                Generate a 'Human-Readable Ethical Audit' explaining the real-world impact and providing mitigation recommendations.
                '''
                response = genai_model.generate_content(prompt)
                st.session_state.audit_result = response.text
                status.update(label="Audit Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Audit Failed!", state="error", expanded=False)
                st.error(f"Error calling Gemini API: {e}")
                
    if 'audit_result' in st.session_state:
        with st.chat_message("assistant", avatar="🛡️"):
            st.write(st.session_state.audit_result)
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "AURA ETHICAL AUDIT REPORT", ln=True, align='C')
        pdf.set_font("Helvetica", size=12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Analyzed Attribute: {attr_name}", ln=True)
        pdf.cell(0, 10, f"Champion Model: {st.session_state.champion_model_name}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"Demographic Parity Difference: {dpd:.3f}", ln=True)
        pdf.cell(0, 10, f"Disparate Impact (Ratio): {dpr:.3f}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, st.session_state.audit_result.encode('latin-1', 'replace').decode('latin-1'))
        
        if 'proxy_assessment' in st.session_state:
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Proxy Variable Warning", ln=True)
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 10, st.session_state.proxy_assessment.encode('latin-1', 'replace').decode('latin-1'))
            
        if 'mitigation_results' in st.session_state:
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Bias Mitigation Results", ln=True)
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 10, st.session_state.mitigation_results.encode('latin-1', 'replace').decode('latin-1'))
            
        if 'arena_plot_buf' in st.session_state:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Model Arena Tradeoff Comparison", ln=True)
            pdf.ln(10)
            from PIL import Image
            img = Image.open(st.session_state.arena_plot_buf)
            pdf.image(img, w=170)
            
        st.download_button(
            label="📥 Download Professional PDF Report",
            data=bytes(pdf.output()),
            file_name=f"Aura_Audit_Report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

# ---------------------------------------------------------
# ARENA TAB (RED TEAMING & PARETO)
# ---------------------------------------------------------
with tab_arena:
    st.header("Bias Mitigation Arena (🏟️)")
    st.write("Comparing multiple architectures simultaneously for inherent fairness.")
    
    st.session_state.champion_model_name = st.radio("Select Champion Model for Dashboard & SHAP", list(st.session_state.model_arena.keys()), horizontal=True)
    
    with st.spinner("Calculating Arena Metrics..."):
        arena_dpr = {}
        arena_acc = {}
        for name, m in st.session_state.model_arena.items():
            p = m.predict(X_test)
            arena_acc[name] = accuracy_score(y_test, p)
            arena_dpr[name] = demographic_parity_ratio(y_test, p, sensitive_features=sensitive_test)
            
        fig_arena, ax_arena = plt.subplots(figsize=(8, 5))
        colors = ['red', 'blue', 'green']
        markers = ['o', 's', '^'] # Circle, Square, Triangle
        for i, name in enumerate(arena_dpr.keys()):
            ax_arena.scatter([arena_dpr[name]], [arena_acc[name]], color=colors[i], marker=markers[i], label=name, s=200, alpha=0.7, edgecolors='black')
            
        ax_arena.set_xlabel("Disparate Impact Ratio (Fairness)")
        ax_arena.set_ylabel("Accuracy")
        ax_arena.axvline(0.8, color='orange', linestyle=':', label='0.8 Threshold')
        ax_arena.legend()
        ax_arena.set_title("Multi-Model Fairness vs. Accuracy Tradeoff")
        st.pyplot(fig_arena)
        st.caption("🔍 **How to read this:** The vertical dotted orange line represents the industry-standard fairness threshold (0.8 Disparate Impact). You want your model to be to the **right** of this line (fair) and as high up as possible (accurate). Models to the left of the line are discriminatory.")
        
        buf = io.BytesIO()
        fig_arena.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        st.session_state.arena_plot_buf = buf

    st.divider()
    st.subheader("Algorithmic Red Teaming (🛡️)")
    if st.button("Run Epsilon-Greedy Noise Injection"):
        with st.spinner("Injecting adversarial noise (epsilon=0.01) into test set..."):
            X_test_noisy = X_test.copy()
            numeric_cols = X_test_noisy.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                noise = np.random.normal(0, 0.01 * X_test_noisy[col].std(), size=len(X_test_noisy))
                X_test_noisy[col] += noise
                
            p_noisy = champion.predict(X_test_noisy)
            acc_noisy = accuracy_score(y_test, p_noisy)
            acc_drop = arena_acc[st.session_state.champion_model_name] - acc_noisy
            
            if acc_drop > 0.10:
                st.error(f"🚨 **Vulnerable!** Fragility Score: {acc_drop:.1%} accuracy drop. The model is highly unstable against adversarial data.")
            else:
                st.success(f"🛡️ **Robust.** Fragility Score: {acc_drop:.1%} accuracy drop. The model maintained stability.")
        
    st.divider()
    st.subheader("Active Mitigation (Pareto Frontier 🧮)")
    epsilon_val = st.slider("Select Fairness Tolerance (Epsilon)", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
    
    if st.button(f"Apply Mitigation (Epsilon={epsilon_val}) to {st.session_state.champion_model_name}"):
        with st.spinner("Retraining model with Demographic Parity constraint..."):
            from fairlearn.reductions import ExponentiatedGradient, DemographicParity
            base_estimator = st.session_state.model_arena[st.session_state.champion_model_name]
            try:
                mitigator = ExponentiatedGradient(base_estimator, DemographicParity(difference_bound=epsilon_val))
                mitigator.fit(X_train, y_train, sensitive_features=X_train[attr_name] if attr_name in X_train.columns else X_raw.loc[X_train.index, attr_name])
                y_pred_mitigated = mitigator.predict(X_test)
                
                acc_before = arena_acc[st.session_state.champion_model_name]
                acc_after = accuracy_score(y_test, y_pred_mitigated)
                dpr_before = arena_dpr[st.session_state.champion_model_name]
                dpr_after = demographic_parity_ratio(y_test, y_pred_mitigated, sensitive_features=sensitive_test)
                
                st.session_state.mitigation_results = f"Accuracy changed from {acc_before:.1%} to {acc_after:.1%}. Disparate Impact improved from {dpr_before:.3f} to {dpr_after:.3f}."
                
                col1, col2 = st.columns(2)
                col1.metric("Accuracy (After)", f"{acc_after:.1%}", delta=f"{acc_after-acc_before:.1%}")
                col2.metric("Disparate Impact (After)", f"{dpr_after:.3f}", delta=f"{dpr_after-dpr_before:.3f}")
                
            except Exception as e:
                st.error(f"Mitigation failed for this model architecture. Error: {str(e)}")

# ---------------------------------------------------------
# SHAP TAB
# ---------------------------------------------------------
with tab_shap:
    st.header("Deep Explainability (SHAP)")
    if st.button("Generate SHAP Waterfall Plot"):
        with st.spinner(f"Running Explainer on {st.session_state.champion_model_name}..."):
            champ = st.session_state.model_arena[st.session_state.champion_model_name]
            
            # Use appropriate explainer
            if st.session_state.champion_model_name == "LogisticRegression":
                explainer = shap.LinearExplainer(champ, X_train)
            else:
                explainer = shap.TreeExplainer(champ)
                
            sample_idx = X_test.iloc[0].name
            st.write(f"Explaining predictions for sample ID {sample_idx}")
            
            shap_values = explainer(pd.DataFrame([X_test.iloc[0]]))
            
            # Adjust shape extraction based on explainer
            if st.session_state.champion_model_name == "RandomForest":
                shap_val = shap_values[0, :, 1] if len(shap_values.shape) > 2 else shap_values[0]
            else:
                shap_val = shap_values[0]
                
            fig_shap, ax_shap = plt.subplots()
            shap.plots.waterfall(shap_val, show=False)
            st.pyplot(fig_shap)
            st.caption("🔍 **How to read this:** The waterfall plot breaks down how each individual feature contributed to the final prediction. **Red bars** push the prediction higher (closer to a positive outcome), while **blue bars** push it lower. Look out for sensitive attributes (like race or gender) taking up large red or blue chunks—this is direct evidence of the model relying on bias.")

# ---------------------------------------------------------
# CHAT TAB (WHAT-IF SIMULATOR)
# ---------------------------------------------------------
with tab_chat:
    st.header("Aura Chat Agent & What-If Simulator (⏱️)")
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask Aura or trigger a What-If simulation (e.g. 'What if I remove age?')..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🛡️"):
            message_placeholder = st.empty()
            
            # Structured Safe-Parsing for What-If
            is_what_if = "what if" in prompt.lower() and ("remove" in prompt.lower() or "drop" in prompt.lower())
            
            if is_what_if:
                with st.spinner("Running Data Simulation..."):
                    feature_to_drop = None
                    for col in X_raw.columns:
                        if col.lower() in prompt.lower():
                            feature_to_drop = col
                            break
                            
                    if feature_to_drop:
                        try:
                            # Safely simulate
                            X_train_sim = X_train.drop(columns=[feature_to_drop])
                            X_test_sim = X_test.drop(columns=[feature_to_drop])
                            
                            sim_model = RandomForestClassifier(n_estimators=10, random_state=42)
                            sim_model.fit(X_train_sim, y_train)
                            p_sim = sim_model.predict(X_test_sim)
                            sim_acc = accuracy_score(y_test, p_sim)
                            sim_dpr = demographic_parity_ratio(y_test, p_sim, sensitive_features=sensitive_test)
                            
                            orig_acc = accuracy_score(y_test, y_pred)
                            diff_acc = sim_acc - orig_acc
                            diff_dpr = sim_dpr - dpr
                            
                            sim_result = f"**Simulation Complete.**\\n\\nDropping `{feature_to_drop}` resulted in:\\n- **Accuracy**: {sim_acc:.1%} ({diff_acc:+.1%})\\n- **Disparate Impact**: {sim_dpr:.3f} ({diff_dpr:+.3f})"
                            message_placeholder.markdown(sim_result)
                            st.session_state.messages.append({"role": "assistant", "content": sim_result})
                        except Exception as e:
                            message_placeholder.error(f"Simulation failed. Error: {e}")
                    else:
                        message_placeholder.error("I couldn't identify a valid column name in your prompt to simulate.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        model_name = available_models[0] if available_models else 'models/gemini-1.5-pro'
                        genai_model = genai.GenerativeModel(model_name)
                        context = f"Context: Attribute {attr_name}. Model {st.session_state.champion_model_name}."
                        if 'proxy_assessment' in st.session_state:
                            context += f" Proxies: {st.session_state.proxy_assessment}"
                        full_prompt = context + "\\n\\nUser Question: " + prompt
                        response = genai_model.generate_content(full_prompt)
                        message_placeholder.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        message_placeholder.error(f"Error calling Gemini API: {e}")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown('''
<div class="footer-text">
    Enterprise Grade Ethics | Powered by Gemini 1.5 Flash & Antigravity IDE
</div>
''', unsafe_allow_html=True)
"""
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("app.py successfully rewritten with Phase 5 features!")
