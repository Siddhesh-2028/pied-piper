# agent.py
import matplotlib
# CRITICAL FIX: Must be set BEFORE importing pyplot or pandasai
matplotlib.use('Agg') 

import os
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from mock_db import generate_static_data

load_dotenv()

# --- 1. THE CUSTOM WRAPPER ---
class PandasAILangChainWrapper(LLM):
    def __init__(self, langchain_model):
        self.model = langchain_model
        
    def call(self, instruction, value=None, suffix="") -> str:
        prompt_text = str(instruction)
        response = self.model.invoke(prompt_text)
        return response.content

    @property
    def type(self) -> str:
        return "google-gemini-wrapper"

# --- 2. SETUP ---
df = generate_static_data()

# Initialize Gemini
google_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# Initialize PandasAI
agent = SmartDataframe(
    df, 
    config={
        "llm": PandasAILangChainWrapper(google_llm),
        "save_charts": True,
        "save_charts_path": "static/charts", 
        "enable_cache": False,
    }
)

def ask_pandas_ai(question):
    try:
        # Run the chat
        response = agent.chat(question)
        
        # Check if response is an image path (PandasAI returns absolute paths sometimes)
        if isinstance(response, str) and (response.endswith(".png") or response.endswith(".jpg")):
            # Extract just the filename to serve it via Flask
            filename = os.path.basename(response)
            return {"type": "image", "data": f"/charts/{filename}"}
            
        return {"type": "text", "data": str(response)}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"type": "error", "data": str(e)}