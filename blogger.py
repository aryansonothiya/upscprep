import google.generativeai as genai
import os
import time

# 1. API Setup
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') 

# 2. Advanced UPSC Prompt
upsc_prompt = """
You are an expert UPSC faculty. Create a comprehensive Daily Study Brief for an aspirant.
If a newspaper document is provided, extract the most important news from it (focus on National News, Editorials, and IR). 

Format the output STRICTLY using this Markdown structure. Use emojis, bold text for key terms, and bullet points:

# 📰 Daily UPSC Master-Brief

## 📝 The Hindu Editorial Analysis
* **Topic:** [Name of the topic]
* **Context:** [Brief background]
* **Key Takeaways:** 
  * [Point 1]
  * [Point 2]

## 🏛️ Polity & Governance
* **Current Issue:** [Name of the issue]
* **Main Points:** 
  * [Point 1]

## 🌍 Geography & Environment
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]

## 🌐 International Relations (IR)
* **Current Issue:** [Name of the issue]
* **Main Points:**
  * [Point 1]
"""

try:
    print("Content generation shuru kar rahe hain...")
    
    # 3. PDF Upload aur SMART WAIT Logic
    if os.path.exists("newspaper.pdf"):
        print("Full Newspaper PDF detected! Uploading to Google servers...")
        uploaded_pdf = genai.upload_file("newspaper.pdf")
        
        # Google ko PDF padhne ka time dena
        print("Google AI PDF ko process kar raha hai. 30-60 seconds wait karein...")
        while uploaded_pdf.state.name == "PROCESSING":
            time.sleep(10) # 10 second ruko
            uploaded_pdf = genai.get_file(uploaded_pdf.name) # Status check karo
            
        if uploaded_pdf.state.name == "FAILED":
            print("Error: Google PDF ko process nahi kar paya.")
            exit(1)
            
        print("PDF successfully read! Ab notes extract ho rahe hain...")
        response = model.generate_content([uploaded_pdf, upsc_prompt])
        
        # AI server se PDF delete kar do taaki space bache
        genai.delete_file(uploaded_pdf.name)
        
    else:
        print("Koi PDF nahi mila. Auto-mode on...")
        response = model.generate_content(upsc_prompt)
    
    # 4. File mein save karo
    with open("content.md", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("Success! 'content.md' file ban gayi hai aur ready hai.")

except Exception as e:
    print(f"\n--- ERROR AAYA HAI ---")
    print(e)
    exit(1)
