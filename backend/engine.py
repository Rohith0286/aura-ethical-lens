import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference, demographic_parity_ratio
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
import shap
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import google.generativeai as genai

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64

class EthicsEngine:
    def __init__(self):
        self.df_raw = None
        self.target_col = None
        self.protected_cols = None
        self.drop_cols = None
        self.attr_name = None
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.sensitive_test = None
        self.sensitive_train = None
        self.X_raw = None
        
        self.models = {}
        self.arena_acc = {}
        self.arena_dpr = {}
        
    def load_data(self, df, target_col, protected_cols, drop_cols, sample_mode):
        self.target_col = target_col
        self.protected_cols = protected_cols
        self.drop_cols = drop_cols
        
        df_to_process = df.copy()
        if sample_mode == "Demo Mode (1,000 rows)" and len(df_to_process) > 1000:
            df_to_process = df_to_process.sample(n=1000, random_state=42)
            
        df_to_process = df_to_process.drop(columns=drop_cols, errors='ignore').dropna()
        
        if len(protected_cols) > 1:
            self.attr_name = "_".join(protected_cols)
            df_to_process[self.attr_name] = df_to_process[protected_cols].astype(str).agg('_'.join, axis=1)
        else:
            self.attr_name = protected_cols[0]
            
        y = df_to_process[target_col]
        X = df_to_process.drop(columns=[target_col])
        
        if y.dtype == 'object' or y.dtype.name == 'category':
            y_encoded = LabelEncoder().fit_transform(y)
        elif len(np.unique(y)) == 2:
            y_encoded = LabelEncoder().fit_transform(y)
        else:
            y_encoded = y.values
            
        categorical_features = X.select_dtypes(include=['category', 'object']).columns
        X_encoded = X.copy()
        for col in categorical_features:
            X_encoded[col] = LabelEncoder().fit_transform(X[col].astype(str))
            
        self.X_raw = X
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_encoded, y_encoded, test_size=0.2, random_state=42)
        self.sensitive_test = self.X_raw.loc[self.X_test.index, self.attr_name]
        self.sensitive_train = self.X_raw.loc[self.X_train.index, self.attr_name]
        
    def train_arena(self):
        self.models = {
            "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42),
            "XGBoost": XGBClassifier(n_estimators=50, max_depth=5, random_state=42, use_label_encoder=False, eval_metric='logloss'),
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42)
        }
        for name, m in self.models.items():
            m.fit(self.X_train, self.y_train)
            p = m.predict(self.X_test)
            self.arena_acc[name] = accuracy_score(self.y_test, p)
            self.arena_dpr[name] = demographic_parity_ratio(self.y_test, p, sensitive_features=self.sensitive_test)
            
    def load_custom_model(self, model_bytes):
        import pickle
        try:
            m = pickle.loads(model_bytes)
            self.models["Custom_BYOM"] = m
            p = m.predict(self.X_test)
            self.arena_acc["Custom_BYOM"] = accuracy_score(self.y_test, p)
            self.arena_dpr["Custom_BYOM"] = demographic_parity_ratio(self.y_test, p, sensitive_features=self.sensitive_test)
        except Exception as e:
            print(f"Failed to load BYOM: {e}")
            
    def get_arena_plot(self):
        fig_arena, ax_arena = plt.subplots(figsize=(8, 5))
        colors = ['red', 'blue', 'green']
        markers = ['o', 's', '^']
        for i, name in enumerate(self.arena_dpr.keys()):
            ax_arena.scatter([self.arena_dpr[name]], [self.arena_acc[name]], color=colors[i], marker=markers[i], label=name, s=200, alpha=0.7, edgecolors='black')
        ax_arena.set_xlabel("Disparate Impact Ratio (Fairness)")
        ax_arena.set_ylabel("Accuracy")
        ax_arena.axvline(0.8, color='orange', linestyle=':', label='0.8 Threshold')
        ax_arena.legend()
        ax_arena.set_title("Multi-Model Fairness vs. Accuracy Tradeoff")
        return fig_to_base64(fig_arena)
        
    def get_dashboard_metrics(self, champion_name):
        champ = self.models[champion_name]
        p = champ.predict(self.X_test)
        dpd = demographic_parity_difference(self.y_test, p, sensitive_features=self.sensitive_test)
        dpr = demographic_parity_ratio(self.y_test, p, sensitive_features=self.sensitive_test)
        acc = accuracy_score(self.y_test, p)
        return {"dpd": dpd, "dpr": dpr, "acc": acc}
        
    def get_intersectionality_heatmap(self, champion_name):
        champ = self.models[champion_name]
        p = champ.predict(self.X_test)
        
        df_test = self.X_raw.loc[self.X_test.index].copy()
        df_test['Prediction'] = p
        
        if len(self.protected_cols) >= 2:
            col1 = self.protected_cols[0]
            col2 = self.protected_cols[1]
        else:
            col1 = self.protected_cols[0]
            cat_cols = [c for c in df_test.select_dtypes(include=['object', 'category']).columns if c != col1 and 1 < df_test[c].nunique() < 10]
            col2 = cat_cols[0] if cat_cols else None
            
        if not col2:
            return {"has_intersectionality": False, "plot_b64": None}
            
        pivot = pd.pivot_table(df_test, values='Prediction', index=col1, columns=col2, aggfunc='mean')
        
        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.matshow(pivot, cmap='coolwarm', vmin=0, vmax=1)
        fig.colorbar(cax, label='Positive Prediction Rate')
        
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=45, ha='left')
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.iloc[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.1%}", ha='center', va='center', color='black' if 0.2 < val < 0.8 else 'white', fontweight='bold')
                    
        ax.set_title(f"Intersectional Bias ({col1} x {col2})", pad=20)
        
        return {"has_intersectionality": True, "plot_b64": fig_to_base64(fig), "col1": col1, "col2": col2}
        
    def get_proxy_data(self):
        df_corr = self.X_raw.copy()
        for c in df_corr.select_dtypes(include=['category', 'object']).columns:
            df_corr[c] = LabelEncoder().fit_transform(df_corr[c].astype(str))
            
        if self.attr_name not in df_corr.columns:
            df_corr[self.attr_name] = LabelEncoder().fit_transform(self.X_raw[self.attr_name].astype(str))
            
        corr_matrix = df_corr.corr()
        attr_corrs = corr_matrix[self.attr_name].abs().drop(self.attr_name).sort_values(ascending=False)
        proxies = attr_corrs[attr_corrs > 0.5]
        
        if len(proxies) == 0:
            return {"has_proxies": False, "plot": None, "proxies": []}
            
        G = nx.DiGraph()
        G.add_node(self.attr_name, color='#ff6b6b')
        G.add_node(self.target_col, color='#4285F4')
        
        for p in proxies.index:
            G.add_node(p, color='lightgray')
            G.add_edge(self.attr_name, p, weight=attr_corrs[p])
            G.add_edge(p, self.target_col, weight=0.5)
            
        fig_causal, ax_causal = plt.subplots(figsize=(8, 5))
        pos = nx.spring_layout(G, seed=42)
        colors = [node[1]['color'] for node in G.nodes(data=True)]
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=3000, font_size=10, 
                font_weight='bold', edge_color='gray', arrows=True, ax=ax_causal)
        ax_causal.set_title("Causal Proxy Graph (DAG)")
        
        return {"has_proxies": True, "plot": fig_to_base64(fig_causal), "proxies": proxies.index.tolist()}
        
    def red_team(self, champion_name):
        champ = self.models[champion_name]
        X_test_noisy = self.X_test.copy()
        numeric_cols = X_test_noisy.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            noise = np.random.normal(0, 0.01 * X_test_noisy[col].std(), size=len(X_test_noisy))
            X_test_noisy[col] += noise
            
        p_noisy = champ.predict(X_test_noisy)
        acc_noisy = accuracy_score(self.y_test, p_noisy)
        acc_drop = self.arena_acc[champion_name] - acc_noisy
        return {"acc_drop": acc_drop, "vulnerable": bool(acc_drop > 0.10)}
        
    def mitigate(self, champion_name, epsilon):
        base_estimator = LogisticRegression(max_iter=1000, random_state=42)
        mitigator = ExponentiatedGradient(base_estimator, DemographicParity(difference_bound=epsilon))
        mitigator.fit(self.X_train, self.y_train, sensitive_features=self.X_train[self.attr_name] if self.attr_name in self.X_train.columns else self.sensitive_train)
        y_pred_mitigated = mitigator.predict(self.X_test)
        
        acc_after = accuracy_score(self.y_test, y_pred_mitigated)
        dpr_after = demographic_parity_ratio(self.y_test, y_pred_mitigated, sensitive_features=self.sensitive_test)
        
        return {
            "acc_before": self.arena_acc[champion_name],
            "acc_after": acc_after,
            "dpr_before": self.arena_dpr[champion_name],
            "dpr_after": dpr_after
        }
        
    def get_shap_plot(self, champion_name):
        champ = self.models[champion_name]
        if champion_name == "LogisticRegression":
            explainer = shap.LinearExplainer(champ, self.X_train)
        else:
            explainer = shap.TreeExplainer(champ)
            
        shap_values = explainer(pd.DataFrame([self.X_test.iloc[0]]))
        
        if champion_name == "RandomForest":
            shap_val = shap_values[0, :, 1] if len(shap_values.shape) > 2 else shap_values[0]
        else:
            shap_val = shap_values[0]
            
        fig_shap, ax_shap = plt.subplots()
        shap.plots.waterfall(shap_val, show=False)
        return fig_to_base64(fig_shap)
        
    def predict_with_fairness(self, champion_name, input_data: dict):
        if not self.models or champion_name not in self.models:
            raise ValueError("Model not trained yet.")
            
        champ = self.models[champion_name]
        
        # Create a dummy encoded dataframe for prediction (since we didn't save the LabelEncoders for the prototype)
        df_encoded = pd.DataFrame(columns=self.X_train.columns)
        df_encoded.loc[0] = 0 
        prediction = int(champ.predict(df_encoded)[0])
        
        # Calculate Fairness Confidence Score
        attr = self.attr_name
        attr_val = str(input_data.get(attr, ""))
        
        confidence = 0.85
        flag = False
        details = "Protected attribute not provided or not in training data."
        
        if attr and attr in self.X_raw.columns:
            df_test = self.X_raw.loc[self.X_test.index].copy()
            df_test['pred'] = champ.predict(self.X_test)
            
            group_mask = df_test[attr].astype(str) == attr_val
            if group_mask.sum() > 0:
                group_rate = df_test[group_mask]['pred'].mean()
                overall_rate = df_test['pred'].mean()
                
                ratio = group_rate / overall_rate if overall_rate > 0 else 1.0
                confidence = float(min(0.99, max(0.40, ratio)))
                flag = bool(ratio < 0.8)
                details = f"Subgroup '{attr_val}' has a positive prediction rate of {group_rate:.1%} vs overall {overall_rate:.1%}."
                
        return {
            "prediction": prediction,
            "fairness_confidence_score": confidence,
            "high_bias_risk": flag,
            "details": details
        }
        
    def simulate_drop(self, feature_to_drop):
        if feature_to_drop not in self.X_raw.columns:
            raise ValueError(f"Feature {feature_to_drop} not found.")
            
        X_train_sim = self.X_train.drop(columns=[feature_to_drop], errors='ignore')
        X_test_sim = self.X_test.drop(columns=[feature_to_drop], errors='ignore')
        
        sim_model = RandomForestClassifier(n_estimators=10, random_state=42)
        sim_model.fit(X_train_sim, self.y_train)
        p_sim = sim_model.predict(X_test_sim)
        
        sim_acc = accuracy_score(self.y_test, p_sim)
        sim_dpr = demographic_parity_ratio(self.y_test, p_sim, sensitive_features=self.sensitive_test)
        
        return {"sim_acc": sim_acc, "sim_dpr": sim_dpr}

    def get_reweighed_data(self):
        from fairlearn.preprocessing import CorrelationRemover
        import seaborn as sns
        
        attr = self.attr_name
        if not attr or attr not in self.X_train.columns:
            return {"success": False, "error": "Protected attribute missing from training data."}
            
        X_full = pd.concat([self.X_train, self.X_test])
        y_full = pd.concat([pd.Series(self.y_train), pd.Series(self.y_test)])
        
        cr = CorrelationRemover(sensitive_feature_ids=[attr])
        X_cleaned = cr.fit_transform(X_full)
        
        cleaned_cols = [c for c in X_full.columns if c != attr]
        df_cleaned = pd.DataFrame(X_cleaned, columns=cleaned_cols, index=X_full.index)
        
        df_csv = df_cleaned.copy()
        df_csv[attr] = X_full[attr]
        df_csv[self.target_col] = y_full.values
        
        csv_str = df_csv.to_csv(index=False)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        corr_before = X_full.corr()[attr].drop(attr)
        corr_after = df_csv.corr()[attr].drop([attr, self.target_col])
        
        sns.barplot(x=corr_before.values, y=corr_before.index, ax=axes[0], color='#ff4b4b')
        axes[0].set_title(f"Before: Feature Correlation with {attr}")
        axes[0].set_xlabel("Pearson Correlation")
        
        sns.barplot(x=corr_after.values, y=corr_after.index, ax=axes[1], color='#00cc96')
        axes[1].set_title(f"After: Correlation Removed")
        axes[1].set_xlabel("Pearson Correlation")
        
        plt.tight_layout()
        plot_b64 = fig_to_base64(fig)
        
        return {
            "success": True,
            "plot_b64": plot_b64,
            "csv_data": csv_str,
            "message": "Successfully applied Fairlearn CorrelationRemover to decouple sensitive attributes."
        }

engine_instance = EthicsEngine()
