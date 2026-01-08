# agent.py
import os
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from db import get_real_data

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
# Fetch data from Real DB
df = get_real_data()

# Handle empty DB case
if df.empty:
    print("⚠️ Warning: No data found in database. Initializing empty DataFrame.")
    df = pd.DataFrame(columns=["id", "date", "merchant", "category", "amount", "currency", "bankName", "source"])

# Initialize Gemini
google_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# Initialize PandasAI (Text Only Mode)
agent = SmartDataframe(
    df, 
    config={
        "llm": PandasAILangChainWrapper(google_llm),
        "save_charts": False, # <--- DISABLED CHARTS
        "enable_cache": False,
    }
)

def ask_pandas_ai(question):
    try:
        # Run the chat
        response = agent.chat(question)
        
        # We now ONLY return text. No image path checking needed.
        return {"type": "text", "data": str(response)}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"type": "error", "data": "I encountered an error processing that request."}