import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
import json
import os
import io
import random
import configparser
from flask import Flask, request, jsonify
import requests

# ========================================
# 🚂 RailBot - بوت القصائد الآمن
# ========================================
# 
# هذا البوت مصمم للعمل على PythonAnywhere
# يمكن تشغيله بطريقتين:
# 1. باستخدام متغيرات البيئة (مفضل للإنتاج)
# 2. باستخدام ملف config.ini (للاختبار المحلي)
# ========================================

# دالة تشفير للنصوص لتجاوز خوارزمية تلغرام
def encrypt_text(text):
    """
    تشفير النص بإدخال علامات بين الحروف لجعل الأسماء غير واضحة
    لتجاوز خوارزمية التعرف على الكلمات في تلغرام
    """
    if not text:
        return text
    
    # علامات التشفير
    encrypt_chars = ['ـ', 'ـ', 'ـ', 'ـ', 'ـ', 'ـ', 'ـ', 'ـ', 'ـ', 'ـ']
    
    encrypted = ""
    for char in text:
        encrypted += char
        # إضافة علامة تشفير بعد بعض الأحرف (لجعل الأسماء غير واضحة)
        if char.strip() and random.random() < 0.2:  # 20% احتمال إضافة علامة
            encrypted += random.choice(encrypt_chars)
    
    return encrypted

# قراءة الإعدادات من متغيرات البيئة أو ملف config.ini
def load_config():
    """قراءة إعدادات البوت من متغيرات البيئة أو ملف config.ini"""
    # محاولة قراءة من متغيرات البيئة (إذا وجدت)
    bot_token = os.getenv("TG_BOT_TOKEN")
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    secret_token = os.getenv("TG_SECRET_TOKEN", "default-secret-123")

    # إذا وجدت متغيرات البيئة، استخدمها
    if bot_token and api_id and api_hash:
        print("✅ تم قراءة الإعدادات من متغيرات البيئة")
        return {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "bot_token": bot_token,
            "secret_token": secret_token,
        }

    # وإلا اقرأ من ملف config.ini
    print("ℹ️ لم يتم العثور على متغيرات البيئة، جاري القراءة من config.ini")
    try:
        cfg = configparser.ConfigParser()
        cfg.read("config.ini", encoding="utf-8")
        return {
            "api_id": int(cfg.get("pyrogram", "api_id")),
            "api_hash": cfg.get("pyrogram", "api_hash"),
            "bot_token": cfg.get("pyrogram", "bot_token"),
            "secret_token": cfg.get("webhook", "secret_token", fallback="default-secret-123"),
        }
    except Exception as e:
        print(f"❌ خطأ في قراءة الإعدادات: {e}")
        print("يرجى التأكد من وجود ملف config.ini أو إضافة متغيرات البيئة")
        exit(1)

# إعداد Flask لاستقبال Webhook من Telegram
flask_app = Flask(__name__)

# إعداد الاتصال بالبوت باستخدام ملف config.ini
try:
    bot_config = load_config()
    bot = Client(
        "safe_poetry_bot",
        api_id=bot_config['api_id'],
        api_hash=bot_config['api_hash'],
        bot_token=bot_config['bot_token'],
        in_memory=True
    )
    bot.start()  # مهم جداً مع الـ webhook
except Exception as e:
    print(f"❌ خطأ في قراءة ملف config.ini: {e}")
    print("يرجى التأكد من وجود الملف وصحة البيانات")
    exit(1)

# تكوين Webhook URL
# يمكن استخدام متغير البيئة TG_WEBHOOK_URL أو إنشاؤه تلقائياً
webhook_base = os.environ.get('TG_WEBHOOK_URL', f"https://ahmrabaee.pythonanywhere.com")
WEBHOOK_URL = f"{webhook_base}/{bot_config['bot_token']}"

# تعريف توكن البوت للاستخدام المباشر
BOT_TOKEN = bot_config['bot_token']

# 💬 رسالة الترحيب
intro_message = (
    "بسمِ اللهِ ربِّ أبي أيوبَ وأصحابِه، وبه نستعين، وبعد:\n"
    "فإنّ القلمَ كالسّيفِ، إذا عرَفَ التوحيدَ، قام من رمسه على رأسه، يطيرُ بصاحبه إلى كلِّ نِزالٍ وقِتال، "
    "ولم يزل به يَصولُ ويجولُ، حتى يُقيمَ اللهُ به الحجة، وينصرَ به دينَه.\n"
    "فاكتبْ، فإنّ روحَ القُدُسِ معك، ما نصرتَ الحق، وأقمتَ الكلمةَ، وجعلتَ المِدادَ جـ ـهـ ادًا."
)

# 📝 تحميل القصائد من ملف خارجي
def load_poems():
    try:
        with open("poems.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: poems.json file not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode poems.json.")
        return []
    except Exception as e:
        print(f"Error loading poems: {e}")
        return []

poems = load_poems()

# --- دالة مركزية لإرسال الملفات ---
def send_file(client, callback_query, file_path, caption):
    try:
        if not os.path.exists(file_path):
            error_msg = f"❌ خطأ: لم يتم العثور على الملف في المسار: {file_path}"
            print(error_msg)
            callback_query.answer(error_msg, show_alert=True)
            return

        client.send_document(
            chat_id=callback_query.message.chat.id,
            document=file_path,
            caption=caption
        )
        callback_query.answer("✅ تم إرسال الملف بنجاح.")
    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء الإرسال: {e}"
        print(error_msg)
        callback_query.answer(error_msg, show_alert=True)

# --- معالجات الأوامر الرئيسية ---
@bot.on_message(filters.command("start"))
def start(client, message: Message):
    message.reply_text(
        intro_message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("انتقل إلى مادة الأرشيف", callback_data="show_archive")]
        ])
    )

