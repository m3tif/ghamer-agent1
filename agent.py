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

# 2. قراءة ملف الخدمات مباشرة لخفة وسرعة الاستجابة
def read_services_file() -> str:
    file_path = os.path.join(os.path.dirname(__file__), "services.txt")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""

# قراءة الخدمات مرة واحدة فقط عند بدء السيرفر لزيادة السرعة
SERVICES_CONTEXT = read_services_file()

def get_agent_response(user_message: str) -> str:
    """دالة خفيفة وسريعة جداً لمعالجة الردود"""
    system_instruction = f"""
أنت مساعد خدمة العملاء الذكي لوكالة "غامر للإعلان والتسويق" (Ghamer Agency).
وظيفتك الرد على استفسارات العملاء وإجابتهم بالتفصيل عن الخدمات المتاحة بناءً على المعلومات التالية فقط.

المعلومات المتاحة لديك عن الخدمات والشركة:
{SERVICES_CONTEXT}

قواعد التعامل مع الأسئلة واللغة:
1. إظهار الخدمات: عند سؤال العميل عن الخدمات المتاحة، اذكر له جميع الخدمات والحلول الموجودة في البيانات أعلاه بوضوح وبأسلوب جذاب ومختصر.
2. التكيف مع اللهجات: افهم سؤال العميل بأي لهجة عربية وأجب عليه بلغة عربية مبسطة وودودة.
3. عدم توفر المعلومة: فقط إذا كان السؤال عن شيء غير موجود تماماً في البيانات، اعتذر برفق واطلب التواصل عبر الرقم 966115105887+ أو حساب الانستجرام ghameragency@.
"""

    # البداية بالموديل الأسرع والأخف فوراً
    models_to_try = ["gemini-1.5-flash", "gemini-2.5-flash"]

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
            print(f"Error with {model_name}: {e}")
            continue

    return "عذراً، حدث تأخير في الاستجابة. يرجى إعادة محاولة إرسال الرسالة."
