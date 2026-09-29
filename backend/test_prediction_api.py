import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_model_status():
    print("Testing /api/predictions/model-status")
    response = client.get("/api/predictions/model-status")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True
    print("OK\n")

def test_analyze_case():
    print("Testing POST /api/predictions/analyze")
    # Synthetic case features
    payload = {
        "case_id": "CASE_00001",
        "transaction_amount": 15000.0,
        "transaction_count": 5,
        "transaction_velocity": 1.2,
        "fraud_hour": 14,
        "fraud_day": 3,
        "crime_category": "UPI_FRAUD",
        "victim_latitude": 12.9716,
        "victim_longitude": 77.5946,
        "historical_similarity": 0.85,
        "top_k": 3
    }
    
    response = client.post("/api/predictions/analyze", json=payload)
    if response.status_code != 200:
        print("Error:", response.json())
        
    assert response.status_code == 200
    data = response.json()
    print("Overall Risk Level:", data["overall_risk_level"])
    print(f"Returned {len(data['locations'])} locations")
    print("Top Prediction:", data["locations"][0]["location_name"], "- Score:", data["locations"][0]["risk_score"])
    print("OK\n")

def test_get_prediction():
    print("Testing GET /api/predictions/CASE_00001")
    response = client.get("/api/predictions/CASE_00001")
    assert response.status_code == 200
    data = response.json()
    print(f"Retrieved {len(data['locations'])} locations for case", data["case_id"])
    print("OK\n")

if __name__ == "__main__":
    test_model_status()
    test_analyze_case()
    test_get_prediction()
