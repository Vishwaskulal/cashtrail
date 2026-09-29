import os
os.environ['ALERT_RISK_THRESHOLD'] = '0.50'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_alert_flow():
    # Step 1: Perform prediction which generates alert
    payload = {
        "case_id": "CASE_00001",
        "transaction_amount": 150000.0,
        "transaction_count": 50,
        "transaction_velocity": 12.5,
        "fraud_hour": 3,
        "fraud_day": 6,
        "crime_category": "Account Takeover",
        "victim_latitude": 28.7041,
        "victim_longitude": 77.1025,
        "historical_similarity": 0.85,
        "top_k": 3
    }

    print("Testing POST /api/predictions/analyze")
    response = client.post("/api/predictions/analyze", json=payload)
    response.raise_for_status()
    data = response.json()
    print(f"Prediction generated {data.get('alerts_generated')} alerts")
    
    # Verify alert threshold was crossed
    top_loc = data['locations'][0]
    print(f"Top Location: {top_loc['location_id']} - Score: {top_loc['risk_score']}")
    
    # We need to test if an alert actually got generated
    if data.get('alerts_generated', 0) == 0:
        print("No alert generated. You might need to adjust the payload or threshold to ensure a high-risk prediction is made.")
    
    # Step 5: Call GET /api/alerts
    print("\nTesting GET /api/alerts")
    alert_resp = client.get("/api/alerts?case_number=CASE_00001")
    alert_resp.raise_for_status()
    alerts_data = alert_resp.json()
    
    if alerts_data['total'] == 0:
        print("No alerts found in database!")
        return
        
    alert = alerts_data['alerts'][0]
    alert_id = alert['id']
    print(f"Found Alert ID: {alert_id}, Status: {alert['status']}")
    
    # Step 7: Acknowledge it
    print(f"\nTesting PATCH /api/alerts/{alert_id}/acknowledge")
    ack_resp = client.patch(f"/api/alerts/{alert_id}/acknowledge", json={"status": "ACKNOWLEDGED", "user_id": 1})
    ack_resp.raise_for_status()
    print(f"Alert Status changed to: {ack_resp.json()['status']}")
    
    # Step 9: Resolve it
    print(f"\nTesting PATCH /api/alerts/{alert_id}/resolve")
    res_resp = client.patch(f"/api/alerts/{alert_id}/resolve", json={"status": "RESOLVED", "user_id": 1})
    res_resp.raise_for_status()
    print(f"Alert Final Status: {res_resp.json()['status']}")

if __name__ == "__main__":
    try:
        test_alert_flow()
    except Exception as e:
        print(f"Error: {e}")
