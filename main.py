import pyrogram
print(f"Pyrogram version: {pyrogram.__version__}") # تم إضافة هذا السطر للتحقق من الإصدار

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import json
import os # استيراد مكتبة os للتعامل مع المسارات
import io # استيراد مكتبة io للتعامل مع كائنات البايتات كملفات

# إعداد الاتصال بالبوت
app = Client(
    "safe_poetry_bot",
    api_id=int(os.environ.get("23613053")),
    api_hash=os.environ.get("ae6f029e868b731ff7c4ab0429f18fb5"),
    bot_token=os.environ.get("7693900838:AAHBRpiVqAgzuvArq1edXTLCefuPBSTqyRk")
)
# 💬 رسالة الترحيب
intro_message = (
    "بسمِ اللهِ ربِّ أبي أيوبَ وأصحابِه، وبه نستعين، وبعد:\n"
    "فإنّ القلمَ كالسّيفِ، إذا عرَفَ التوحيدَ، قام من رمسه على رأسه، يطيرُ بصاحبه إلى كلِّ نِزالٍ وقِتال، "
    "ولم يزل به يَصولُ ويجولُ، حتى يُقيمَ اللهُ به الحجة، وينصرَ به دينَه.\n"
    "فاكتبْ، فإنّ روحَ القُدُسِ معك، ما نصرتَ الحق، وأقمتَ الكلمةَ، وجعلتَ المِدادَ جـ ـهـ ادًا."
)

# 📝 تحميل القصائد من ملف خارجي
# تأكد أن ملف poems.json موجود في نفس مجلد البوت
try:
    with open("poems.json", "r", encoding="utf-8") as f:
        poems = json.load(f)
except FileNotFoundError:
    print("Error: poems.json file not found. Please make sure it's in the same directory as the script.")
    poems = [] # تهيئة قائمة فارغة لتجنب الأخطاء إذا لم يتم العثور على الملف
except json.JSONDecodeError:
    print("Error: Could not decode poems.json. Check if the JSON format is valid.")
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
            [InlineKeyboardButton("📚 أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر", callback_data="show_abu_hamza_books")], # تم التغيير ليشير إلى قائمة الكتب
            [InlineKeyboardButton("📖 أبو أنس الفلسطيني", callback_data="show_abu_anas")],
            [InlineKeyboardButton("📝 مـ يـسـ رة الغـ ريـ ب", callback_data="show_mysara_gharib_books")],
            [InlineKeyboardButton("📜 أبو بـ كـ ر المـ دني", callback_data="show_abu_bakr_madani_books")],
            [InlineKeyboardButton("🌸 أحلام النصر الدمشقية", callback_data="show_ahlam_alnaser_books")] # خيار جديد
        ])
    )

@app.on_callback_query(filters.regex("show_osama_poems"))
def show_osama_poems(client, callback_query):
    # تحقق للتأكد من أن قائمة القصائد ليست فارغة
    if not poems:
        callback_query.message.edit_text(
            "عذراً، لا توجد قصائد متاحة حالياً.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
            ])
        )
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
    
    # تحقق لتجنب الوصول إلى فهرس خارج النطاق
    if 0 <= idx < len(poems):
        poem = poems[idx]
        callback_query.message.edit_text(
            f"📖 {poem['title']}\n\n{poem['content']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ رجوع", callback_data="show_osama_poems")]
            ]),
            # parse_mode="HTML" # تم إزالة هذا السطر
        )
    else:
        callback_query.message.edit_text(
            "عذراً، القصيدة المطلوبة غير موجودة.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ رجوع", callback_data="show_osama_poems")]
            ])
        )


