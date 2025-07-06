import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import json
import os # استيراد مكتبة os للتعامل مع المسارات
import io # استيراد مكتبة io للتعامل مع كائنات البايتات كملفات

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
    callback_query.message.edit_text(
        "اختر مجموعة القصائد:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 أ سـ ـامـ ـة بـ ن لـ اد ن", callback_data="show_osama_poems")],
            [InlineKeyboardButton("📘 أبو خيثمة الشنقـ يطي", callback_data="show_abu_khithama")],
            [InlineKeyboardButton("📗 لويس عطية الله", callback_data="show_louis")],
            [InlineKeyboardButton("📚 أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر", callback_data="show_abu_hamza_books")],
            [InlineKeyboardButton("📖 أبو أنس الفلسطيني", callback_data="show_abu_anas")],
            [InlineKeyboardButton("📝 مـ يـسـ رة الغـ ريـ ب", callback_data="show_mysara_gharib_books")],
            [InlineKeyboardButton("📜 أبو بـ كـ ر المـ دني", callback_data="show_abu_bakr_madani_books")],
            [InlineKeyboardButton("🌸 أحلام النصر الدمشقية", callback_data="show_ahlam_alnaser_books")]
        ])
    )

@app.on_callback_query(filters.regex("show_osama_poems"))
def show_osama_poems(client, callback_query):
    if not poems:
        callback_query.answer("عذراً، لا توجد قصائد متاحة حالياً.", show_alert=True)
        return

    keyboard = [[InlineKeyboardButton(p["title"], callback_data=f"poem_{i}")] for i, p in enumerate(poems)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")])
    callback_query.message.edit_text(
        "📖 قائمة القصائد:\n\n(أ سـ ـامـ ـة بـ ن لـ اد ن)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^poem_\d+$"))
def show_poem(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    if 0 <= idx < len(poems):
        poem = poems[idx]
        callback_query.message.edit_text(
            f"📖 {poem['title']}\n\n{poem['content']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ رجوع", callback_data="show_osama_poems")]
            ])
        )
    else:
        callback_query.answer("عذراً، القصيدة المطلوبة غير موجودة.", show_alert=True)

def send_file(client, callback_query, file_path, caption):
    full_path = os.path.join("قصائد المشروع", file_path)
    try:
        if not os.path.exists(full_path):
            error_msg = f"❌ خطأ: لم يتم العثور على الملف: {full_path}"
            print(error_msg)
            callback_query.answer(error_msg, show_alert=True)
            return

        client.send_document(
            chat_id=callback_query.message.chat.id,
            document=full_path,
            caption=caption
        )
        callback_query.answer("✅ تم إرسال الملف بنجاح.")
    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء الإرسال: {e}"
        print(error_msg)
        callback_query.answer(error_msg, show_alert=True)

@app.on_callback_query(filters.regex("show_abu_khithama"))
def show_abu_khithama(client, callback_query):
    send_file(client, callback_query, "قصائد دبجت بالدماء.pdf", "📘 ديوان الشاعر أبو خيثمة الشنقيطي")

@app.on_callback_query(filters.regex("show_louis"))
def show_louis(client, callback_query):
    send_file(client, callback_query, "لويس_مقالات.pdf", "📗 مجموعة مقالات لويس عطية الله")

