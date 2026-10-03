import os
import chromadb
from google import genai
from google.genai import types

# 1. جلب API Key
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
    """دالة لمعالجة سؤال العميل وإرجاع الرد مباشرة مع محاولة موديل احتياطي"""
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

    # قائمة الموديلات المتاحة بالترتيب (في حال كان الأول عليه ضغط يذهب للثاني)
    models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            # إذا كان الخطأ بسبب الضغط (503)، جرب الموديل التالي
            print(f"Failed with model {model_name}: {e}")
            continue

    return "السيرفرات تشهد ضغطاً حالياً، يرجى إعادة محاولة إرسال الرسالة بعد لحظات."
