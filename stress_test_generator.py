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

NUM_SUBMISSIONS = 300

def generate_submissions():
    print(f"Starting Stress Test Generation: {NUM_SUBMISSIONS} submissions...")
    start_time = time.time()
    
    batch = db.batch()
    count = 0
    total_created = 0
    
    # VALID SOLUTIONS DICTIONARY (Python)
    SOLUTIONS = {
        1: """def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []""",
        2: """def solution(s):
    return s[::-1]""", # Simplified pythonic reverse
        3: """def solution(s):
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]""",
        4: """def solution(nums, target):
    import bisect
    idx = bisect.bisect_left(nums, target)
    if idx < len(nums) and nums[idx] == target:
        return idx
    return -1""",
        5: """def solution(nums):
    current_sum = nums[0]
    max_sum = nums[0]
    for i in range(1, len(nums)):
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)
    return max_sum""",
        6: """def solution(s):
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map:
            left = max(left, char_map[s[right]] + 1)
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len""",
        7: """def solution(height):
    if not height: return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water""",
        8: """def solution(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]""",
        9: """def solution(lists):
    merged = []
    for sublist in lists:
        for item in sublist:
            merged.append(item)
    merged.sort()
    return merged""",
        10: """from collections import deque
def solution(nums, k):
    q = deque()
    result = []
    for i in range(len(nums)):
        while q and nums[q[-1]] <= nums[i]:
            q.pop()
        q.append(i)
        if q[0] == i - k:
            q.popleft()
        if i >= k - 1:
            result.append(nums[q[0]])
    return result"""
    }

    for i in range(NUM_SUBMISSIONS):
        rand_val = random.random()
        
        # 98% -> PASSING (Valid Solution for Random Problem)
        if rand_val < 0.98:
             q_id = random.randint(1, 10)
             lang = 'python'
             code = SOLUTIONS[q_id]
             c_type = "submit"
             
        # 2% -> ERROR (To show red on dashboard)
        else:
             q_id = random.randint(1, 10)
             lang = 'python'
             code = "print('Error me')"
             c_type = "submit"
        
        # Participant Data (For Dashboard)
        user_id = f"stress-user-{random.randint(100, 999)}"
        doc_ref = db.collection('submissions').document()
        
        data = {
            "participant_id": user_id,
            "problem_id": q_id,
            "language": lang,
            "code": code,
            "status": "pending",
            "type": c_type, 
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
