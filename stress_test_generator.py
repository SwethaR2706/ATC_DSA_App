import firebase_admin
from firebase_admin import credentials, firestore
import time
import random
from datetime import datetime

# Initialize Firebase (Reuse existing logic or simplified)
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        exit(1)

db = firestore.client()

NUM_SUBMISSIONS = 250

def generate_submissions():
    print(f"Starting Stress Test Generation: {NUM_SUBMISSIONS} submissions...")
    start_time = time.time()
    
    batch = db.batch()
    count = 0
    total_created = 0
    
    for i in range(NUM_SUBMISSIONS):
        # Randomize Data
        q_id = random.randint(1, 10)
        lang = random.choice(['python', 'java'])
        
        # 10% chance of "Infinite Loop" code
        if random.random() < 0.1:
            code = "while True: pass"
            c_type = "Infinite Loop"
        else:
            code = "print('Hello World')"
            c_type = "Normal"
            
        # Participant Data (For Dashboard)
        user_id = f"stress-user-{random.randint(100, 999)}"
        doc_ref = db.collection('submissions').document()
        
        data = {
            "participant_id": user_id,
            "problem_id": q_id,
            "language": lang,
            "code": code,
            "status": "pending",
            "type": random.choice(["run", "submit"]), 
            "submitted_at": firestore.SERVER_TIMESTAMP,
            "stress_test": True 
        }
        
        batch.set(doc_ref, data)
        
        # Also create Participant so they show on Dashboard
        part_ref = db.collection('participants').document(user_id)
        part_data = {
            "name": f"Stress User {user_id.split('-')[-1]}",
            "email": f"{user_id}@fake.com",
            "score": 0,
            "solved": [],
            "status": "ACTIVE",
            "violations": 0,
            "start_time": firestore.SERVER_TIMESTAMP
        }
        batch.set(part_ref, part_data)
        
        count += 1
        
        # Commit batches of 50 (x2 ops = 100 ops, well within 500 limit)
        if count >= 50:
            batch.commit()
            total_created += count
            print(f"   -> Committed {total_created} submissions...")
            batch = db.batch() # New batch
            count = 0
            
    if count > 0:
        batch.commit()
        total_created += count
        
    duration = time.time() - start_time
    print(f"✅ GENERATION COMPLETE")
    print(f"Total: {total_created} submissions")
    print(f"Time: {duration:.2f} seconds")
    print(f"Rate: {total_created/duration:.2f} subs/sec")

if __name__ == "__main__":
    generate_submissions()
