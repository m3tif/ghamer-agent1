import os
import chromadb
from google import genai
from google.genai import types

# 1. جلب API Key من البيئة أو من Streamlit Secrets
api_key = os.getenv("GEMINI_API_KEY")

def get_client():
    if not api_key:
        try:
            import streamlit as st
            return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        except Exception:
            raise ValueError("⚠️ لم يتم العثور على GEMINI_API_KEY!")
    return genai.Client(api_key=api_key)

client = get_client()

# 2. الاتصال بقاعدة البيانات المحفوظة
db_path = os.path.join(os.path.dirname(__file__), "company_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_or_create_collection(name="services")

def get_context(user_query: str) -> str:
    """استرجاع المعلومات المتعلقة من قاعدة البيانات"""
    try:
        results = collection.query(query_texts=[user_query], n_results=3)
        if results and results.get("documents") and results["documents"][0]:
            return "\n".join(results["documents"][0])
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
    return ""

def get_agent_response(user_message: str) -> str:
    """دالة لمعالجة سؤال العميل وإرجاع الرد مباشرة"""
    retrieved_docs = get_context(user_message)

    system_instruction = f"""
أنت مساعد خدمة العملاء الذكي لوكالة "غامر للإعلان والتسويق" (Ghamer Agency).
وظيفتك الرد على استفسارات العملاء بأسلوب مهني، ودود، ومختصر باللغة العربية.

المعلومات المتاحة لديك عن الخدمات والشركة:
{retrieved_docs}

قواعد التعامل مع الأسئلة واللغة:
1. التكيف مع اللهجات: افهم سؤال العميل بأي لهجة عربية وأجب عليه بلغة عربية مبسطة وودودة.
2. عدم توفر المعلومة: إذا كانت المعلومة غير موجودة في البيانات أعلاه، لا تخترع إجابة، بل اعتذر برفق واطلب منه التواصل عبر الرقم 966115105887+ أو حساب الانستجرام ghameragency@.
3. التذكر والسياق: راعِ سياق الحديث والردود السابقة مع العميل.
"""

    try:
        # استخدام الموديل المطلوب gemini-3.8-flash
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )
        return response.text
    except Exception as e:
        return f"حدث خطأ أثناء معالجة طلبك: {e}"