@app.on_callback_query(filters.regex("show_abu_khithama"))
def show_abu_khithama(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\قصائد دبجت بالدماء.pdf"
        caption_text = "📘 ديوان الشاعر أبو خيثمة الشنقيطي"
        
        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال الديوان.\n\n⬅️ يمكنك الرجوع إلى القائمة:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_archive")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("show_louis"))
def show_louis(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/لويس_مقالات.pdf"
        caption_text = "📗 مجموعة مقالات لويس عطية الله"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال مقالات لويس عطية الله.\n\n⬅️ يمكنك الرجوع إلى قائمة الأرشيف:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_archive")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")


# دالة لعرض قائمة بكتب أبي حمزة المهاجر (تم تعديلها)
@app.on_callback_query(filters.regex("show_abu_hamza_books"))
def show_abu_hamza_books(client, callback_query):
    keyboard = [
        [InlineKeyboardButton("📚 ديوان هموم وآلام", callback_data="send_abu_hamza_homoom_w_alam")],
        [InlineKeyboardButton("📖 سير أعلام الشـ هـ داء", callback_data="send_abu_hamza_seir_alam_shohada")], # كتاب جديد
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text(
        "📚 اختر كتاباً لـ أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# دالة إرسال ديوان هموم وآلام لأبي حمزة المهاجر (تم إعادة تسميتها)
@app.on_callback_query(filters.regex("send_abu_hamza_homoom_w_alam"))
def send_abu_hamza_homoom_w_alam(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\هموم وآلام أبو حمزة.pdf"
        caption_text = "📚 ديوان هموم وآلام (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال ديوان هموم وآلام.\n\n⬅️ يمكنك الرجوع إلى قائمة أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_abu_hamza_books")] # الرجوع إلى قائمة كتبه
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

# دالة جديدة لإرسال سير أعلام الشهداء لأبي حمزة المهاجر
@app.on_callback_query(filters.regex("send_abu_hamza_seir_alam_shohada"))
def send_abu_hamza_seir_alam_shohada(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\سير-أعلام-الشُّهداء-1.pdf"
        caption_text = "📖 كتاب: سير أعلام الشـ هـ داء (أبو حـ ـمـ ـزة المـ ـهـ ـاجـ ـر)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب سير أعلام الشـ هـ داء.\n\n⬅️ يمكنك الرجوع إلى قائمة أبو حـ ـمـ ـز:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_abu_hamza_books")] # الرجوع إلى قائمة كتبه
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

# دالة جديدة لإرسال يوميات مجاهد من الفلوجة لأبي أنس الفلسطيني
@app.on_callback_query(filters.regex("show_abu_anas"))
def show_abu_anas(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\يوميات مجاهد من الفلوجة.pdf"
        caption_text = "📖 كتاب يوميات مـ ـجـ ـاهـ ـد من الفـ ـلـ ـوجـ ـة (أبو أنس الفلسطيني)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب يوميات مجاهد من الفلوجة.\n\n⬅️ يمكنك الرجوع إلى قائمة الأرشيف:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_archive")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

# دالة لعرض قائمة بكتب ميسرة الغريب
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

# دوال إرسال الكتب الخاصة بميسرة الغريب
@app.on_callback_query(filters.regex("send_mysara_ramziyat"))
def send_mysara_ramziyat(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\رَمْزِيَّات.pdf"
        caption_text = "📝 كتاب: رمزيات (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب رمزيات.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("send_mysara_shifaa_alayi"))
def send_mysara_shifaa_alayi(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\إنما شفاء العيّ السؤال.pdf"
        caption_text = "📝 كتاب: إنما شفاء العي السؤال (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب إنما شفاء العي السؤال.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("send_mysara_kurab"))
def send_mysara_kurab(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf"
        caption_text = "📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب الكُرَبُ وسُبُلُ تَفْرِيجِها.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("send_mysara_bidmaihim"))
def send_mysara_bidmaihim(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf"
        caption_text = "📝 بدمائهم نصحوا1 (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب بدمائهم نصحوا1.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("send_mysara_zarqawi"))
def send_mysara_zarqawi(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf"
        caption_text = "📝 سلسلة: من خفايا التاريخ- الزرقـ ا وي (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب من خفايا التاريخ- الزرقـ ا وي.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

@app.on_callback_query(filters.regex("send_mysara_qalou_faqal"))
def send_mysara_qalou_faqal(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\ميسرة الغريب\قـالـوا.. فـقـل!.pdf"
        caption_text = "📝 كتاب: قـالـوا.. فـقـل! (مـ يـسـ رة الغـ ريـ ب)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب قـالـوا.. فـقـل!.\n\n⬅️ يمكنك الرجوع إلى قائمة مـ يـسـ رة الغـ ريـ ب:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_mysara_gharib_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

# دالة جديدة لعرض قائمة بكتب أبي بكر المدني
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

# دالة جديدة لإرسال كتاب لفت الأنظار لأبي بكر المدني
@app.on_callback_query(filters.regex("send_abu_bakr_madani_laft_alanzar"))
def send_abu_bakr_madani_laft_alanzar(client, callback_query):
    # تم تحديث هذه الدالة لاستخدام طريقة فتح الملف
    try:
        document_path = r"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\أبو بكر المدني\لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf"
        caption_text = "📜 كتاب: لفت الأنظار لما جاء في الفلـ وجتين من أخبار1 (أبو بـ كـ ر المـ دني)"

        if not os.path.exists(document_path):
            callback_query.message.edit_text(
                f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
            )
            print(f"Error: File not found at path: {document_path}")
            return

        with open(document_path, "rb") as f:
            client.send_document(
                chat_id=callback_query.message.chat.id,
                document=io.BytesIO(f.read()),
                file_name=os.path.basename(document_path),
                caption=caption_text,
            )
        callback_query.message.edit_text(
            "✅ تم إرسال كتاب لفت الأنظار.\n\n⬅️ يمكنك الرجوع إلى قائمة أبو بـ كـ ر المـ دني:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_abu_bakr_madani_books")]
            ])
        )
    except Exception as e:
        callback_query.message.edit_text(
            f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}")

# دالة جديدة لعرض قائمة بكتب أحلام النصر الدمشقية
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
        [InlineKeyboardButton("📚 قصة: عائد من الظلام", callback_data="show_aed_min_althalam_parts")], # الزر الجديد للقصة
        [InlineKeyboardButton("⬅️ رجوع", callback_data="show_archive")]
    ]
    callback_query.message.edit_text(
        "🌸 اختر كتاباً لـ أحلام النصر الدمشقية:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("show_aed_min_althalam_parts"))
def show_aed_min_althalam_parts(client, callback_query):
    # إنشاء أزرار الأجزاء من 1 إلى 35
    keyboard = []
    for i in range(1, 36):
        keyboard.append([InlineKeyboardButton(f"الجزء {i}", callback_data=f"send_aed_min_althalam_part_{i}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="show_ahlam_alnaser_books")]) # زر الرجوع
    
    callback_query.message.edit_text(
        "📚 قصة: عائد من الظلام - اختر الجزء:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# دوال إرسال الكتب الخاصة بأحلام النصر الدمشقية (تم تعديلها لاستخدام io.BytesIO)
def send_ahlam_alnaser_book(client, callback_query, document_path, caption_text, return_callback):
    # تم التأكد من وجود callback_query.message
    if not callback_query.message:
        print("Error: callback_query.message is None. Cannot send/edit message.")
        return

    chat_id = callback_query.message.chat.id
    # تم التغيير من .message_id إلى .id
    message_id = callback_query.message.id 
    
    # التحقق مما إذا كان الملف موجودًا
    if not os.path.exists(document_path):
        client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ خطأ: لم يتم العثور على الملف المحدد:\n`{document_path}`\nيرجى التأكد من أن المسار صحيح وأن الملف موجود.",
        )
        print(f"Error: File not found at path: {document_path}") # طباعة الخطأ في الكونسول
        return # التوقف هنا إذا لم يتم العثور على الملف

    try:
        print(f"Attempting to send document: {document_path}") # طباعة المسار في الكونسول للمراجعة
        with open(document_path, "rb") as f: # فتح الملف بوضع القراءة الثنائية
            client.send_document(
                chat_id=chat_id,
                document=io.BytesIO(f.read()), # تمرير محتوى الملف ككائن BytesIO
                file_name=os.path.basename(document_path), # تحديد اسم الملف لـ Telegram
                caption=caption_text,
            )
        client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ تم إرسال {caption_text.split(':', 1)[-1].strip()}.\n\n⬅️ يمكنك الرجوع إلى القائمة السابقة:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data=return_callback)]
            ])
        )
    except Exception as e:
        client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ حدث خطأ أثناء الإرسال:\n{str(e)}",
        )
        print(f"Error sending document {document_path}: {e}") # طباعة الخطأ في الكونسول