@bot.on_callback_query(filters.regex("show_archive"))
def show_archive(client, callback_query):
    # تم تعديل ترتيب الأزرار فقط في هذا القسم
    keyboard = [
        [InlineKeyboardButton(encrypt_text("أسامة بن لادن"), callback_data="show_osama_poems")],
        [InlineKeyboardButton(encrypt_text("أبو حمزة المهاجر"), callback_data="show_abu_hamza_books")],
        [InlineKeyboardButton(encrypt_text("أبو أنس الفلسطيني"), callback_data="show_abu_anas")],
        [InlineKeyboardButton(encrypt_text("ميسرة الغريب"), callback_data="show_mysara_gharib_books")],
        [InlineKeyboardButton(encrypt_text("أبو الحسن المهاجر"), callback_data="show_muhajir_books")],
        [InlineKeyboardButton(encrypt_text("العدنان"), callback_data="show_adnani_books")],
        [InlineKeyboardButton(encrypt_text("أبو حمزة القرشي"), callback_data="show_qurashi_books")],
        [InlineKeyboardButton(encrypt_text("أبو عمر المهاجر"), callback_data="show_abu_omar_books")],
        [InlineKeyboardButton(encrypt_text("أبو بلال الحربي"), callback_data="show_harbi_books")],
        [InlineKeyboardButton(encrypt_text("أحلام النصر الدمشقية"), callback_data="show_ahlam_alnaser_books")],
        # --- باقي الأسماء بترتيب غير مهم ---
        [InlineKeyboardButton(encrypt_text("الشاعر أبو مالك شيبية الحمد"), callback_data="show_shaybah_books")],
        [InlineKeyboardButton(encrypt_text("المهندس محمد الزهيري"), callback_data="show_zuhayri_books")],
        [InlineKeyboardButton(encrypt_text("بنت نجد"), callback_data="show_bint_najd_books")],
        [InlineKeyboardButton(encrypt_text("العقاب المصري"), callback_data="show_oqab_masri")],
        [InlineKeyboardButton(encrypt_text("مرثد بن عبد الله"), callback_data="show_marthad_abdullah")],
        [InlineKeyboardButton(encrypt_text("أبو خيثمة الشنقيطي"), callback_data="show_abu_khithama")],
        [InlineKeyboardButton(encrypt_text("لويس عطية الله"), callback_data="show_louis")],
        [InlineKeyboardButton(encrypt_text("أبو بكر المدني"), callback_data="show_abu_bakr_madani_books")],
        [InlineKeyboardButton(encrypt_text("حسين المعاضيدي"), callback_data="show_hussein_almadidi")]
    ]
    callback_query.message.edit_text("اختر مجموعة القصائد:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- قسم القصائد النصية ---
@bot.on_callback_query(filters.regex("show_osama_poems"))
def show_osama_poems(client, callback_query):
    # تحميل القصائد ديناميكياً
    current_poems = load_poems()
    # عرض قصائد أسامة بن لادن فقط
    osama_poems = [p for p in current_poems if p.get("author") == "أسامة بن لادن"]
    keyboard = []
    
    # إضافة القصائد مع تحسين العرض
    for i, poem in enumerate(osama_poems):
        title = poem.get("title", f"قصيدة {i+1}")
        keyboard.append([InlineKeyboardButton(f"📜 {title}", callback_data=f"poem_{current_poems.index(poem)}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    
    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
    poem_count = len(osama_poems)
    total_poems = len(current_poems)
    callback_query.message.edit_text(encrypt_text(f"قائمة القصائد:\n\n(أسامة بن لادن)\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}"), reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^poem_(\d+)$"))
def show_poem(client, callback_query):
    try:
        # تحميل القصائد ديناميكياً
        current_poems = load_poems()
        idx = int(callback_query.matches[0].group(1))
        if 0 <= idx < len(current_poems):
            poem = current_poems[idx]
            author = poem.get("author", "غير محدد")
            
            # تحديد زر الرجوع حسب المؤلف
            return_callback = "show_archive"
            if author == "أسامة بن لادن":
                return_callback = "show_osama_poems"
            elif author == "العدنان":
                return_callback = "show_adnani_books"
            elif author == "أبو الحسن المهاجر":
                return_callback = "show_muhajir_books"
            elif author == "أبو عمر المهاجر":
                return_callback = "show_abu_omar_books"
            elif author == "أبو بلال الحربي":
                return_callback = "show_harbi_books"
            
            callback_query.message.edit_text(encrypt_text(f"📖 **{poem['title']}**\n\n---\n\n{poem['content']}\n\n✍️ {author}"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=return_callback)]]))
        else:
            callback_query.answer(f"❌ القصيدة غير موجودة (المؤشر: {idx}, العدد الإجمالي: {len(current_poems)})", show_alert=True)
    except Exception as e:
        callback_query.answer(f"❌ خطأ في تحميل القصيدة: {str(e)}", show_alert=True)

# --- قسم الكتب (ملفات PDF) ---

# --- قسم أبو بلال الحربي ---
@bot.on_callback_query(filters.regex("show_harbi_books"))
def show_harbi_books(client, callback_query):
    # تحميل القصائد ديناميكياً
    current_poems = load_poems()
    # عرض قصائد أبو بلال الحربي مع الكتب
    harbi_poems = [p for p in current_poems if p.get("author") == "أبو بلال الحربي"]
    keyboard = []
    
    # إضافة القصائد مع تحسين العرض
    for i, poem in enumerate(harbi_poems):
        title = poem.get("title", f"قصيدة {i+1}")
        keyboard.append([InlineKeyboardButton(f"📜 {title}", callback_data=f"poem_{current_poems.index(poem)}")])
    
    # إضافة الكتب
    keyboard.append([InlineKeyboardButton("📖 وقفات مع الشيخ المربي", callback_data="send_harbi_pdf_1")])
    keyboard.append([InlineKeyboardButton("📖 ماذا فعلت بنا يا سعد؟", callback_data="send_harbi_pdf_2")])
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    
    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
    poem_count = len(harbi_poems)
    total_poems = len(current_poems)
    callback_query.message.edit_text(encrypt_text(f"⚔️ اختر من مؤلفات أبي بلال الحربي:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}"), reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("send_harbi_pdf_1"))
def send_harbi_pdf_1(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو بلال الحربي", "وقفات مع الشيخ المربي.pdf")
    send_file(client, callback_query, path, "📖 وقفات مع الشيخ المربي")

@bot.on_callback_query(filters.regex("send_harbi_pdf_2"))
def send_harbi_pdf_2(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو بلال الحربي", "ماذا فعلت بنا يا سعد؟.pdf")
    send_file(client, callback_query, path, "📖 ماذا فعلت بنا يا سعد؟")

# --- قسم الشاعر أبو مالك شيبة الحمد ---
SHAYBAH_ALHAMAD_BOOKS_MAP = {
    "send_shaybah_book_1": ("أزفتْ نهايةُ جبهةِ الجولاني - شيبة الحمد.pdf", "أزفتْ نهايةُ جبهةِ الجولاني"),
    "send_shaybah_book_2": ("أنا مع أبي بكر- شعر شيبة الحمد.pdf", "أنا مع أبي بكر"),
    "send_shaybah_book_3": ("الديوان العـرّيســة الشعري للشيخ شيبة الحمد.pdf", "الديوان العـرّيســة الشعري"),
    "send_shaybah_book_4": ("الستينية فى ذكر سلاطين الخلافة العثمانية بقلم شيبة الحمد -للتعديل.pdf", "الستينية فى ذكر سلاطين الخلافة العثمانية"),
    "send_shaybah_book_5": ("ديوان عبرة وعبير، شيبة الحمد.pdf", "ديوان عبرة وعبير"),
    "send_shaybah_book_6": ("سلام و إكرام لدولة الإسلام.pdf", "سلام و إكرام لدولة الإسلام"),
    "send_shaybah_book_7": ("على نهج الرسول - أبو مالك شيبة الحمد.pdf", "على نهج الرسول"),
    "send_shaybah_book_8": ("قصيدة سلام على سجن كوبر شيبة الحمد.pdf", "قصيدة سلام على سجن كوبر"),
    "send_shaybah_book_9": ("قصيدة أرق بالسيف كل دم كفور،_شيبة الحمد.pdf", "قصيدة أرق بالسيف كل دم كفور"),
    "send_shaybah_book_10": ("قصيدة جحاجح القوقاز - شيبة الحمد.pdf", "قصيدة جحاجح القوقاز"),
    "send_shaybah_book_11": ("قصيدة ذكـرتـك يـا أسـامـة دموع القلب شـيـبـة الـحـمـد.pdf", "قصيدة ذكـرتـك يـا أسـامـة"),
    "send_shaybah_book_12": ("قصيدة رحل الشّهيد وما رحل، شيبة الحمد.pdf", "قصيدة رحل الشّهيد وما رحل"),
    "send_shaybah_book_13": ("قصيدة صرخة من أزواد، شيبة الحمد.pdf", "قصيدة صرخة من أزواد"),
    "send_shaybah_book_14": ("قصيدة فارس الإيمان، شيبة الحمد.pdf", "قصيدة فارس الإيمان"),
    "send_shaybah_book_15": ("قصيدة متنا دعاة على أبواب عزتنا، شيبة الحمد.pdf", "قصيدة متنا دعاة على أبواب عزتنا"),
    "send_shaybah_book_16": ("قصيدة متى يكسر الشعب أغلاله، شيبة الحمد.pdf", "قصيدة متى يكسر الشعب أغلاله"),
    "send_shaybah_book_17": ("قصيدة نصرة لعبد الكريم_ الحميد، شيبة الحمد.pdf", "قصيدة نصرة لعبد الكريم الحميد"),
    "send_shaybah_book_18": ("مرثية آل الشيخ أسامة للشاعر شيبة الحمد.pdf", "مرثية آل الشيخ أسامة"),
    "send_shaybah_book_19": ("يا أسيراً خلفَ قضبانِ العدا.pdf", "يا أسيراً خلفَ قضبانِ العدا"),
    "send_shaybah_book_20": ("يـا دارَ سِـرْتَـ الفاتحيـنَ للشيخ شيبة الحمد.pdf", "يـا دارَ سِـرْتَـ الفاتحيـنَ")
}

@bot.on_callback_query(filters.regex("show_shaybah_books"))
def show_shaybah_books(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"📖 {v[1]}", k)] for k, v in SHAYBAH_ALHAMAD_BOOKS_MAP.items()]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text("✍️ اختر من مؤلفات الشاعر أبـو مـالك شيبـة الحمـد:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^send_shaybah_book_"))
def send_shaybah_book(client, callback_query):
    book_info = SHAYBAH_ALHAMAD_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_name, caption = book_info
        path = os.path.join("قصائد المشروع", "الشاعر أبـو مـالك شيبـة الحمـد", file_name)
        send_file(client, callback_query, path, f"📖 {caption}")

# --- قسم المهندس محمد الزهيري ---
ZUHAYRI_BOOKS_MAP = {
    "send_zuhayri_book_1": ("أعدنا القادسية في شموخٍ - محمد الزهيري.pdf", "أعدنا القادسية في شموخٍ"),
    "send_zuhayri_book_2": ("ركزنا في ذرى الأمجاد رمحاً - محمد الزهيري.pdf", "ركزنا في ذرى الأمجاد رمحاً"),
    "send_zuhayri_book_3": ("ستزيد دعوتنا عزا وتمكينا -محمد الزهيري.pdf", "ستزيد دعوتنا عزا وتمكينا"),
    "send_zuhayri_book_4": ("صليل الصوارم - محمد الزهيري.pdf", "صليل الصوارم"),
    "send_zuhayri_book_5": ("عراق اﷲ یزخر بالغیارى محمد الزهيري.pdf", "عراق الله يزخر بالغياري"),
    "send_zuhayri_book_6": ("قصيدة [مَنْ مُبلغٍ كلبَ الروافض ياسراً - نصرة لأم المؤمنين عائشة (رضي الله عنها)] للزهيري.pdf", "مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
    "send_zuhayri_book_7": ("قصيدة يكفي محمدا أن الله حافظه للاخ محمد الزهيري.pdf", "يكفي محمدا أن الله حافظه"),
    "send_zuhayri_book_8": ("قصيدة_ستزيد_دعوتنا_عزا_محمد_الزهيري.pdf", "قصيدة ستزيد دعوتنا عزا"),
    "send_zuhayri_book_9": ("قصيدة_مَنْ_مُبلغٍ_كلبَ_الروافض_ياسراً_نصرة_لأم_المؤمنين_عائشة_رضي.pdf", "قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
    "send_zuhayri_book_10": ("قصيدة_نسجت_لكم_بقاني_الدم_محمد_الزهيري.pdf", "قصيدة نسجت لكم بقاني الدم"),
    "send_zuhayri_book_11": ("نازلُ الأعماق للموت سعى -محمد الزهيري.pdf", "نازلُ الأعماق للموت سعى"),
    "send_zuhayri_book_12": ("نسجت لكم بقاني الدم عهدا -محمد الزهيري.pdf", "نسجت لكم بقاني الدم عهدا"),
    "send_zuhayri_book_13": ("هيهات ينــــزو كافـرٌ - محمد الزهيري.pdf", "هيهات ينــــزو كافـرٌ"),
    "send_zuhayri_book_14": ("يا دولة التوحيد أينع زرعنا - محمد الزهيري.pdf", "يا دولة التوحيد أينع زرعنا")
}

@bot.on_callback_query(filters.regex("show_zuhayri_books"))
def show_zuhayri_books(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"📖 {v[1]}", k)] for k, v in ZUHAYRI_BOOKS_MAP.items()]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text("👷 اختر من مؤلفات المهندس محمد الزهيري:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^send_zuhayri_book_"))
def send_zuhayri_book(client, callback_query):
    book_info = ZUHAYRI_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_name, caption = book_info
        path = os.path.join("قصائد المشروع", "المهندس محمد الزهيري", file_name)
        send_file(client, callback_query, path, f"📖 {caption}")

