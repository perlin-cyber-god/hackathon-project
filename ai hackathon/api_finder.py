# check_models.py
import google.generativeai as genai

# --- IMPORTANT ---
# Paste your secret API key here
API_KEY = "AIzaSyAOr3JM9iPKTYED1P2RZCDfe5w7n-QZ6-Y"

try:
    genai.configure(api_key=API_KEY)
    
    print("\n--- Finding Models You Can Use ---")
    
    found_model = False
    for m in genai.list_models():
        # We are looking for models that support the 'generateContent' method
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found a working model: {m.name}")
            found_model = True
            
    if not found_model:
        print("\n❌ No models supporting 'generateContent' were found for your API key.")
        print("This might be a regional or account-level restriction.")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")