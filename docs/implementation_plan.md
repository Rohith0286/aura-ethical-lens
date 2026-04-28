# Aura: The Ethical Lens - Implementation Plan

Building a web application that detects and explains gender bias in automated decision-making using the UCI Adult Census dataset, aligning with UN SDG Goal 10 (Reduced Inequalities).

## User Review Required

> [!IMPORTANT]
> The app will require a Google Gemini API key to function. The user must have an environment variable `GEMINI_API_KEY` set, or be able to input it via the Streamlit UI. Please confirm how you'd like to provide the API key (e.g., via `.env` file, system env var, or a text input in the app itself).

## Open Questions

> [!WARNING]
> Do you have a preference for the project directory name? I will use `C:\Users\rohit\.gemini\antigravity\scratch\aura_ethical_lens` by default.

## Proposed Changes

### Project Setup
- Create project directory `C:\Users\rohit\.gemini\antigravity\scratch\aura_ethical_lens`.
- Initialize a `requirements.txt` with `streamlit`, `pandas`, `matplotlib`, `fairlearn`, `google-generativeai`, `scikit-learn` (needed for training a simple model to audit), `seaborn` (for the heatmap visualization).
- Create a Python virtual environment and install dependencies.

### Application Logic
#### [NEW] `app.py`
- Load the Adult Census dataset using `fairlearn.datasets.fetch_adult()`.
- Preprocess data and train a simple model (e.g., Logistic Regression or Random Forest) to predict high income.
- Calculate bias metrics: Demographic Parity Difference and Disparate Impact using `fairlearn.metrics` focusing on the 'sex' attribute.
- Generate a Bias Heatmap visualization showing the gap in high-income predictions.
- Integrate `google-generativeai` (Gemini 1.5 Flash) to generate a Human-Readable Ethical Audit based on the metrics.
- Build the Streamlit UI with the following features:
  - **Run Live Audit**: Button to trigger calculations and AI audit.
  - **Counterfactual Comparison**: UI to compare 'Male' vs 'Female' profile with identical stats.
  - **Mitigation Recommendation**: Display Gemini's advice on bias mitigation.

### Documentation
#### [NEW] `README.md`
- Explain the Agentic Workflow used to build this tool.
- Detail how the tool addresses systemic bias and aligns with UN SDG Goal 10.
- Provide instructions for running the application locally.

## Verification Plan

### Automated Tests
- None planned for this phase.

### Manual Verification
- Run the Streamlit app locally using `streamlit run app.py`.
- Verify the dataset loads correctly.
- Ensure the bias metrics are calculated and displayed.
- Test the Gemini integration by running a live audit and checking the generated explanations.
- Test the counterfactual comparison tool.
