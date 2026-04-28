# Aura: The Ethical Lens ✨

Aura is a web application that detects and explains gender bias in automated decision-making systems. It serves as an interactive platform for the 2026 Google Solution Challenge, directly aligning with UN SDG Goal 10 (Reduced Inequalities).

## Overview

Aura uses the UCI Adult Census dataset to train a predictive model for income classification (>50K or <=50K). It then performs a comprehensive bias audit to identify disparities in how different demographic groups (specifically, gender) are treated by the model. 

Crucially, Aura integrates **Gemini 1.5 Flash** for Explainable AI (XAI) to provide human-readable ethical audits, transforming raw bias metrics into understandable narratives with actionable mitigation recommendations.

## Features

- **Live Bias Audit Engine**: Calculates Demographic Parity Difference and Disparate Impact.
- **Bias Heatmap**: Visualizes the gap in high-income predictions across genders using a clear `magma` color palette.
- **Explainable AI (XAI)**: Uses Gemini to generate an "Ethical Audit" that explains the real-world impact of the model's biases on social equality.
- **Counterfactual Comparison**: Demonstrates how changing just the gender of a given profile alters the model's prediction, directly exposing algorithmic bias.
- **Model Transparency Card**: Generates a dynamic summary of the dataset's historical limitations and fairness benchmarks.

## Installation

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### Setup
1. Clone this repository or download the source code.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The main dependencies are streamlit, pandas, matplotlib, seaborn, scikit-learn, fairlearn, and google-generativeai).*

## Usage

Run the Streamlit application locally:
```bash
streamlit run app.py
```

Once the application launches in your browser:
1. Enter your **Gemini API Key** in the sidebar.
2. Review the calculated bias metrics and the heatmap.
3. Click **Run Live Audit** to receive an AI-generated ethical consultation.
4. Experiment with the **Counterfactual Comparison** and generate the **Model Transparency Card**.

## Agentic Workflow and UN SDG Goal 10

This tool was built using an advanced agentic workflow, leveraging the AI assistant *Antigravity* to rapidly prototype a full-stack ethical AI platform. 

Aura directly addresses **UN SDG Goal 10: Reduced Inequalities** by:
1. **Detecting Systemic Bias**: Shining a light on historical inequalities embedded in data.
2. **Fostering Accountability**: Translating opaque metrics into actionable recommendations via Explainable AI.
3. **Promoting Fair Systems**: Encouraging developers to mitigate bias before deploying decision-making systems.

---
*Built for the 2026 Google Solution Challenge.*