@app.on_callback_query(filters.regex("show_abu_hamza_books"))
def show_abu_hamza_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📚 ديوان هموم وآلام", callback_data="send_abu_hamza_homoom_w_alam")],
        [InlineKeyboardButton("📖 سير أعلام الشـ هـ داء", callback_data="send_abu_hamza_seir_alam_shohada")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text(
        "📚 اختر كتاباً لـ أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("send_abu_hamza_homoom_w_alam"))
def send_abu_hamza_homoom_w_alam(client, callback_query):
    send_file(client, callback_query, "هموم وآلام أبو حمزة.pdf", "📚 ديوان هموم وآلام (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@app.on_callback_query(filters.regex("send_abu_hamza_seir_alam_shohada"))
def send_abu_hamza_seir_alam_shohada(client, callback_query):
    send_file(client, callback_query, "سير-أعلام-الشُّهداء-1.pdf", "📖 كتاب: سير أعلام الشـ هـ داء (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)")

@app.on_callback_query(filters.regex("show_abu_anas"))
def show_abu_anas(client, callback_query):
    send_file(client, callback_query, "يوميات مجاهد من الفلوجة.pdf", "📖 كتاب يوميات مـ ـجـ ـاهـ ـد من الفـ ـلـ ـوجـ ـة (أبو أنس الفلسطيني)")

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
    callback_query.message.edit_text(
        "📝 اختر كتاباً لـ مـ يـسـ رة الغـ ريـ ب:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("send_mysara_ramziyat"))
def send_mysara_ramziyat(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "رَمْزِيَّات.pdf"), "📝 كتاب: رمزيات (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("send_mysara_shifaa_alayi"))
def send_mysara_shifaa_alayi(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "إنما شفاء العيّ السؤال.pdf"), "📝 كتاب: إنما شفاء العي السؤال (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("send_mysara_kurab"))
def send_mysara_kurab(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf"), "📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("send_mysara_bidmaihim"))
def send_mysara_bidmaihim(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf"), "📝 بدمائهم نصحوا1 (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("send_mysara_zarqawi"))
def send_mysara_zarqawi(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf"), "📝 سلسلة: من خفايا التاريخ- الزرقـ ا وي (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("send_mysara_qalou_faqal"))
def send_mysara_qalou_faqal(client, callback_query):
    send_file(client, callback_query, os.path.join("ميسرة الغريب", "قـالـوا.. فـقـل!.pdf"), "📝 كتاب: قـالـوا.. فـقـل! (مـ يـسـ رة الغـ ريـ ب)")

@app.on_callback_query(filters.regex("show_abu_bakr_madani_books"))
def show_abu_bakr_madani_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("لفت الأنظار لما جاء في الفلـ وجتين من أخبار1", callback_data="send_abu_bakr_madani_laft_alanzar")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text(
        "📜 اختر كتاباً لـ أبو بـ كـ ر المـ دني:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("send_abu_bakr_madani_laft_alanzar"))
def send_abu_bakr_madani_laft_alanzar(client, callback_query):
    send_file(client, callback_query, os.path.join("أبو بكر المدني", "لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf"), "📜 كتاب: لفت الأنظار لما جاء في الفلـ وجتين من أخبار1 (أبو بـ كـ ر المـ دني)")


# Mapping for Ahlam Al-Naser books to avoid repetitive code
AHLAM_ALNASER_BOOKS_MAP = {
    "send_ahlam_alnaser_book_1": ("أوار الحق/1 الباغوز، ومدرسة الابتلاء!.pdf", "🌸 كتاب: 1 الباغوز، ومدرسة الابتلاء!"),
    "send_ahlam_alnaser_book_2": ("أوار الحق/2 مَن سمح لهم أن يكونوا أبرياء؟!.pdf", "🌸 كتاب: 2 مَن سمح لهم أن يكونوا أبرياء؟!"),
    "send_ahlam_alnaser_book_3": ("أوار الحق/3 يا أهل مصر؛ احذروا الأدوية!.pdf", "🌸 كتاب: 3 يا أهل مصر؛ احذروا الأدوية!"),
    "send_ahlam_alnaser_book_4": ("أوار الحق/4 بل أطعنا الله إذ أحرقناه!.pdf", "🌸 كتاب: 4 بل أطعنا الله إذ أحرقناه!"),
    "send_ahlam_alnaser_book_5": ("أوار الحق/5 دولة المنهج لا دولة الماديات.pdf", "🌸 كتاب: 5 دولة المنهج لا دولة الماديات"),
    "send_ahlam_alnaser_book_6": ("أوار الحق/6 أخطأت يا أم ستيفن!.pdf", "🌸 كتاب: 6 أخطأت يا أم ستيفن!"),
    "send_ahlam_alnaser_book_7": ("أوار الحق/7 عمل المرأة، وكذبة التحرر!.pdf", "🌸 كتاب: 7 عمل المرأة، وكذبة التحرر!"),
    "send_ahlam_alnaser_book_8": ("أوار الحق/8 توضيح لا بد منه.pdf", "🌸 كتاب: 8 توضيح لا بد منه"),
    "send_ahlam_alnaser_book_9": ("أوار الحق/9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!.pdf", "🌸 كتاب: 9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!"),
    "send_ahlam_alnaser_book_10": ("أوار الحق/10 منشورات في التربية.pdf", "🌸 كتاب: 10 منشورات في التربية"),
    # ... Add all other books here in the same format
    "send_aed_min_althalam_part_1": (os.path.join("أوار الحق", "أجزاء قصة عائد من الظلام", "AMT-E1.pdf"), "🌸 قصة: عائد من الظلام - الجزء 1"),
    # ... Dynamically generate paths for all 35 parts
}

# Dynamically add all 35 parts of the story to the map
for i in range(1, 36):
    key = f"send_aed_min_althalam_part_{i}"
    path = os.path.join("أوار الحق", "أجزاء قصة عائد من الظلام", f"AMT-E{i}.pdf")
    caption = f"🌸 قصة: عائد من الظلام - الجزء {i}"
    AHLAM_ALNASER_BOOKS_MAP[key] = (path, caption)


@app.on_callback_query(filters.regex("show_ahlam_alnaser_books"))
def show_ahlam_alnaser_books(client, callback_query):
    # This list can be simplified if all books are in the map
    keyboard = [
        [InlineKeyboardButton("1 الباغوز، ومدرسة الابتلاء!", callback_data="send_ahlam_alnaser_book_1")],
        # Add all other buttons...
        [InlineKeyboardButton("📚 قصة: عائد من الظلام", callback_data="show_aed_min_althalam_parts")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text(
        "🌸 اختر كتاباً لـ أحلام النصر الدمشقية:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("show_aed_min_althalam_parts"))
def show_aed_min_althalam_parts(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"الجزء {i}", callback_data=f"send_aed_min_althalam_part_{i}")] for i in range(1, 36)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_ahlam_alnaser_books")])
    callback_query.message.edit_text(
        "📚 قصة: عائد من الظلام - اختر الجزء:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@app.on_callback_query(filters.regex(r"^send_ahlam_alnaser_book_|^send_aed_min_althalam_part_"))
def send_ahlam_alnaser_specific_book(client, callback_query):
    book_info = AHLAM_ALNASER_BOOKS_MAP.get(callback_query.data)
    if book_info:
        file_path, caption = book_info
        full_caption = f"{caption} (أحلام النصر الدمشقية)"
        send_file(client, callback_query, file_path, full_caption)
    else:
        callback_query.answer("❌ حدث خطأ: الكتاب المطلوب غير موجود.", show_alert=True)


print("Bot is starting...")
app.run()
print("Bot has stopped.")