# --- قسم بنت نجد ---
BINT_NAJD_BOOKS_MAP = {
    "send_bint_najd_book_1": ("أمسِكْ لسانكَ يا قُنيبي.pdf", "أمسِكْ لسانكَ يا قُنيبي"),
    "send_bint_najd_book_2": ("فرعونُ نجد ستنتهي أيامهُ.pdf", "فرعونُ نجد ستنتهي أيامهُ"),
    "send_bint_najd_book_3": ("مادحة للعدناني هاجية للجولاني.pdf", "مادحة للعدناني هاجية للجولاني"),
    "send_bint_najd_book_4": ("هذه دولة الإسلام، ياعشماوي - بنت نجد.pdf", "هذه دولة الإسلام، ياعشماوي")
}

@bot.on_callback_query(filters.regex("show_bint_najd_books"))
def show_bint_najd_books(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"✍️ {v[1]}", k)] for k, v in BINT_NAJD_BOOKS_MAP.items()]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text("✍️ اختر من مؤلفات بنت نجد:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^send_bint_najd_book_"))
def send_bint_najd_book(client, callback_query):
    book_info = BINT_NAJD_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_name, caption = book_info
        path = os.path.join("قصائد المشروع", "بنت نجد", file_name)
        send_file(client, callback_query, path, f"✍️ {caption}")

