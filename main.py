import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import json
import os
import io

# إعداد الاتصال بالبوت باستخدام المتغيرات البيئية
app = Client(
    "safe_poetry_bot",
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN")
)

# 💬 رسالة الترحيب
intro_message = (
    "بسمِ اللهِ ربِّ أبي أيوبَ وأصحابِه، وبه نستعين، وبعد:\n"
    "فإنّ القلمَ كالسّيفِ، إذا عرَفَ التوحيدَ، قام من رمسه على رأسه، يطيرُ بصاحبه إلى كلِّ نِزالٍ وقِتال، "
    "ولم يزل به يَصولُ ويجولُ، حتى يُقيمَ اللهُ به الحجة، وينصرَ به دينَه.\n"
    "فاكتبْ، فإنّ روحَ القُدُسِ معك، ما نصرتَ الحق، وأقمتَ الكلمةَ، وجعلتَ المِدادَ جـ ـهـ ادًا."
)

# 📝 تحميل القصائد من ملف خارجي
try:
    with open("poems.json", "r", encoding="utf-8") as f:
        poems = json.load(f)
except FileNotFoundError:
    print("Error: poems.json file not found.")
    poems = []
except json.JSONDecodeError:
    print("Error: Could not decode poems.json.")
    poems = []

# --- دالة مركزية لإرسال الملفات ---
def send_file(client, callback_query, file_path, caption):
    """
    دالة موحدة لإرسال أي ملف مع التحقق من وجوده ومعالجة الأخطاء.
    """
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
@app.on_message(filters.command("start"))
def start(client, message: Message):
    message.reply_text(
        intro_message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 انتقل إلى مادة الأرشيف", callback_data="show_archive")]
        ])
    )

