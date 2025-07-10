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
        [InlineKeyboardButton("📚 أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر", callback_data="show_abu_hamza_books")],
        [InlineKeyboardButton("📖 أبو أنس الفلسطيني", callback_data="show_abu_anas")],
        [InlineKeyboardButton("📝 مـ يـسـ رة الغـ ريـ ب", callback_data="show_mysara_gharib_books")],
        [InlineKeyboardButton("📜 أبو بـ كـ ر المـ دني", callback_data="show_abu_bakr_madani_books")],
        [InlineKeyboardButton("⚔️ حسين المعاضيدي", callback_data="show_hussein_almadidi")], # ## التعديل الأول: إضافة الزر الجديد هنا
        [InlineKeyboardButton("🌸 أحلام النصر الدمشقية", callback_data="show_ahlam_alnaser_books")]
    ]
    callback_query.message.edit_text("اختر مجموعة القصائد:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- قسم أسامة بن لادن (قصائد نصية) ---
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="show_osama_poems")]])
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

# ## التعديل الثاني: إضافة دالة جديدة للكتاب الجديد
# ## الدالة الجديدة (الصحيحة)
@app.on_callback_query(filters.regex("show_hussein_almadidi"))
def show_hussein_almadidi(client, callback_query):
    path = os.path.join("قصائد المشروع", "حسين المعاضيدي", "هنا أرض الخلافة- حسين المعاضيدي.pdf") # <-- تم التصحيح
    send_file(client, callback_query, path, "⚔️ كتاب: هنا أرض الخلافة (حسين المعاضيدي)")
# --- قسم أحلام النصر ---

