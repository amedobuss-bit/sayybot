# 🚂 إعداد RailBot على PythonAnywhere

## 📋 المتطلبات
- حساب PythonAnywhere (مجاني)
- بوت Telegram مع توكن صالح
- ملف `config.ini` يحتوي على بيانات البوت

## 🚀 خطوات التثبيت

### 1. رفع الملفات
- ارفع جميع ملفات المشروع إلى PythonAnywhere
- تأكد من وجود `main.py`, `wsgi.py`, `requirements.txt`, `config.ini`

### 2. تثبيت المتطلبات
```bash
pip install --user -r requirements.txt
```

### 3. إعداد متغيرات البيئة (مفضل)
في صفحة "Web app setup":
1. انزل تحت إلى **Environment variables**
2. أضف المتغيرات التالية:
   - `TG_SECRET_TOKEN` = `your_bot_token_here`
   - `TG_API_ID` = `your_api_id_here`
   - `TG_API_HASH` = `your_api_hash_here`
   - `TG_WEBHOOK_URL` = `https://ahmrabaee.pythonanywhere.com`

**ملاحظة:** يمكنك أيضاً استخدام ملف `config.ini` للاختبار المحلي

### 4. إعداد Web App
1. اذهب إلى تبويب "Web"
2. انقر على "Add a new web app"
3. اختر "Manual configuration"
4. اختر Python 3.9 أو أحدث
5. في "Code" section:
   - Source code: `/home/YOUR_USERNAME/railBot`
   - Working directory: `/home/YOUR_USERNAME/railBot`
   - WSGI configuration file: `/home/YOUR_USERNAME/railBot/wsgi.py`

### 5. تعديل WSGI
في ملف WSGI، تأكد من المسار الصحيح:
```python
from main import flask_app
application = flask_app
```

### 6. تشغيل البوت
1. انقر على "Reload" في Web App
2. اذهب إلى Console وقم بتشغيل:
```bash
cd railBot
python main.py
```

## 🔧 استكشاف الأخطاء

### مشكلة في Webhook
- تأكد من صحة التوكن
- تحقق من عنوان URL
- تأكد من أن HTTPS يعمل

### مشكلة في المكتبات
- تأكد من تثبيت Flask و requests
- تحقق من إصدار Python

## 📱 اختبار البوت
1. أرسل `/start` للبوت
2. تحقق من استجابة البوت
3. اختبر الأزرار والوظائف

## 🎯 ملاحظات مهمة
- البوت يعمل الآن كـ Web App
- لا حاجة لتشغيل يدوي مستمر
- Webhook يتلقى الرسائل تلقائياً
- احتفظ بجميع الوظائف الأصلية

## 🔐 متغيرات البيئة

### **المتغيرات المطلوبة:**
- `TG_SECRET_TOKEN`: توكن البوت من @BotFather
- `TG_API_ID`: معرف API من my.telegram.org
- `TG_API_HASH`: مفتاح API من my.telegram.org
- `TG_WEBHOOK_URL`: عنوان الموقع (اختياري)

### **كيفية إضافتها:**
1. اذهب إلى **Web** → اختر موقعك
2. انزل تحت إلى **Environment variables**
3. أضف كل متغير على حدة
4. انقر على **"Reload"** بعد الإضافة

## 🆘 الدعم
إذا واجهت مشاكل، تحقق من:
- سجلات الخطأ في PythonAnywhere
- حالة Web App
- صحة بيانات البوت
- متغيرات البيئة