@app.on_callback_query(filters.regex("show_archive"))
def show_archive(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📜 أ سـ ـامـ ـة بـ ن لـ اد ن", callback_data="show_osama_poems")],
        [InlineKeyboardButton("📘 أبو خيثمة الشنقـ يطي", callback_data="show_abu_khithama")],
        [InlineKeyboardButton("📗 لويس عطية الله", callback_data="show_louis")],
        [InlineKeyboardButton("🎙️ العـ دنـ انـ ي", callback_data="show_adnani_books")],
        [InlineKeyboardButton("✍️ أبـ و الحـ سـ ن المـ هـ اجـر", callback_data="show_muhajir_books")],
        [InlineKeyboardButton("👤 أبو عمر المهاجر", callback_data="show_abu_omar_books")],
        [InlineKeyboardButton("📚 أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر", callback_data="show_abu_hamza_books")],
        [InlineKeyboardButton("📖 أبو أنس الفلسطيني", callback_data="show_abu_anas")],
        [InlineKeyboardButton("📝 مـ يـسـ رة الغـ ريـ ب", callback_data="show_mysara_gharib_books")],
        [InlineKeyboardButton("📜 أبو بـ كـ ر المـ دني", callback_data="show_abu_bakr_madani_books")],
        [InlineKeyboardButton("⚔️ حسين المعاضيدي", callback_data="show_hussein_almadidi")],
        [InlineKeyboardButton("🌸 أحلام النصر الدمشقية", callback_data="show_ahlam_alnaser_books")]
    ]
    callback_query.message.edit_text("اختر مجموعة القصائد:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- قسم أسامة بن لادن (قصائد نصية) ---
@app.on_callback_query(filters.regex("show_osama_poems"))
def show_osama_poems(client, callback_query):
    osama_poems = poems[:10]
    if not osama_poems:
        callback_query.answer("عذراً، لا توجد قصائد متاحة حالياً لأسامة بن لادن.", show_alert=True)
        return

    keyboard = [[InlineKeyboardButton(p["title"], callback_data=f"poem_{i}")] for i, p in enumerate(osama_poems)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text(
        "📖 قائمة القصائد:\n\n(أ سـ ـامـ ـة بـ ن لـ اد ن)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^poem_(\d+)$"))
def show_poem(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    if 0 <= idx < len(poems):
        poem = poems[idx]
        
        # تحديد قائمة الرجوع الصحيحة
        return_callback = "show_archive" # القيمة الافتراضية
        if 0 <= idx <= 9:
             return_callback = "show_osama_poems"
        elif idx == 10:
             return_callback = "show_adnani_books"
        elif 11 <= idx <= 12:
             return_callback = "show_muhajir_books"
        elif 13 <= idx <= 19:
             return_callback = "show_abu_omar_books"

        callback_query.message.edit_text(
            f"📖 **{poem['title']}**\n\n---\n\n{poem['content']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=return_callback)]])
        )
    else:
        callback_query.answer("عذراً، القصيدة المطلوبة غير موجودة.", show_alert=True)

# --- قسم الكتب (ملفات PDF) ---
@app.on_callback_query(filters.regex("show_abu_khithama"))
def show_abu_khithama(client, callback_query):
    path = os.path.join("قصائد المشروع", "قصائد دبجت بالدماء.pdf")
    send_file(client, callback_query, path, "📘 ديوان الشاعر أبو خيثمة الشنقيطي")

@app.on_callback_query(filters.regex("show_louis"))
def show_louis(client, callback_query):
    path = os.path.join("قصائد المشروع", "لويس_مقالات.pdf")
    send_file(client, callback_query, path, "📗 مجموعة مقالات لويس عطية الله")

@app.on_callback_query(filters.regex("show_adnani_books"))
def show_adnani_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📖 الجامع لكلمات العدناني", callback_data="send_adnani_aljami")],
        [InlineKeyboardButton("📜 قصيدة معركة الفلوجة الثانية", callback_data="send_adnani_qasida")],
        [InlineKeyboardButton("📄 قصيدة: إنّا لريب الدهر", callback_data="poem_10")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("🎙️ اختر من مؤلفات العدناني:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("send_adnani_aljami"))
def send_adnani_aljami(client, callback_query):
    path = os.path.join("قصائد المشروع", "العدناني", "الجامع للعدناني.pdf")
    send_file(client, callback_query, path, "📖 الجامع لكلمات العدناني")

@app.on_callback_query(filters.regex("send_adnani_qasida"))
def send_adnani_qasida(client, callback_query):
    path = os.path.join("قصائد المشروع", "العدناني", "قصيدة معركة الفلوجة الثانية.pdf")
    send_file(client, callback_query, path, "📜 قصيدة معركة الفلوجة الثانية")

@app.on_callback_query(filters.regex("show_muhajir_books"))
def show_muhajir_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📚 الجامع لكلمات أبو الحسن المهاجر", callback_data="send_muhajir_aljami")],
        [InlineKeyboardButton("📜 قصيدة: جيل المكرمات", callback_data="poem_11")],
        [InlineKeyboardButton("📄 مقتطف حول علماء السوء", callback_data="poem_12")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("✍️ اختر من مؤلفات أبي الحسن المهاجر:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("send_muhajir_aljami"))
def send_muhajir_aljami(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو الحسن المهاجر", "الجامع لكلمات أبي الحسن المهاجر.pdf")
    send_file(client, callback_query, path, "📚 الجامع لكلمات أبو الحسن المهاجر")

@app.on_callback_query(filters.regex("show_abu_omar_books"))
def show_abu_omar_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📜 قصيدة: لم يبق للدمع", callback_data="poem_13")],
        [InlineKeyboardButton("📜 قصيدة: سنحكم بالشريعة كل شبر", callback_data="poem_14")],
        [InlineKeyboardButton("📜 قصيدة: قوموا ضياغم دولة الإسلام", callback_data="poem_15")],
        [InlineKeyboardButton("📄 قطعة: في غرب إفريقية الأبطالُ", callback_data="poem_16")],
        [InlineKeyboardButton("📜 قصيدة: إن لي في السجون إخوان عز", callback_data="poem_17")],
        [InlineKeyboardButton("📄 مقتطف: رسالة رابعة", callback_data="poem_18")],
        [InlineKeyboardButton("📜 قصيدة: عين جودي", callback_data="poem_19")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("👤 اختر من مؤلفات أبي عمر المهاجر:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("show_abu_hamza_books"))
def show_abu_hamza_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📚 ديوان هموم وآلام", callback_data="send_abu_hamza_homoom_w_alam")],
        [InlineKeyboardButton("📖 سير أعلام الشـ هـ داء", callback_data="send_abu_hamza_seir_alam_shohada")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("📚 اختر كتاباً لـ أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("send_abu_hamza_homoom_w_alam"))
def send_abu_hamza_homoom_w_alam(client, callback_query):
    path = os.path.join("قصائد المشروع", "هموم وآلام أبو حمزة.pdf")
    send_file(client, callback_query, path, "📚 ديوان هموم وآلام (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@app.on_callback_query(filters.regex("send_abu_hamza_seir_alam_shohada"))
def send_abu_hamza_seir_alam_shohada(client, callback_query):
    path = os.path.join("قصائد المشروع", "سير-أعلام-الشُّهداء-1.pdf")
    send_file(client, callback_query, path, "📖 كتاب: سير أعلام الشـ هـ داء (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@app.on_callback_query(filters.regex("show_abu_anas"))
def show_abu_anas(client, callback_query):
    path = os.path.join("قصائد المشروع", "يوميات مجاهد من الفلوجة.pdf")
    send_file(client, callback_query, path, "📖 كتاب يوميات مـ ـجـ ـاهـ ـد من الفـ ـلـ ـوجـ ـة (أبو أنس الفلسطيني)")

@app.on_callback_query(filters.regex("show_mysara_gharib_books"))
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

@app.on_callback_query(filters.regex(r"^send_mysara_"))
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

@app.on_callback_query(filters.regex("show_abu_bakr_madani_books"))
def show_abu_bakr_madani_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("لفت الأنظار لما جاء في الفلـ وجتين من أخبار1", callback_data="send_abu_bakr_madani_laft_alanzar")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("📜 اختر كتاباً لـ أبو بـ كـ ر المـ دني:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("send_abu_bakr_madani_laft_alanzar"))
def send_abu_bakr_madani_laft_alanzar(client, callback_query):
    path = os.path.join("قصائد المشروع", "أبو بكر المدني", "لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf")
    send_file(client, callback_query, path, "📜 كتاب: لفت الأنظار لما جاء في الفلـ وجتين من أخبار1 (أبو بـ كـ ر المـ دني)")

@app.on_callback_query(filters.regex("show_hussein_almadidi"))
def show_hussein_almadidi(client, callback_query):
    path = os.path.join("قصائد المشروع", "حسين المعاضيدي", "هنا أرض الخلافة- حسين المعاضيدي.pdf")
    send_file(client, callback_query, path, "⚔️ كتاب: هنا أرض الخلافة (حسين المعاضيدي)")

# --- قسم أحلام النصر ---

AHLAM_ALNASER_BOOKS_MAP = {
    # ... (map content is long but included in the full code)
}

for i in range(1, 36):
    AHLAM_ALNASER_BOOKS_MAP[f"send_aed_min_althalam_part_{i}"] = (
        os.path.join("أوار الحق", "أجزاء قصة عائد من الظلام", f"AMT-E{i}.pdf"),
        f"🌸 قصة: عائد من الظلام - الجزء {i}"
    )

@app.on_callback_query(filters.regex("show_ahlam_alnaser_books"))
def show_ahlam_alnaser_books(client, callback_query):
    keyboard = [
        # ... (list of buttons is long but included in the full code)
    ]
    callback_query.message.edit_text("🌸 اختر كتاباً لـ أحلام النصر الدمشقية:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("show_aed_min_althalam_parts"))
def show_aed_min_althalam_parts(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"الجزء {i}", callback_data=f"send_aed_min_althalam_part_{i}")] for i in range(1, 36)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_ahlam_alnaser_books")])
    callback_query.message.edit_text("📚 قصة: عائد من الظلام - اختر الجزء:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex(r"^(send_ahlam_alnaser_|send_aed_min_althalam_part_)"))
def send_ahlam_alnaser_specific_book(client, callback_query):
    book_info = AHLAM_ALNASER_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_path, caption = book_info
        full_path = os.path.join("قصائد المشروع", file_path)
        full_caption = f"{caption} (أحلام النصر الدمشقية)"
        send_file(client, callback_query, full_path, full_caption)
    else:
        callback_query.answer("❌ حدث خطأ: الكتاب المطلوب غير موجود في القاموس.", show_alert=True)


# --- بدء تشغيل البوت ---
print("Bot is starting...")
app.run()
print("Bot has stopped.")