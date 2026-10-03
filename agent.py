import os
import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. تحميل الإعدادات
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ لم يتم العثور على GEMINI_API_KEY في ملف .env!")

client = genai.Client(api_key=api_key)

# 2. الاتصال بقاعدة البيانات المحلية
chroma_client = chromadb.PersistentClient(path="./company_db")
collection = chroma_client.get_collection(name="services")

# 3. إعداد تطبيق FastAPI
app = FastAPI(title="Ghamer AI Agent API")

# تخزين جلسات الشات في الذاكرة (مقتطع حسب العميل)
sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

def get_context(user_query: str) -> str:
    """استرجاع المعلومات من قاعدة البيانات"""
    results = collection.query(
        query_texts=[user_query],
        n_results=3
    )
    if results and results["documents"]:
        return "\n".join(results["documents"][0])
    return ""

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="الرسالة فارغة")

    # جلب context الخدمات المتعلق بالسؤال
    retrieved_docs = get_context(user_message)

    # إنشاء جلسة شات جديدة لو العميل أول مرة يراسلنا
    if session_id not in sessions:
        system_instruction = f"""
أنت مساعد خدمة العملاء الذكي لوكالة "غامر للإعلان والتسويق" (Ghamer Agency).
وظيفتك الرد على استفسارات العملاء بأسلوب مهني، ودود، ومختصر باللغة العربية.

المعلومات المتاحة لديك عن الخدمات والشركة:
{retrieved_docs}

قواعد التعامل مع الأسئلة واللغة:
1. التكيف مع اللهجات: افهم سؤال العميل بأي لهجة عربية (سعودية، مصرية، شامية... إلخ) وأجب عليه بلغة عربية مبسطة وودودة.
2. عدم توفر المعلومة: إذا كانت المعلومة غير موجودة في البيانات أعلاه، لا تخترع إجابة، بل اعتذر برفق واطلب منه التواصل عبر الرقم 966115105887+ أو حساب الانستجرام ghameragency@.
3. التذكر والسياق: راعِ سياق الحديث والردود السابقة مع العميل.
"""
        sessions[session_id] = client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )

    chat = sessions[session_id]

    try:
        # إرسال الرسالة مع تذكر الـ History تلقائياً
        response = chat.send_message(user_message)
        return {
            "status": "success",
            "session_id": session_id,
            "response": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# تشغيل الـ CLI المباشر للتجربة في الـ Terminal
if __name__ == "__main__":
    import uvicorn
    print("🚀 جاري تشغيل الـ Agent سيرفر على http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)