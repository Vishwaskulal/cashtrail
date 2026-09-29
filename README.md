# CashTrail

## Purpose
Predictive cybercrime intelligence prototype.
CashTrail is a prototype predictive analytics platform for cybercrime complaints. It analyzes historical/synthetic cybercrime and financial transaction patterns and predicts potential cash-withdrawal risk locations. The system will provide risk scores, GIS visualization, alerts, and investigation support for authorized stakeholders.

**IMPORTANT NOTE:**
This is a DEMONSTRATION PROTOTYPE, not a production system.
- Uses only synthetic/anonymized data during development.
- Does not track live GPS locations of scammers.
- Predictions are potential/high-risk locations with risk scores and confidence, not guaranteed actual withdrawal locations.

## Current status
Step 1 — Project Foundation

## Technology stack
- **Frontend:** React.js, Vite, JavaScript, React Router, Axios, Tailwind CSS
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic
- **Database:** MySQL
- **ML (Future):** Python, Pandas, NumPy, Scikit-learn, XGBoost, SHAP
- **GIS (Future):** Leaflet, OpenStreetMap

## Local development commands

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Backend:
```bash
cd backend
python -m venv venv

# Windows activation:
venv\Scripts\activate

# Install dependencies:
pip install -r requirements.txt

# Run backend:
uvicorn app.main:app --reload
```

## Future Implementation Steps
1. Database schema
2. Synthetic dataset
3. ML model
4. Prediction API
5. GIS risk map
6. Alert system
7. Investigation interface
8. Full frontend-backend integration