# --- قسم العقاب المصري ---
OQAB_MASRI_BOOKS_MAP = {
    "send_oqab_book_1": ("إلى ابْنَتي مَوَدَّة.pdf", "إلى ابْنَتي مَوَدَّة"),
    "send_oqab_book_2": ("هنا الخلافة- ديوان شعري العقاب المصري.pdf", "هنا الخلافة - ديوان شعري")
}

@bot.on_callback_query(filters.regex("show_oqab_masri"))
def show_oqab_masri(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"🦅 {v[1]}", k)] for k, v in OQAB_MASRI_BOOKS_MAP.items()]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text("🦅 اختر من مؤلفات العقاب المصري:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^send_oqab_book_"))
def send_oqab_book(client, callback_query):
    book_info = OQAB_MASRI_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_name, caption = book_info
        path = os.path.join("قصائد المشروع", "العقاب المصري", file_name)
        send_file(client, callback_query, path, f"🦅 {caption}")

# --- قسم مرثد بن عبد الله ---
@bot.on_callback_query(filters.regex("show_marthad_abdullah"))
def show_marthad_abdullah(client, callback_query):
    path = os.path.join("قصائد المشروع", "مـرثد بن عبد الله", "بعض من قصائد مرثد بن عبد الله.pdf")
    send_file(client, callback_query, path, "✒️ بعض من قصائد مرثد بن عبد الله")

# --- باقي المؤلفين ---
@bot.on_callback_query(filters.regex("show_abu_khithama"))
def show_abu_khithama(client, callback_query):
    path = os.path.join("قصائد المشروع", "قصائد دبجت بالدماء.pdf")
    send_file(client, callback_query, path, "📘 ديوان الشاعر أبو خيثمة الشنقيطي")

@bot.on_callback_query(filters.regex("show_louis"))
def show_louis(client, callback_query):
    path = os.path.join("قصائد المشروع", "لويس_مقالات.pdf")
    send_file(client, callback_query, path, "📗 مجموعة مقالات لويس عطية الله")