# Mapping of callback_data to book details for Ahlam Al-Naser
AHLAM_ALNASER_BOOKS_MAP = {
    "send_ahlam_alnaser_book_1": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/1 الباغوز، ومدرسة الابتلاء!.pdf",
        "caption": "🌸 كتاب: 1 الباغوز، ومدرسة الابتلاء! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_2": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/2 مَن سمح لهم أن يكونوا أبرياء؟!.pdf",
        "caption": "🌸 كتاب: 2 مَن سمح لهم أن يكونوا أبرياء؟! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_3": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/3 يا أهل مصر؛ احذروا الأدوية!.pdf",
        "caption": "🌸 كتاب: 3 يا أهل مصر؛ احذروا الأدوية! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_4": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/4 بل أطعنا الله إذ أحرقناه!.pdf",
        "caption": "🌸 كتاب: 4 بل أطعنا الله إذ أحرقناه! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_5": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/5 دولة المنهج لا دولة الماديات.pdf",
        "caption": "🌸 كتاب: 5 دولة المنهج لا دولة الماديات (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_6": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/6 أخطأت يا أم ستيفن!.pdf",
        "caption": "🌸 كتاب: 6 أخطأت يا أم ستيفن! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_7": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/7 عمل المرأة، وكذبة التحرر!.pdf",
        "caption": "🌸 كتاب: 7 عمل المرأة، وكذبة التحرر! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_8": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/8 توضيح لا بد منه.pdf",
        "caption": "🌸 كتاب: 8 توضيح لا بد منه (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_9": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!.pdf",
        "caption": "🌸 كتاب: 9 أتينا لنبقى.. وإن بلغت القلوب الحناجر! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_10": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/10 منشورات في التربية.pdf",
        "caption": "🌸 كتاب: 10 منشورات في التربية (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_11": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/11 إنَّني بريئةٌ منكَ.pdf",
        "caption": "🌸 كتاب: 11 إنَّني بريئةٌ منكَ (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_12": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/12 ديوان أوار الحق لأحلام النصر.pdf",
        "caption": "🌸 كتاب: 12 ديوان أوار الحق لأحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_13": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/13 ديوان هدير المعامع لأحلام النصر.pdf",
        "caption": "🌸 كتاب: 13 ديوان هدير المعامع لأحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_14": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/14 أفيـون السهولة، لأحلام النصر.pdf",
        "caption": "🌸 كتاب: 14 أفيـون السهولة، لأحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_15": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب.pdf",
        "caption": "🌸 كتاب: 15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_16": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/16 الغلاة.. وبقرة بني إسرائيل!.pdf",
        "caption": "🌸 كتاب: 16 الغلاة.. وبقرة بني إسرائيل! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_17": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/17 وِجاءُ_الثغور_في_دفع_شرور_الكَفور.pdf",
        "caption": "🌸 كتاب: 17 وِجاءُ الثغور في دفع شرور الكَفور (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_18": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/18 ديوان سحابة نقاء، لأحلام النصر.pdf",
        "caption": "🌸 كتاب: 18 ديوان سحابة نقاء، لأحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_19": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/19 لا عزة إلا بالجهاد.pdf",
        "caption": "🌸 كتاب: 19 لا عزة إلا بالجهاد (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_20": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/20 بدايتي مع الدولة.pdf",
        "caption": "🌸 كتاب: 20 بدايتي مع الدولة (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_21": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/21 ربعي بن عامر؛ بين شرعة الله تعالى وشرعة الأمم المتحدة.pdf",
        "caption": "🌸 كتاب: 21 ربعي بن عامر؛ بين شرعة الله تعالى وشرعة الأمم المتحدة (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_22": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/22 الانتصار.pdf",
        "caption": "🌸 كتاب: 22 الانتصار (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_23": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/23 القائدالشهيد أبو طالب السنوار!.pdf",
        "caption": "🌸 كتاب: 23 القائدالشهيد أبو طالب السنوار! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_24": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/24 بيان مؤسسة أوار الحق.pdf",
        "caption": "🌸 كتاب: 24 بيان مؤسسة أوار الحق (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_25": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/25 المرجئة_يهود_القبلة.pdf",
        "caption": "🌸 كتاب: 25 المرجئة يهود القبلة (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_26": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/26 تناطح البغال في ردغة الخبال.pdf",
        "caption": "🌸 كتاب: 26 تناطح البغال في ردغة الخبال (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_27": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/27 طالبان_على_خطى_مرسي_بقلم_أحلام_النصر.pdf",
        "caption": "🌸 كتاب: 27 طالبان على خطى مرسي بقلم أحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_28": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/28 ليكون الدين كله لله، بقلم أحلام النصر.pdf",
        "caption": "🌸 كتاب: 28 ليكون الدين كله لله، بقلم أحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_29": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/29 الجانب التعليمي، أحلام النصر.pdf",
        "caption": "🌸 كتاب: 29 الجانب التعليمي، أحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_30": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/30 أمة الإسناد، لأحلام النصر.pdf",
        "caption": "🌸 كتاب: 30 أمة الإسناد، لأحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_31_a": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/31 علام الخذلان؟!.pdf",
        "caption": "🌸 كتاب: 31 علام الخذلان؟! (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_32": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/32 فلسطين إلى متى يبقى الخطر آمنا.pdf",
        "caption": "🌸 كتاب: 32 فلسطين إلى متى يبقى الخطر آمنا (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_اثبت_ولا_تتردد": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/اثبت_ولا_تتردد،_وبايع_الهزبر_لترشَد (2).pdf",
        "caption": "🌸 كتاب: اثبت ولا تتردد، وبايع الهزبر لترشَد (2) (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_الذئاب_المنفردة": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/الذئاب المنفردة.pdf",
        "caption": "🌸 كتاب: الذئاب المنفردة (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_الزرقاوي_كما_صحبته": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/الزرقاوي_كما_صحبته.pdf",
        "caption": "🌸 كتاب: الزرقاوي كما صحبته (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_الموت_الزؤام": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/الموت_الزؤام_لأعداء_نبي_الإسلام_وشعر_أتجرؤون_بقلم_أحلام_النصر.pdf",
        "caption": "🌸 كتاب: الموت الزؤام لأعداء نبي الإسلام وشعر أتجرؤون بقلم أحلام النصر (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_حرب_دينية": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/حرب دينية لا تصرفات فردية.pdf",
        "caption": "🌸 كتاب: حرب دينية لا تصرفات فردية (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_حكم_المنظومة": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/حكم المنظومة التعليمية.pdf",
        "caption": "🌸 كتاب: حكم المنظومة التعليمية (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_حملة_المناصرة": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/حملة المناصرة رباط وجهاد.pdf",
        "caption": "🌸 كتاب: حملة المناصرة رباط وجهاد (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_لا_يصح": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/لا يصح إلا الصحيح، والمرتد لن يستريح.pdf",
        "caption": "🌸 كتاب: لا يصح إلا الصحيح، والمرتد لن يستريح (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_taysir_altaalim_1": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/تيسير_التعليم_لمريد_قراءات_القرآن_الكريم_1.pdf",
        "caption": "🌸 كتاب: تيسير التعليم لمريد قراءات القرآن الكريم 1 (أحلام النصر الدمشقية)"
    },
    "send_ahlam_alnaser_book_kitab_altajweed": {
        "path": r"C:/Users/Extreme/Desktop/adabjehad/قصائد المشروع/أوار الحق/كتاب التجويد.pdf",
        "caption": "🌸 كتاب: كتاب التجويد (أحلام النصر الدمشقية)"
    },
    # إضافة أجزاء قصة عائد من الظلام
    **{f"send_aed_min_althalam_part_{i}": {
        "path": fr"C:\Users\Extreme\Desktop\adabjehad\قصائد المشروع\أوار الحق\أجزاء قصة عائد من الظلام\AMT-E{i}.pdf",
        "caption": f"🌸 قصة: عائد من الظلام - الجزء {i} (أحلام النصر الدمشقية)"
    } for i in range(1, 36)}
}


@app.on_callback_query(filters.regex(r"^send_ahlam_alnaser_book_|^send_aed_min_althalam_part_"))
def send_ahlam_alnaser_specific_book(client, callback_query):
    callback_data_key = callback_query.data
    book_info = AHLAM_ALNASER_BOOKS_MAP.get(callback_data_key)

    if book_info:
        # تحديد الـ return_callback بناءً على الـ callback_data
        if callback_data_key.startswith("send_aed_min_althalam_part_"):
            return_callback = "show_aed_min_althalam_parts"
        else:
            return_callback = "show_ahlam_alnaser_books"

        send_ahlam_alnaser_book(
            client,
            callback_query,
            book_info["path"],
            book_info["caption"],
            return_callback # تم تمرير الـ return_callback الصحيح هنا
        )
    else:
        callback_query.message.edit_text(
            "❌ حدث خطأ: الكتاب المطلوب غير موجود.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="show_ahlam_alnaser_books")]
            ])
        )


app.run()