import os
from google import genai
from google.genai import types


def get_secret(name: str):
    """جلب قيمة من متغيرات البيئة أو من Streamlit Secrets"""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


def get_client():
    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ لم يتم العثور على GEMINI_API_KEY!")
    return genai.Client(api_key=api_key)


# قراءة الخدمات
def read_services_file() -> str:
    file_path = os.path.join(os.path.dirname(__file__), "services.txt")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""


SERVICES_CONTEXT = read_services_file()


def get_agent_response(user_message: str) -> str:
    """إرسال الطلب والحصول على رد سريع"""
    try:
        client = get_client()
    except Exception as e:
        return f"خطأ في الاتصال بالمفتاح (API Key): {e}"

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

    # اسم النموذج ممكن يتغير من Secrets (MODEL_NAME) بدون تعديل الكود
    custom_model = get_secret("MODEL_NAME")

    models_to_try = [
        m for m in [
            custom_model,
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-2.5-flash",
        ] if m
    ]

    errors = []
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                ),
            )
            return response.text
        except Exception as e:
            errors.append(f"{model_name}: {e}")
            continue

    return "حدث خطأ أثناء الاتصال بالنموذج:\n" + "\n".join(errors)
