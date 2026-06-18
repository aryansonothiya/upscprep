import google.generativeai as genai
import os
import time
from google.api_core import exceptions

# 1. API Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY secret nahi mila.")
    exit(1)

genai.configure(api_key=api_key)

# NOTE: gemini-1.5-flash aur gemini-1.0 models Google ne completely SHUT DOWN kar diye hain.
# gemini-2.5-flash abhi active hai aur 20MB jaisi heavy PDFs ke liye bhi
# same bada context window deta hai jo 1.5-flash deta tha.
model = genai.GenerativeModel('gemini-2.5-flash')


def call_gemini_with_retry(prompt, file_obj=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if file_obj:
                return model.generate_content([file_obj, prompt])
            else:
                return model.generate_content(prompt)
        except exceptions.ResourceExhausted as e:
            print(f"Speed Limit! 30 seconds wait kar rahe hain...")
            if attempt < max_retries - 1:
                time.sleep(30)
            else:
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

    # 3. PDF Upload aur SMART WAIT Logic
    if os.path.exists("newspaper.pdf"):
        print("Full Newspaper PDF detected! Uploading to Google servers...")
        try:
            uploaded_pdf = genai.upload_file("newspaper.pdf")
        except exceptions.PermissionDenied as e:
            print("\n--- API KEY ERROR ---")
            print("Yeh upload step hi fail ho gaya, matlab key Google tak pahunch hi nahi rahi sahi se.")
            print("Agar tumne abhi naya AQ. prefix wala key banaya hai AI Studio se, toh yeh")
            print("filhaal kuch SDKs ke saath compatible nahi hai (Google ka known issue, June 2026).")
            print("Cloud Console (console.cloud.google.com) se key banao aur check karo woh")
            print("'AIzaSy...' se start ho rahi hai, 'AQ.' se nahi.")
            print(f"Original error: {e}")
            exit(1)

        # Yahan script wait karegi jab tak Google PDF padh nahi leta
        print("Google AI PDF ko process kar raha hai. Isme 30-60 seconds lag sakte hain...")
        while uploaded_pdf.state.name == "PROCESSING":
            time.sleep(10)
            uploaded_pdf = genai.get_file(uploaded_pdf.name)

        if uploaded_pdf.state.name == "FAILED":
            print("Error: Google PDF ko process nahi kar paya. Format check karein.")
            exit(1)

        print("PDF successfully read! Ab notes extract ho rahe hain...")
        response = call_gemini_with_retry(upsc_prompt, file_obj=uploaded_pdf)

        # Cleanup
        genai.delete_file(uploaded_pdf.name)

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
