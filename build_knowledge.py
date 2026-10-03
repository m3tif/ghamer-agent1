import chromadb

# 1. إنشاء قاعدة بيانات محلية Vector DB
chroma_client = chromadb.PersistentClient(path="./company_db")

# إنشاء مجموعة (Collection) لخدمات الشركة
collection = chroma_client.get_or_create_collection(name="services")

# 2. قراءة ملف الخدمات
with open("services.txt", "r", encoding="utf-8") as f:
    text = f.read()

# تقسيم النص لفقرات أو خدمات منفصلة (بناءً على السطر الجديد)
docs = [doc.strip() for doc in text.split("\n\n") if doc.strip()]

# 3. إدخال البيانات في Vector Database
ids = [f"service_{i}" for i in range(len(docs))]
collection.add(
    documents=docs,
    ids=ids
)

print(f"✅ تم تحميل {len(docs)} معلومة عن خدماتك بنجاح في قاعدة البيانات!")