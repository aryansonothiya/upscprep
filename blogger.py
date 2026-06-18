import google.generativeai as genai
import os
import time
from google.api_core import exceptions

# 1. API Setup
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') 

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
        uploaded_pdf = genai.upload_file("newspaper.pdf")
        
        # Yahan script wait karegi jab tak Google PDF padh nahi leta
        print("Google AI PDF ko process kar raha hai. Isme 30-60 seconds lag sakte hain...")
        while uploaded_pdf.state.name == "PROCESSING":
            time.sleep(10) # 10 second ruko
            uploaded_pdf = genai.get_file(uploaded_pdf.name) # Status check karo
            
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