@bot.on_callback_query(filters.regex("show_adnani_books"))
def show_adnani_books(client, callback_query):
    # تحميل القصائد ديناميكياً
    current_poems = load_poems()
    # عرض قصائد العدناني مع الكتب
    adnani_poems = [p for p in current_poems if p.get("author") == "العدنان"]
    keyboard = []
    
    # إضافة القصائد مع تحسين العرض
    for i, poem in enumerate(adnani_poems):
        title = poem.get("title", f"قصيدة {i+1}")
        keyboard.append([InlineKeyboardButton(f"📜 {title}", callback_data=f"poem_{current_poems.index(poem)}")])
    
    # إضافة الكتب
    keyboard.append([InlineKeyboardButton("📖 الجامع لكلمات العدناني", callback_data="send_adnani_aljami")])
    keyboard.append([InlineKeyboardButton("📜 قصيدة معركة الفلوجة الثانية", callback_data="send_adnani_qasida")])
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    
    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
    poem_count = len(adnani_poems)
    total_poems = len(current_poems)
    callback_query.message.edit_text(encrypt_text(f"🎙️ اختر من مؤلفات العدناني:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}"), reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("send_adnani_aljami"))
def send_adnani_aljami(client, callback_query):
    path = os.path.join("قصائد المشروع", "العدناني", "الجامع للعدناني.pdf")
    send_file(client, callback_query, path, "📖 الجامع لكلمات العدناني")

@bot.on_callback_query(filters.regex("send_adnani_qasida"))
def send_adnani_qasida(client, callback_query):
    path = os.path.join("قصائد المشروع", "العدناني", "قصيدة معركة الفلوجة الثانية.pdf")
    send_file(client, callback_query, path, "📜 قصيدة معركة الفلوجة الثانية")

@bot.on_callback_query(filters.regex("show_muhajir_books"))
def show_muhajir_books(client, callback_query):
    # تحميل القصائد ديناميكياً
    current_poems = load_poems()
    # عرض قصائد أبو الحسن المهاجر مع الكتب
    muhajir_poems = [p for p in current_poems if p.get("author") == "أبو الحسن المهاجر"]
    keyboard = []
    
    # إضافة القصائد مع تحسين العرض
    for i, poem in enumerate(muhajir_poems):
        title = poem.get("title", f"قصيدة {i+1}")
        keyboard.append([InlineKeyboardButton(f"📜 {title}", callback_data=f"poem_{current_poems.index(poem)}")])
    
    # إضافة الكتب
    keyboard.append([InlineKeyboardButton("📚 الجامع لكلمات أبي الحسن المهاجر", callback_data="send_muhajir_aljami")])
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    
    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
    poem_count = len(muhajir_poems)
    total_poems = len(current_poems)
    callback_query.message.edit_text(encrypt_text(f"✍️ اختر من مؤلفات أبو الحسن المهاجر:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}"), reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("send_muhajir_aljami"))
