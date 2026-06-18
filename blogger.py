import google.generativeai as genai
import os
import time
from datetime import datetime
from google.api_core import exceptions

# 1. API Setup
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# PDF padhne ke liye humein Gemini ka sabse advanced aur fast model chahiye
model = genai.GenerativeModel('gemini-2.5-flash') 

def call_gemini_with_retry(prompt, file_obj=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} chal raha hai...")
            if file_obj:
                return model.generate_content([file_obj, prompt])
            else:
                return model.generate_content(prompt)
        except exceptions.ResourceExhausted as e:
            print(f"Speed Limit lag gayi! 30 seconds wait kar rahe hain...")
            if attempt < max_retries - 1:
                time.sleep(30)
            else:
                raise e

# 2. Advanced UPSC Prompt (Website par sundar dikhne ke liye)
upsc_prompt = """
You are an expert UPSC faculty. Create a comprehensive Daily Study Brief for an aspirant.

If a newspaper document is provided, extract the most important news from it. 
If NO document is provided, generate today's most important potential UPSC topics based on current affairs.

Format the output STRICTLY using this Markdown structure. Use emojis, bold text for key terms, and bullet points for readability:

# 📰 Daily UPSC Master-Brief

## 📝 The Hindu Editorial Analysis
* **Topic:** [Name of the topic]
* **Context:** [Brief background]
* **Key Takeaways:** 
  * [Point 1]
  * [Point 2]
  * [Point 3]

## 🏛️ Polity & Governance
* **Current Issue:** [Name of the issue]
* **Main Points:** 
  * [Point 1]
  * [Point 2]

## 🌍 Geography & Environment
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]
  * [Point 2]

## 🌐 International Relations (IR)
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]
  * [Point 2]

## 🏏 Sports & Miscellaneous
* **Highlight:** [Brief point relevant for Prelims]

Make the content detailed enough for UPSC revision.
"""

try:
    print("Content generation shuru kar rahe hain...")
    
    # 3. Check karo ki kya Aryan ne aaj koi Newspaper PDF upload kiya hai?
    if os.path.exists("newspaper.pdf"):
        print("Newspaper PDF detected! Uploading to AI to extract notes...")
        # PDF ko AI ke paas bhejo
        uploaded_pdf = genai.upload_file("newspaper.pdf")
        response = call_gemini_with_retry(upsc_prompt, file_obj=uploaded_pdf)
        
        # Cleanup: AI ke server se PDF hata do taaki space bache
        genai.delete_file(uploaded_pdf.name)
    else:
        print("Koi PDF nahi mila. AI apni knowledge se aaj ke topics generate kar raha hai...")
        response = call_gemini_with_retry(upsc_prompt)
    
    # 4. File mein save karo
    with open("content.md", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("Success! 'content.md' file ban gayi hai aur ready hai.")

except Exception as e:
    print(f"\n--- ERROR AAYA HAI ---")
    print(e)
    exit(1)
