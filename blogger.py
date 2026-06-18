import google.generativeai as genai
import os
import time
from datetime import datetime
from google.api_core import exceptions

# 1. Caching: Check karte hain ki kya aaj ka article pehle hi ban chuka hai?
if os.path.exists("content.md"):
    file_time = datetime.fromtimestamp(os.path.getmtime("content.md")).date()
    today = datetime.today().date()
    
    if file_time == today:
        print("Caching Check: Aaj ka article pehle hi ban chuka hai! API call bacha li gayi.")
        exit(0) # Script yahin ruk jayegi, limit waste nahi hogi

# 2. API Key Setup (GitHub Secrets se lega)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 3. Model setup
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. Tumhara "Smart Retry" Logic
def call_gemini_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} chal raha hai...")
            return model.generate_content(prompt)
        except exceptions.ResourceExhausted as e:
            print(f"Speed Limit lag gayi! 30 seconds wait kar rahe hain...")
            if attempt < max_retries - 1:
                time.sleep(30) # 30 seconds aaram karega
            else:
                print("Teen baar try kiya par nahi hua.")
                raise e

# 5. Content Generate Karo
topic = "Impact of AI in UPSC Civil Services Preparation"
prompt = f"Write a detailed 500-word UPSC editorial style article on {topic}. Include headings, subheadings, and a conclusion."

try:
    print("Content generation shuru kar rahe hain...")
    response = call_gemini_with_retry(prompt)
    
    # 6. File mein save karo
    with open("content.md", "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(response.text)
        
    print("Success! 'content.md' file ban gayi hai aur ready hai.")

except Exception as e:
    print(f"\n--- ERROR AAYA HAI ---")
    print(e)
    print(f"----------------------")
    exit(1) # Isse GitHub Action ko pata chalega ki fail ho gaya
