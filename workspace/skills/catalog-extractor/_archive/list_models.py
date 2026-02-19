import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