AHLAM_ALNASER_BOOKS_MAP = {
    "send_ahlam_alnaser_book_1": ("أوار الحق/1 الباغوز، ومدرسة الابتلاء!.pdf", "🌸 كتاب: 1 الباغوز، ومدرسة الابتلاء!"),
    "send_ahlam_alnaser_book_2": ("أوار الحق/2 مَن سمح لهم أن يكونوا أبرياء؟!.pdf", "🌸 كتاب: 2 مَن سمح لهم أن يكونوا أبرياء؟!"),
    "send_ahlam_alnaser_book_3": ("أوار الحق/3 يا أهل مصر؛ احذروا الأدوية!.pdf", "🌸 كتاب: 3 يا أهل مصر؛ احذروا الأدوية!"),
    "send_ahlam_alnaser_book_4": ("أوار الحق/4 بل أطعنا الله إذ أحرقناه!.pdf", "🌸 كتاب: 4 بل أطعنا الله إذ أحرقناه!"),
    "send_ahlam_alnaser_book_5": ("أوار الحق/5 دولة المنهج لا دولة الماديات.pdf", "🌸 كتاب: 5 دولة المنهج لا دولة الماديات"),
    "send_ahlam_alnaser_book_6": ("أوار الحق/6 أخطأت يا أم ستيفن!.pdf", "🌸 كتاب: 6 أخطأت يا أم ستيفن!"),
    "send_ahlam_alnaser_book_7": ("أوار الحق/7 عمل المرأة، وكذبة التحرر!.pdf", "🌸 كتاب: 7 عمل المرأة، وكذبة التحرر!"),
    "send_ahlam_alnaser_book_8": ("أوار الحق/8 توضيح لا بد منه.pdf", "🌸 كتاب: 8 توضيح لا بد منه"),
    "send_ahlam_alnaser_book_9": ("أوار الحق/9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!.pdf", "🌸 كتاب: 9 أتينا لنبقى.."),
    "send_ahlam_alnaser_book_10": ("أوار الحق/10 منشورات في التربية.pdf", "🌸 كتاب: 10 منشورات في التربية"),
    "send_ahlam_alnaser_book_11": ("أوار الحق/11 إنَّني بريئةٌ منكَ.pdf", "🌸 كتاب: 11 إنَّني بريئةٌ منكَ"),
    "send_ahlam_alnaser_book_12": ("أوار الحق/12 ديوان أوار الحق لأحلام النصر.pdf", "🌸 كتاب: 12 ديوان أوار الحق"),
    "send_ahlam_alnaser_book_13": ("أوار الحق/13 ديوان هدير المعامع لأحلام النصر.pdf", "🌸 كتاب: 13 ديوان هدير المعامع"),
    "send_ahlam_alnaser_book_14": ("أوار الحق/14 أفيـون السهولة، لأحلام النصر.pdf", "🌸 كتاب: 14 أفيـون السهولة"),
    "send_ahlam_alnaser_book_15": ("أوار الحق/15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب.pdf", "🌸 كتاب: 15 رحلة علم وجهاد"),
    "send_ahlam_alnaser_book_16": ("أوار الحق/16 الغلاة.. وبقرة بني إسرائيل!.pdf", "🌸 كتاب: 16 الغلاة.. وبقرة بني إسرائيل!"),
    "send_ahlam_alnaser_book_17": ("أوار الحق/17 وِجاءُ_الثغور_في_دفع_شرور_الكَفور.pdf", "🌸 كتاب: 17 وِجاءُ الثغور"),
    "send_ahlam_alnaser_book_18": ("أوار الحق/18 ديوان سحابة نقاء، لأحلام النصر.pdf", "🌸 كتاب: 18 ديوان سحابة نقاء"),
    "send_ahlam_alnaser_book_19": ("أوار الحق/19 لا عزة إلا بالجهاد.pdf", "🌸 كتاب: 19 لا عزة إلا بالجهاد"),
    "send_ahlam_alnaser_book_20": ("أوار الحق/20 بدايتي مع الدولة.pdf", "🌸 كتاب: 20 بدايتي مع الدولة"),
    "send_ahlam_alnaser_book_21": ("أوار الحق/21 ربعي بن عامر؛ بين شرعة الله تعالى وشرعة الأمم المتحدة.pdf", "🌸 كتاب: 21 ربعي بن عامر"),
    "send_ahlam_alnaser_book_22": ("أوار الحق/22 الانتصار.pdf", "🌸 كتاب: 22 الانتصار"),
    "send_ahlam_alnaser_book_23": ("أوار الحق/23 القائدالشهيد أبو طالب السنوار!.pdf", "🌸 كتاب: 23 القائدالشهيد أبو طالب السنوار!"),
    "send_ahlam_alnaser_book_24": ("أوار الحق/24 بيان مؤسسة أوار الحق.pdf", "🌸 كتاب: 24 بيان مؤسسة أوار الحق"),
    "send_ahlam_alnaser_book_25": ("أوار الحق/25 المرجئة_يهود_القبلة.pdf", "🌸 كتاب: 25 المرجئة يهود القبلة"),
    "send_ahlam_alnaser_book_26": ("أوار الحق/26 تناطح البغال في ردغة الخبال.pdf", "🌸 كتاب: 26 تناطح البغال في ردغة الخبال"),
    "send_ahlam_alnaser_book_27": ("أوار الحق/27 طالبان_على_خطى_مرسي_بقلم_أحلام_النصر.pdf", "🌸 كتاب: 27 طالبان على خطى مرسي"),
    "send_ahlam_alnaser_book_28": ("أوار الحق/28 ليكون الدين كله لله، بقلم أحلام النصر.pdf", "🌸 كتاب: 28 ليكون الدين كله لله"),
    "send_ahlam_alnaser_book_29": ("أوار الحق/29 الجانب التعليمي، أحلام النصر.pdf", "🌸 كتاب: 29 الجانب التعليمي"),
    "send_ahlam_alnaser_book_30": ("أوار الحق/30 أمة الإسناد، لأحلام النصر.pdf", "🌸 كتاب: 30 أمة الإسناد"),
    "send_ahlam_alnaser_book_31_a": ("أوار الحق/31 علام الخذلان؟!.pdf", "🌸 كتاب: 31 علام الخذلان؟!"),
    "send_ahlam_alnaser_book_32": ("أوار الحق/32 فلسطين إلى متى يبقى الخطر آمنا.pdf", "🌸 كتاب: 32 فلسطين إلى متى يبقى الخطر آمنا"),
    "send_ahlam_alnaser_book_اثبت_ولا_تتردد": ("أوار الحق/اثبت_ولا_تتردد،_وبايع_الهزبر_لترشَد (2).pdf", "🌸 كتاب: اثبت ولا تتردد، وبايع الهزبر لترشَد"),
    "send_ahlam_alnaser_book_الذئاب_المنفردة": ("أوار الحق/الذئاب المنفردة.pdf", "🌸 كتاب: الذئاب المنفردة"),
    "send_ahlam_alnaser_book_الزرقاوي_كما_صحبته": ("أوار الحق/الزرقاوي_كما_صحبته.pdf", "🌸 كتاب: الزرقاوي كما صحبته"),
    "send_ahlam_alnaser_book_الموت_الزؤام": ("أوار الحق/الموت_الزؤام_لأعداء_نبي_الإسلام_وشعر_أتجرؤون_بقلم_أحلام_النصر.pdf", "🌸 كتاب: الموت الزؤام لأعداء نبي الإسلام"),
    "send_ahlam_alnaser_book_حرب_دينية": ("أوار الحق/حرب دينية لا تصرفات فردية.pdf", "🌸 كتاب: حرب دينية لا تصرفات فردية"),
    "send_ahlam_alnaser_book_حكم_المنظومة": ("أوار الحق/حكم المنظومة التعليمية.pdf", "🌸 كتاب: حكم المنظومة التعليمية"),
    "send_ahlam_alnaser_book_حملة_المناصرة": ("أوار الحق/حملة المناصرة رباط وجهاد.pdf", "🌸 كتاب: حملة المناصرة رباط وجهاد"),
    "send_ahlam_alnaser_book_لا_يصح": ("أوار الحق/لا يصح إلا الصحيح، والمرتد لن يستريح.pdf", "🌸 كتاب: لا يصح إلا الصحيح"),
    "send_ahlam_alnaser_book_taysir_altaalim_1": ("أوار الحق/تيسير_التعليم_لمريد_قراءات_القرآن_الكريم_1.pdf", "🌸 كتاب: تيسير التعليم لمريد قراءات القرآن 1"),
    "send_ahlam_alnaser_book_kitab_altajweed": ("أوار الحق/كتاب التجويد.pdf", "🌸 كتاب: كتاب التجويد"),
}

