import google.generativeai as genai
import os

# 1. Apni API Key yahan daalein
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# 2. Model setup - Humne 'gemini-1.5-pro' use kiya hai jo zyada stable hai
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. Topic define karo
topic = "Impact of AI in UPSC Civil Services Preparation"

# 4. Content generate karo
response = model.generate_content(f"Write a detailed 500-word UPSC editorial style article on {topic}. Include headings, subheadings, and a conclusion.")

# 5. File mein save karo
with open("content.md", "w", encoding="utf-8") as f:
    f.write(f"# {topic}\n\n")
    f.write(response.text)

print("Article generate ho gaya! Check karo 'content.md' file.")