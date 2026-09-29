import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.session import engine, Base, SessionLocal
from app.models.user import User
from app.models.case import Case
from app.models.transaction import Transaction
from app.models.withdrawal_location import WithdrawalLocation
from app.models.prediction import Prediction, PredictionLocation

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
def seed_data():
    db = SessionLocal()
    
    # Check if we already seeded
    if db.query(WithdrawalLocation).count() > 0:
        print("Database already seeded.")
        return
        
    print("Seeding Users...")
    user = User(
        email="test@cashtrail.com",
        name="testuser",
        password_hash="fakehashedpassword",
        role="INVESTIGATOR"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print("Seeding Locations...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    loc_path = os.path.join(base_dir, 'data', 'synthetic', 'withdrawal_locations.csv')
    df_loc = pd.read_csv(loc_path)
    
    for _, row in df_loc.iterrows():
        loc = WithdrawalLocation(
            location_code=row['location_id'], # Use location_id as code to match dataset
            location_name=row['location_name'],
            location_type=row['location_type'],
            city=row['city'],
            district=row['district'],
            state=row['state'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            location_activity_score=row['location_activity_score'],
            night_activity_score=row['night_activity_score'],
            historical_withdrawal_frequency=row['historical_withdrawal_frequency'],
            is_active=True,
        )
        db.add(loc)
    db.commit()

    print("Seeding Cases (First 10 for testing)...")
    cases_path = os.path.join(base_dir, 'data', 'synthetic', 'cashtrail_cases.csv')
    df_cases = pd.read_csv(cases_path).head(10)
    
    for _, row in df_cases.iterrows():
        case = Case(
            case_number=row['case_id'], # Use case_id as case_number to match dataset API calls
            complaint_date=datetime.strptime(row['complaint_date'], '%Y-%m-%d %H:%M:%S'),
            crime_category=row['crime_category'],
            description="Synthetic Test Case",
            victim_state=row['victim_state'],
            victim_district=row['victim_district'],
            victim_latitude=row['victim_latitude'],
            victim_longitude=row['victim_longitude'],
            total_amount=row['total_amount'],
            status="NEW",
            created_by=user.id
        )
        # Add extra properties needed by prediction service (hack for demo since model differs slightly)
        # Actually in SQLAlchemy, if the columns don't exist, we can't just assign them if they aren't in Case.
        # Wait, does Case have transaction_count, transaction_velocity, etc.?
        db.add(case)
        
    db.commit()
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