# Dynamically add all 35 parts of the story to the map
for i in range(1, 36):
    AHLAM_ALNASER_BOOKS_MAP[f"send_aed_min_althalam_part_{i}"] = (
        os.path.join("أوار الحق", "أجزاء قصة عائد من الظلام", f"AMT-E{i}.pdf"),
        f"🌸 قصة: عائد من الظلام - الجزء {i}"
    )

@app.on_callback_query(filters.regex("show_ahlam_alnaser_books"))
def show_ahlam_alnaser_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("1 الباغوز، ومدرسة الابتلاء!", callback_data="send_ahlam_alnaser_book_1")],
        [InlineKeyboardButton("2 مَن سمح لهم أن يكونوا أبرياء؟!", callback_data="send_ahlam_alnaser_book_2")],
        [InlineKeyboardButton("3 يا أهل مصر؛ احذروا الأدوية!", callback_data="send_ahlam_alnaser_book_3")],
        [InlineKeyboardButton("4 بل أطعنا الله إذ أحرقناه!", callback_data="send_ahlam_alnaser_book_4")],
        [InlineKeyboardButton("5 دولة المنهج لا دولة الماديات", callback_data="send_ahlam_alnaser_book_5")],
        [InlineKeyboardButton("6 أخطأت يا أم ستيفن!", callback_data="send_ahlam_alnaser_book_6")],
        [InlineKeyboardButton("7 عمل المرأة، وكذبة التحرر!", callback_data="send_ahlam_alnaser_book_7")],
        [InlineKeyboardButton("8 توضيح لا بد منه", callback_data="send_ahlam_alnaser_book_8")],
        [InlineKeyboardButton("9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!", callback_data="send_ahlam_alnaser_book_9")],
        [InlineKeyboardButton("10 منشورات في التربية", callback_data="send_ahlam_alnaser_book_10")],
        [InlineKeyboardButton("11 إنَّني بريئةٌ منكَ", callback_data="send_ahlam_alnaser_book_11")],
        [InlineKeyboardButton("12 ديوان أوار الحق لأحلام النصر", callback_data="send_ahlam_alnaser_book_12")],
        [InlineKeyboardButton("13 ديوان هدير المعامع لأحلام النصر", callback_data="send_ahlam_alnaser_book_13")],
        [InlineKeyboardButton("14 أفيـون السهولة، لأحلام النصر", callback_data="send_ahlam_alnaser_book_14")],
        [InlineKeyboardButton("15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب", callback_data="send_ahlam_alnaser_book_15")],
        [InlineKeyboardButton("16 الغلاة.. وبقرة بني إسرائيل!", callback_data="send_ahlam_alnaser_book_16")],
        [InlineKeyboardButton("17 وِجاءُ الثغور في دفع شرور الكَفور", callback_data="send_ahlam_alnaser_book_17")],
        [InlineKeyboardButton("18 ديوان سحابة نقاء، لأحلام النصر", callback_data="send_ahlam_alnaser_book_18")],
        [InlineKeyboardButton("19 لا عزة إلا بالجهاد", callback_data="send_ahlam_alnaser_book_19")],
        [InlineKeyboardButton("20 بدايتي مع الدولة", callback_data="send_ahlam_alnaser_book_20")],
        [InlineKeyboardButton("21 ربعي بن عامر؛ بين شرعة الله تعالى وشرعة الأمم المتحدة", callback_data="send_ahlam_alnaser_book_21")],
        [InlineKeyboardButton("22 الانتصار", callback_data="send_ahlam_alnaser_book_22")],
        [InlineKeyboardButton("23 القائدالشهيد أبو طالب السنوار!", callback_data="send_ahlam_alnaser_book_23")],
        [InlineKeyboardButton("24 بيان مؤسسة أوار الحق", callback_data="send_ahlam_alnaser_book_24")],
        [InlineKeyboardButton("25 المرجئة يهود القبلة", callback_data="send_ahlam_alnaser_book_25")],
        [InlineKeyboardButton("26 تناطح البغال في ردغة الخبال", callback_data="send_ahlam_alnaser_book_26")],
        [InlineKeyboardButton("27 طالبان على خطى مرسي بقلم أحلام النصر", callback_data="send_ahlam_alnaser_book_27")],
        [InlineKeyboardButton("28 ليكون الدين كله لله، بقلم أحلام النصر", callback_data="send_ahlam_alnaser_book_28")],
        [InlineKeyboardButton("29 الجانب التعليمي، أحلام النصر", callback_data="send_ahlam_alnaser_book_29")],
        [InlineKeyboardButton("30 أمة الإسناد، لأحلام النصر", callback_data="send_ahlam_alnaser_book_30")],
        [InlineKeyboardButton("31 علام الخذلان؟!", callback_data="send_ahlam_alnaser_book_31_a")],
        [InlineKeyboardButton("32 فلسطين إلى متى يبقى الخطر آمنا", callback_data="send_ahlam_alnaser_book_32")],
        [InlineKeyboardButton("اثبت ولا تتردد، وبايع الهزبر لترشَد (2)", callback_data="send_ahlam_alnaser_book_اثبت_ولا_تتردد")],
        [InlineKeyboardButton("الذئاب المنفردة", callback_data="send_ahlam_alnaser_book_الذئاب_المنفردة")],
        [InlineKeyboardButton("الزرقاوي كما صحبته", callback_data="send_ahlam_alnaser_book_الزرقاوي_كما_صحبته")],
        [InlineKeyboardButton("الموت الزؤام لأعداء نبي الإسلام وشعر أتجرؤون بقلم أحلام النصر", callback_data="send_ahlam_alnaser_book_الموت_الزؤام")],
        [InlineKeyboardButton("حرب دينية لا تصرفات فردية", callback_data="send_ahlam_alnaser_book_حرب_دينية")],
        [InlineKeyboardButton("حكم المنظومة التعليمية", callback_data="send_ahlam_alnaser_book_حكم_المنظومة")],
        [InlineKeyboardButton("حملة المناصرة رباط وجهاد", callback_data="send_ahlam_alnaser_book_حملة_المناصرة")],
        [InlineKeyboardButton("لا يصح إلا الصحيح، والمرتد لن يستريح", callback_data="send_ahlam_alnaser_book_لا_يصح")],
        [InlineKeyboardButton("تيسير التعليم لمريد قراءات القرآن الكريم 1", callback_data="send_ahlam_alnaser_book_taysir_altaalim_1")],
        [InlineKeyboardButton("كتاب التجويد", callback_data="send_ahlam_alnaser_book_kitab_altajweed")],
        [InlineKeyboardButton("📚 قصة: عائد من الظلام", callback_data="show_aed_min_althalam_parts")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text("🌸 اختر كتاباً لـ أحلام النصر الدمشقية:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("show_aed_min_althalam_parts"))
def show_aed_min_althalam_parts(client, callback_query):
    keyboard = [[InlineKeyboardButton(f"الجزء {i}", callback_data=f"send_aed_min_althalam_part_{i}")] for i in range(1, 36)]
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_ahlam_alnaser_books")])
    callback_query.message.edit_text("📚 قصة: عائد من الظلام - اختر الجزء:", reply_markup=InlineKeyboardMarkup(keyboard))

# ## التعديل الثالث: التأكد من أن هذه الدالة تشمل كل الأسماء
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