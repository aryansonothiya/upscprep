from google import genai
from google.genai import errors
import os
import time

# 1. API Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY secret nahi mila.")
    exit(1)

client = genai.Client(api_key=api_key)

# NOTE: Purana google.generativeai package AQ. (auth) keys ko sahi se support nahi karta tha,
# yahi tumhare "API_KEY_INVALID" error ki asli wajah thi - chahe key kitni bhi baar regenerate
# karte. Ab naye google-genai SDK pe shift kar diya hai jo Google ke current docs ke mutabik
# AQ. keys ke saath properly kaam karta hai.
# Model: gemini-1.5-flash bhi shut down ho chuka hai, isliye gemini-2.5-flash use kar rahe hain
# (20MB PDF ke liye Files API ka limit 50MB hai, toh yeh easily fit ho jayega).
MODEL_NAME = "gemini-2.5-flash"


def call_gemini_with_retry(contents, max_retries=6):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} chal raha hai...")
            return client.models.generate_content(model=MODEL_NAME, contents=contents)
        except errors.APIError as e:
            error_code = getattr(e, "code", None)
            if error_code == 429:
                wait_time = 30 + (attempt * 15)
                print(f"Speed Limit lag gayi! {wait_time} seconds wait kar rahe hain... (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    print(f"{max_retries} baar try kiya par nahi hua.")
                    raise e
            elif error_code == 503:
                # Google ke servers temporarily overloaded hain - yeh humari galti nahi hai
                wait_time = 20 + (attempt * 10)
                print(f"Google ke servers abhi busy hain (503). {wait_time} seconds wait kar rahe hain... (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    print(f"{max_retries} baar try kiya par server abhi bhi overloaded hai.")
                    raise e
            else:
                # Auth error, bad model name, etc - retry se nahi sudhrega
                print(f"Koi alag error aaya jo rate-limit nahi hai: {e}")
                raise e


# 2. Advanced UPSC Prompt
upsc_prompt = """
You are an expert UPSC faculty. Create a comprehensive Daily Study Brief for an aspirant.
If a newspaper document is provided, extract the most important news from it (focus on National News, Editorials, and IR). 
If NO document is provided, generate today's most important potential UPSC topics.
Format the output STRICTLY using this Markdown structure. Use emojis, bold text for key terms, and bullet points:
# 📰 Daily UPSC Master-Brief
## 📝 The Hindu Editorial Analysis
* **Topic:** [Name of the topic]
* **Context:** [Brief background]
* **Key Takeaways:** * [Point 1]
  * [Point 2]
## 🏛️ Polity & Governance
* **Current Issue:** [Name of the issue]
* **Main Points:** * [Point 1]
## 🌍 Geography & Environment
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]
## 🌐 International Relations (IR)
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]
## 🏏 Sports & Miscellaneous
* **Highlight:** [Brief point relevant for Prelims]
"""

try:
    print("Content generation shuru kar rahe hain...")

    if os.path.exists("newspaper.pdf"):
        print("Full Newspaper PDF detected! Uploading to Google servers...")
        uploaded_pdf = client.files.upload(file="newspaper.pdf")

        # Naye SDK mein file processing turant hoti hai upload ke andar hi for most files,
        # lekin bade PDFs ke liye state check zaroor karte hain.
        print("Google AI PDF ko process kar raha hai...")
        while uploaded_pdf.state.name == "PROCESSING":
            time.sleep(10)
            uploaded_pdf = client.files.get(name=uploaded_pdf.name)

        if uploaded_pdf.state.name == "FAILED":
            print("Error: Google PDF ko process nahi kar paya. Format check karein.")
            exit(1)

        print("PDF successfully read! Ab notes extract ho rahe hain...")
        response = call_gemini_with_retry([uploaded_pdf, upsc_prompt])

        # Cleanup
        client.files.delete(name=uploaded_pdf.name)

    else:
        print("Koi PDF nahi mila. AI apni knowledge se topics generate kar raha hai...")
        response = call_gemini_with_retry(upsc_prompt)

    # 4. File mein save karo
    with open("content.md", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("Success! 'content.md' file ban gayi hai aur ready hai.")
except Exception as e:
    print(f"\n--- ERROR AAYA HAI ---")
    print(e)
    exit(1)
