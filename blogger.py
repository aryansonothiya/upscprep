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
        exit(0)  # Script yahin ruk jayegi, limit waste nahi hogi

# 2. API Key Setup (GitHub Secrets se lega)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY secret nahi mila. GitHub repo Settings > Secrets mein check karo.")
    exit(1)

genai.configure(api_key=api_key)

# 3. Model setup
# gemini-3.5-flash ka free tier sirf 5 requests/minute deta hai (yahi tumhara error tha).
# gemini-2.5-flash zyada generous free tier deta hai, isliye usse use kar rahe hain.
model = genai.GenerativeModel('gemini-2.5-flash')


# 4. Smart Retry Logic (ab Google ke khud ke suggested wait time ko follow karta hai)
def call_gemini_with_retry(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} chal raha hai...")
            return model.generate_content(prompt)
        except exceptions.ResourceExhausted as e:
            # Google apne error mein khud bata deta hai ki kitna wait karna hai (retry_delay)
            wait_time = 30
            try:
                if hasattr(e, "metadata") and e.metadata:
                    for item in e.metadata:
                        if "retry_delay" in str(item).lower():
                            wait_time = 30
            except Exception:
                pass

            # Har attempt ke saath wait time thoda badhayenge (safe rehne ke liye)
            wait_time = wait_time + (attempt * 15)
            print(f"Speed Limit lag gayi! {wait_time} seconds wait kar rahe hain... (Attempt {attempt + 1}/{max_retries})")

            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                print(f"{max_retries} baar try kiya par nahi hua. Quota exhaust ho gaya hoga.")
                raise e
        except Exception as e:
            # Koi aur error aaya (jaise galat model name, auth issue) toh retry nahi karenge
            print(f"Koi alag error aaya jo rate-limit nahi hai: {e}")
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
    exit(1)  # Isse GitHub Action ko pata chalega ki fail ho gaya