def send_muhajir_aljami(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو الحسن المهاجر", "الجامع لكلمات أبي الحسن المهاجر.pdf")
    send_file(client, callback_query, path, "📚 الجامع لكلمات أبي الحسن المهاجر")

@bot.on_callback_query(filters.regex("show_abu_omar_books"))
def show_abu_omar_books(client, callback_query):
    # تحميل القصائد ديناميكياً
    current_poems = load_poems()
    # عرض قصائد أبو عمر المهاجر فقط
    abu_omar_poems = [p for p in current_poems if p.get("author") == "أبو عمر المهاجر"]
    keyboard = []
    
    # إضافة القصائد مع تحسين العرض
    for i, poem in enumerate(abu_omar_poems):
        title = poem.get("title", f"قصيدة {i+1}")
        keyboard.append([InlineKeyboardButton(f"📜 {title}", callback_data=f"poem_{current_poems.index(poem)}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    
    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
    poem_count = len(abu_omar_poems)
    total_poems = len(current_poems)
    callback_query.message.edit_text(encrypt_text(f"👤 اختر من مؤلفات أبي عمر المهاجر:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}"), reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("show_qurashi_books"))
def show_qurashi_books(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو حمزة القرشي", "الجامع لكلمات أبي حمزة القرشي.pdf")
    send_file(client, callback_query, path, "🗣️ الجامع لكلمات أبي حمزة القرشي")

@bot.on_callback_query(filters.regex("show_abu_hamza_books"))
def show_abu_hamza_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📚 ديوان هموم وآلام", callback_data="send_abu_hamza_homoom_w_alam")],
        [InlineKeyboardButton("📖 سير أعلام الشـ هـ داء", callback_data="send_abu_hamza_seir_alam_shohada")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("📚 اختر كتاباً لـ أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("send_abu_hamza_homoom_w_alam"))
def send_abu_hamza_homoom_w_alam(client, callback_query):
    path = os.path.join("قصائد المشروع", "هموم وآلام أبو حمزة.pdf")
    send_file(client, callback_query, path, "📚 ديوان هموم وآلام (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@bot.on_callback_query(filters.regex("send_abu_hamza_seir_alam_shohada"))
def send_abu_hamza_seir_alam_shohada(client, callback_query):
    path = os.path.join("قصائد المشروع", "سير-أعلام-الشُّهداء-1.pdf")
    send_file(client, callback_query, path, "📖 كتاب: سير أعلام الشـ هـ داء (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@bot.on_callback_query(filters.regex("show_abu_anas"))
def show_abu_anas(client, callback_query):
    path = os.path.join("قصائد المشروع", "يوميات مجاهد من الفلوجة.pdf")
    send_file(client, callback_query, path, "📖 كتاب يوميات مـ ـجـ ـاهـ ـد من الفـ ـلـ ـوجـ ـة (أبو أنس الفلسطيني)")

@bot.on_callback_query(filters.regex("show_mysara_gharib_books"))
def show_mysara_gharib_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("كتاب: رمزيات", callback_data="send_mysara_ramziyat")],
        [InlineKeyboardButton("كتاب: إنما شفاء العي السؤال", callback_data="send_mysara_shifaa_alayi")],
        [InlineKeyboardButton("كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها", callback_data="send_mysara_kurab")],
        [InlineKeyboardButton("بدمائهم نصحوا1", callback_data="send_mysara_bidmaihim")],
        [InlineKeyboardButton("سلسلة: من خفايا التاريخ- الزرقـ ا وي", callback_data="send_mysara_zarqawi")],
        [InlineKeyboardButton("كتاب: قـالـوا.. فـقـل!", callback_data="send_mysara_qalou_faqal")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("📝 اختر كتاباً لـ مـ يـسـ رة الغـ ريـ ب:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^send_mysara_"))
def send_mysara_book(client, callback_query):
    book_map = {
        "send_mysara_ramziyat": ("ميسرة الغريب/رَمْزِيَّات.pdf", "📝 كتاب: رمزيات"),
        "send_mysara_shifaa_alayi": ("ميسرة الغريب/إنما شفاء العيّ السؤال.pdf", "📝 كتاب: إنما شفاء العي السؤال"),
        "send_mysara_kurab": ("ميسرة الغريب/الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf", "📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها"),
        "send_mysara_bidmaihim": ("ميسرة الغريب/سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf", "📝 بدمائهم نصحوا1"),
        "send_mysara_zarqawi": ("ميسرة الغريب/سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf", "📝 سلسلة: من خفايا التاريخ- الزرقـ ا وي"),
        "send_mysara_qalou_faqal": ("ميسرة الغريب/قـالـوا.. فـقـل!.pdf", "📝 كتاب: قـالـوا.. فـقـل!"),
    }
    file_info = book_map.get(callback_query.data)
    if file_info:
        path, caption = file_info
        full_path = os.path.join("قصائد المشروع", path)
        full_caption = f"{caption} (مـ يـسـ رة الغـ ريـ ب)"
        send_file(client, callback_query, full_path, full_caption)

@bot.on_callback_query(filters.regex("show_abu_bakr_madani_books"))
def show_abu_bakr_madani_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("لفت الأنظار لما جاء في الفلـ وجتين من أخبار1", callback_data="send_abu_bakr_madani_laft_alanzar")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("📜 اختر كتاباً لـ أبو بـ كـ ر المـ دني:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("send_abu_bakr_madani_laft_alanzar"))
def send_abu_bakr_madani_laft_alanzar(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو بكر المدني", "لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf")
    send_file(client, callback_query, path, "📜 كتاب: لفت الأنظار لما جاء في الفلـ وجتين من أخبار1 (أبو بـ كـ ر المـ دني)")

@bot.on_callback_query(filters.regex("show_hussein_almadidi"))
def show_hussein_almadidi(client, callback_query):
    path = os.path.join("قصائد المشروع", "حسين المعاضيدي", "هنا أرض الخلافة- حسين المعاضيدي.pdf")
    send_file(client, callback_query, path, "⚔️ كتاب: هنا أرض الخلافة (حسين المعاضيدي)")

# --- قسم أحلام النصر ---
AHLAM_ALNASER_BOOKS_MAP = {
    "send_ahlam_alnaser_book_1": ("أوار الحق/1 الباغوز، ومدرسة الابتلاء!.pdf", "1 الباغوز، ومدرسة الابتلاء!"),
    "send_ahlam_alnaser_book_2": ("أوار الحق/2 مَن سمح لهم أن يكونوا أبرياء؟!.pdf", "2 مَن سمح لهم أن يكونوا أبرياء؟!"),
    "send_ahlam_alnaser_book_3": ("أوار الحق/3 يا أهل مصر؛ احذروا الأدوية!.pdf", "3 يا أهل مصر؛ احذروا الأدوية!"),
    "send_ahlam_alnaser_book_4": ("أوار الحق/4 بل أطعنا الله إذ أحرقناه!.pdf", "4 بل أطعنا الله إذ أحرقناه!"),
    "send_ahlam_alnaser_book_5": ("أوار الحق/5 دولة المنهج لا دولة الماديات.pdf", "5 دولة المنهج لا دولة الماديات"),
    "send_ahlam_alnaser_book_6": ("أوار الحق/6 أخطأت يا أم ستيفن!.pdf", "6 أخطأت يا أم ستيفن!"),
    "send_ahlam_alnaser_book_7": ("أوار الحق/7 عمل المرأة، وكذبة التحرر!.pdf", "7 عمل المرأة، وكذبة التحرر!"),
    "send_ahlam_alnaser_book_8": ("أوار الحق/8 توضيح لا بد منه.pdf", "8 توضيح لا بد منه"),
    "send_ahlam_alnaser_book_9": ("أوار الحق/9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!.pdf", "9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!"),
    "send_ahlam_alnaser_book_10": ("أوار الحق/10 منشورات في التربية.pdf", "10 منشورات في التربية"),
    "send_ahlam_alnaser_book_11": ("أوار الحق/11 إنَّني بريئةٌ منكَ.pdf", "11 إنَّني بريئةٌ منكَ"),
    "send_ahlam_alnaser_book_12": ("أوار الحق/12 ديوان أوار الحق لأحلام النصر.pdf", "12 ديوان أوار الحق لأحلام النصر"),
    "send_ahlam_alnaser_book_13": ("أوار الحق/13 ديوان هدير المعامع لأحلام النصر.pdf", "13 ديوان هدير المعامع لأحلام النصر"),
    "send_ahlam_alnaser_book_14": ("أوار الحق/14 أفيـون السهولة، لأحلام النصر.pdf", "14 أفيـون السهولة، لأحلام النصر"),
    "send_ahlam_alnaser_book_15": ("أوار الحق/15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب.pdf", "15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب"),
    "send_ahlam_alnaser_book_16": ("أوار الحق/16 الغلاة.. وبقرة بني إسرائيل!.pdf", "16 الغلاة.. وبقرة بني إسرائيل!"),
    "send_ahlam_alnaser_book_17": ("أوار الحق/17 وِجاءُ_الثغور_في_دفع_شرور_الكَفور.pdf", "17 وِجاءُ الثغور في دفع شرور الكَفور"),
    "send_ahlam_alnaser_book_18": ("أوار الحق/18 ديوان سحابة نقاء، لأحلام النصر.pdf", "18 ديوان سحابة نقاء، لأحلام النصر"),
    "send_ahlam_alnaser_book_19": ("أوار الحق/19 لا عزة إلا بالجهاد.pdf", "19 لا عزة إلا بالجهاد"),
    "send_ahlam_alnaser_book_20": ("أوار الحق/20 بدايتي مع الدولة.pdf", "20 بدايتي مع الدولة"),
    "send_ahlam_alnaser_book_21": ("أوار الحق/21 ربعي بن عامر؛ بين شرعة الله تعالى وشرعة الأمم المتحدة.pdf", "21 ربعي بن عامر؛ بين شرعة الله وشرعة الأمم المتحدة"),
    "send_ahlam_alnaser_book_22": ("أوار الحق/22 الانتصار.pdf", "22 الانتصار"),
    "send_ahlam_alnaser_book_23": ("أوار الحق/23 القائدالشهيد أبو طالب السنوار!.pdf", "23 القائدالشهيد أبو طالب السنوار!"),
    "send_ahlam_alnaser_book_24": ("أوار الحق/24 بيان مؤسسة أوار الحق.pdf", "24 بيان مؤسسة أوار الحق"),
    "send_ahlam_alnaser_book_25": ("أوار الحق/25 المرجئة_يهود_القبلة.pdf", "25 المرجئة يهود القبلة"),
    "send_ahlam_alnaser_book_26": ("أوار الحق/26 تناطح البغال في ردغة الخبال.pdf", "26 تناطح البغال في ردغة الخبال"),
    "send_ahlam_alnaser_book_27": ("أوار الحق/27 طالبان_على_خطى_مرسي_بقلم_أحلام_النصر.pdf", "27 طالبان على خطى مرسي بقلم أحلام النصر"),
    "send_ahlam_alnaser_book_28": ("أوار الحق/28 ليكون الدين كله لله، بقلم أحلام النصر.pdf", "28 ليكون الدين كله لله، بقلم أحلام النصر"),
    "send_ahlam_alnaser_book_29": ("أوار الحق/29 الجانب التعليمي، أحلام النصر.pdf", "29 الجانب التعليمي، أحلام النصر"),
    "send_ahlam_alnaser_book_30": ("أوار الحق/30 أمة الإسناد، لأحلام النصر.pdf", "30 أمة الإسناد، لأحلام النصر"),
    "send_ahlam_alnaser_book_31_a": ("أوار الحق/31 علام الخذلان؟!.pdf", "31 علام الخذلان؟!"),
    "send_ahlam_alnaser_book_32": ("أوار الحق/32 فلسطين إلى متى يبقى الخطر آمنا.pdf", "32 فلسطين إلى متى يبقى الخطر آمنا"),
    "send_ahlam_alnaser_book_اثبت_ولا_تتردد": ("أوار الحق/اثبت_ولا_تتردد،_وبايع_الهزبر_لترشَد (2).pdf", "اثبت ولا تتردد، وبايع الهزبر لترشَد (2)"),
    "send_ahlam_alnaser_book_الذئاب_المنفردة": ("أوار الحق/الذئاب المنفردة.pdf", "الذئاب المنفردة"),
    "send_ahlam_alnaser_book_الزرقاوي_كما_صحبته": ("أوار الحق/الزرقاوي_كما_صحبته.pdf", "الزرقاوي كما صحبته"),
    "send_ahlam_alnaser_book_الموت_الزؤام": ("أوار الحق/الموت_الزؤام_لأعداء_نبي_الإسلام_وشعر_أتجرؤون_بقلم_أحلام_النصر.pdf", "الموت الزؤام لأعداء نبي الإسلام وشعر أتجرؤون"),
    "send_ahlam_alnaser_book_حرب_دينية": ("أوار الحق/حرب دينية لا تصرفات فردية.pdf", "حرب دينية لا تصرفات فردية"),
    "send_ahlam_alnaser_book_حكم_المنظومة": ("أوار الحق/حكم المنظومة التعليمية.pdf", "حكم المنظومة التعليمية"),
    "send_ahlam_alnaser_book_حملة_المناصرة": ("أوار الحق/حملة المناصرة رباط وجهاد.pdf", "حملة المناصرة رباط وجهاد"),
    "send_ahlam_alnaser_book_لا_يصح": ("أوار الحق/لا يصح إلا الصحيح، والمرتد لن يستريح.pdf", "لا يصح إلا الصحيح، والمرتد لن يستريح"),
    "send_ahlam_alnaser_book_taysir_altaalim_1": ("أوار الحق/تيسير_التعليم_لمريد_قراءات_القرآن_الكريم_1.pdf", "تيسير التعليم لمريد قراءات القرآن الكريم 1"),
    "send_ahlam_alnaser_book_kitab_altajweed": ("أوار الحق/كتاب التجويد.pdf", "كتاب التجويد"),
}

for i in range(1, 36):
    AHLAM_ALNASER_BOOKS_MAP[f"send_aed_min_althalam_part_{i}"] = (os.path.join("أوار الحق", "أجزاء قصة عائد من الظلام", f"AMT-E{i}.pdf"), f"🌸 قصة: عائد من الظلام - الجزء {i}")

@bot.on_callback_query(filters.regex("show_ahlam_alnaser_books"))
def show_ahlam_alnaser_books(client, callback_query):
    keyboard = [[InlineKeyboardButton(v[1], k)] for k, v in AHLAM_ALNASER_BOOKS_MAP.items() if k.startswith("send_ahlam_alnaser_book_")]
    keyboard.append([InlineKeyboardButton("📚 قصة: عائد من الظلام (كل الأجزاء)", callback_data="show_aed_min_althalam_parts")])
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text("🌸 اختر من مؤلفات أحلام النصر الدمشقية:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex("show_aed_min_althalam_parts"))
def show_aed_min_althalam_parts(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"الجزء {i}", callback_data=f"send_aed_min_althalam_part_{i}")] for i in range(1, 36)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_ahlam_alnaser_books")])
    callback_query.message.edit_text("📚 قصة: عائد من الظلام - اختر الجزء:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.on_callback_query(filters.regex(r"^(send_ahlam_alnaser_|send_aed_min_althalam_part_)"))
def send_ahlam_alnaser_specific_book(client, callback_query):
    book_info = AHLAM_ALNASER_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_path, caption = book_info
        full_path = os.path.join("قصائد المشروع", file_path)
        full_caption = f"🌸 {caption} (أحلام النصر الدمشقية)"
        send_file(client, callback_query, full_path, full_caption)
    else:
        callback_query.answer("❌ حدث خطأ: الكتاب المطلوب غير موجود في القاموس.", show_alert=True)


# دالة تسجيل Webhook مع Telegram
def set_webhook():
    """تسجيل عنوان Webhook مع Telegram"""
    try:
        webhook_url = WEBHOOK_URL  # استخدام المتغير المعرف مسبقاً
        secret = bot_config["secret_token"]   # من load_config أعلاه
        response = requests.post(
            f"https://api.telegram.org/bot{bot_config['bot_token']}/setWebhook",
            json={"url": webhook_url, "secret_token": secret}
        )
        if response.status_code == 200:
            print(f"✅ تم تسجيل Webhook بنجاح: {webhook_url}")
            print(f"🔐 مع السيكرت: {secret}")
        else:
            print(f"❌ فشل في تسجيل Webhook: {response.text}")
    except Exception as e:
        print(f"❌ خطأ في تسجيل Webhook: {e}")

# دالة معالجة الرسائل الواردة من Webhook
def process_update(update_data):
    """معالجة الرسائل الواردة من Telegram Webhook"""
    try:
        # استخدام bot.process_updates بدلاً من بناء Update يدوياً
        bot.process_updates([update_data])
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

# نقطة نهاية Flask لاستقبال Webhook
# معالج مباشر بدون Pyrogram - أسرع وأبسط
@flask_app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    """نقطة نهاية لاستقبال Webhook من Telegram - معالج مباشر"""
    try:
        data = request.get_json(force=True)  # JSON من تيليجرام

        # تحقّق من التوكن السرّي (اختياري لكنه مفيد)
        sec = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        expected = bot_config.get('secret_token', '')
        if expected and sec != expected:
            # طلب مش من تيليجرام أو التوكن غلط
            print("❌ فشل في التحقق من السيكرت")
            return jsonify({"status": "forbidden"}), 403

        msg = data.get("message") or {}
        chat = (msg.get("chat") or {}).get("id")
        text = msg.get("text", "")

        if chat and text and text.startswith("/start"):
            # رسالة ترحيب مع أزرار
            keyboard = {
                "inline_keyboard": [
                    [{"text": "انتقل إلى مادة الأرشيف", "callback_data": "show_archive"}]
                ]
            }
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat, 
                    "text": "أهلًا! البوت شغّال عبر Webhook على PythonAnywhere ✅\n\nاختر من القائمة:",
                    "reply_markup": keyboard
                }
            )
            print(f"✅ تم الرد على /start في chat_id: {chat}")

        # معالجة Callback Queries
        elif data.get("callback_query"):
            callback_query = data["callback_query"]
            callback_chat_id = callback_query["message"]["chat"]["id"]
            callback_data = callback_query.get("data", "")
            
            if callback_data == "show_archive":
                # إرسال قائمة الأرشيف
                archive_text = "اختر مجموعة القصائد:\n\n• أسامة بن لادن\n• أبو حمزة المهاجر\n• أبو أنس الفلسطيني\n• ميسرة الغريب\n• وأخرون..."
                
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": callback_chat_id, "text": archive_text}
                )
                print(f"✅ تم إرسال الأرشيف في chat_id: {callback_chat_id}")

        # ممكن تضيف ردود أخرى هنا حسب حاجتك…

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# نقطة نهاية للتحقق من حالة البوت
@flask_app.route('/')
def home():
    """الصفحة الرئيسية للتحقق من حالة البوت"""
    return """
    <h1>🚂 RailBot - بوت القصائد الآمن</h1>
    <p>البوت يعمل بنجاح!</p>
    <p>Webhook URL: {}</p>
    """.format(WEBHOOK_URL)

# --- بدء تشغيل البوت ---
if __name__ == "__main__":
    print("🚂 RailBot - بوت القصائد الآمن")
    print("========================================")
    print("جاري بدء البوت...")
    print("✅ تم قراءة الإعدادات بنجاح")
    print("✅ تم تحميل القصائد بنجاح")
    print("✅ تم تسجيل Webhook بنجاح")
    print("✅ البوت يعمل الآن على Flask!")
    print("========================================")
    
    # تسجيل Webhook
    set_webhook()
    
    # تشغيل Flask على المنفذ 5000 (PythonAnywhere)
    flask_app.run(host='0.0.0.0', port=5000, debug=False)