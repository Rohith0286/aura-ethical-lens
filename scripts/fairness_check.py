import requests
import sys

API_URL = "http://localhost:8000/api/v1"
CHAMPION_MODEL = "RandomForest"

def check_fairness():
    try:
        print(f"Pinging Aura Backend to audit champion model: {CHAMPION_MODEL}...")
        res = requests.get(f"{API_URL}/dashboard?champion={CHAMPION_MODEL}")
        if res.status_code != 200:
            print(f"Error connecting to backend: {res.text}")
            sys.exit(1)
            
        data = res.json()
        dpr = data.get("dpr", 0)
        dpd = data.get("dpd", 0)
        
        print(f"Disparate Impact Ratio: {dpr:.3f}")
        print(f"Demographic Parity Difference: {dpd:.3f}")
        
        if dpr < 0.8:
            print("\n[BLOCKED] MODEL IS BIASED! Disparate Impact Ratio is below the 0.8 legal threshold.")
            print("Action Required: Please use the Active Mitigation features in the Aura Dashboard before merging.")
            sys.exit(1)
        else:
            print("\n[APPROVED] Model passes the 0.8 Disparate Impact threshold.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Failed to execute fairness check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_fairness()
