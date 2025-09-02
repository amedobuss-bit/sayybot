import os, requests, json
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
SECRET = os.environ.get("SECRET_TOKEN", "").strip()
assert BOT_TOKEN, "TG_BOT_TOKEN is required"

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)
app.url_map.strict_slashes = False

# رسالة الترحيب الأصلية
INTRO_MESSAGE = (
    "بسمِ اللهِ ربِّ أبي أيوبَ وأصحابِه، وبه نستعين، وبعد:\n"
    "فإنّ القلمَ كالسّيفِ، إذا عرَفَ التوحيدَ، قام من رمسه على رأسه، يطيرُ بصاحبه إلى كلِّ نِزالٍ وقِتال، "
    "ولم يزل به يَصولُ ويجولُ، حتى يُقيمَ اللهُ به الحجة، وينصرَ به دينَه.\n"
    "فاكتبْ، فإنّ روحَ القُدُسِ معك، ما نصرتَ الحق، وأقمتَ الكلمةَ، وجعلتَ المِدادَ جـ ـهـ ادًا."
)

# تحميل القصائد
try:
    with open("poems.json", "r", encoding="utf-8") as f:
        POEMS = json.load(f)
except:
    POEMS = []

# دوال مساعدة
def tg(method, **params):
    try:
        r = requests.post(f"{API}/{method}", json=params, timeout=5)
        return r.json()
    except Exception:
        return {}

def answer_cbq(cbq_id, text=""):
    try: 
        requests.post(f"{API}/answerCallbackQuery", 
                     json={"callback_query_id": cbq_id, "text": text}, timeout=5)
    except Exception: 
        pass

def send(chat_id, text, reply_markup=None):
    tg("sendMessage", chat_id=chat_id, text=text, reply_markup=reply_markup)

def edit(chat_id, msg_id, text, reply_markup=None):
    tg("editMessageText", chat_id=chat_id, message_id=msg_id, text=text, reply_markup=reply_markup)

def kb(rows):
    return {"inline_keyboard": rows}

def send_doc(chat_id, path, caption=""):
    try:
        with open(path, "rb") as f:
            requests.post(
                f"{API}/sendDocument",
                data={"chat_id": str(chat_id), "caption": caption},
                files={"document": (os.path.basename(path), f)},
                timeout=15
            )
    except Exception:
        pass

# الصفحة الرئيسية
@app.get("/")
def home():
    return "🚂 RailBot - بوت القصائد الآمن يعمل بنجاح!", 200

# Webhook endpoint
@app.post(f"/{BOT_TOKEN}")
@app.post(f"/{BOT_TOKEN}/")
def webhook():
    if SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        return "forbidden", 403

    try:
        upd = request.get_json(silent=True) or {}
        
        # معالجة الرسائل
        msg = upd.get("message") or upd.get("edited_message")
        if msg:
            chat_id = (msg.get("chat") or {}).get("id")
            text = (msg.get("text") or "").strip()
            
            if chat_id and text:
                if text.startswith("/start"):
                    send(
                        chat_id,
                        INTRO_MESSAGE,
                        reply_markup=kb([[{"text":"انتقل إلى مادة الأرشيف","callback_data":"show_archive"}]])
                    )
                elif text.startswith("/help"):
                    send(chat_id, "الأوامر:\n/start لبدء البوت\n/help للمساعدة")
                else:
                    send(chat_id, "اكتب /start لبدء البوت")
        
        # معالجة Callback Queries
        cbq = upd.get("callback_query")
        if cbq:
            cbq_id = cbq.get("id")
            from_msg = cbq.get("message") or {}
            chat_id = (from_msg.get("chat") or {}).get("id")
            msg_id = from_msg.get("message_id")
            data = cbq.get("data") or ""

            if data == "show_archive":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "اختر مجموعة القصائد:",
                     reply_markup=kb([
                    [{"text":"أسامة بن لادن","callback_data":"show_osama_poems"}],
                    [{"text":"أبو حمزة المهاجر","callback_data":"show_abu_hamza_books"}],
                    [{"text":"أبو أنس الفلسطيني","callback_data":"show_abu_anas"}],
                    [{"text":"ميسرة الغريب","callback_data":"show_mysara_gharib_books"}],
                    [{"text":"أبو الحسن المهاجر","callback_data":"show_muhajir_books"}],
                    [{"text":"العدنان","callback_data":"show_adnani_books"}],
                    [{"text":"أبو حمزة القرشي","callback_data":"show_qurashi_books"}],
                    [{"text":"أبو عمر المهاجر","callback_data":"show_abu_omar_books"}],
                    [{"text":"أبو بلال الحربي","callback_data":"show_harbi_books"}],
                    [{"text":"أحلام النصر الدمشقية","callback_data":"show_ahlam_alnaser_books"}],
                    [{"text":"الشاعر أبو مالك شيبة الحمد","callback_data":"show_shaybah_books"}],
                    [{"text":"المهندس محمد الزهيري","callback_data":"show_zuhayri_books"}],
                    [{"text":"بنت نجد","callback_data":"show_bint_najd_books"}],
                    [{"text":"العقاب المصري","callback_data":"show_oqab_masri"}],
                    [{"text":"مرثد بن عبد الله","callback_data":"show_marthad_abdullah"}],
                    [{"text":"أبو خيثمة الشنقيطي","callback_data":"show_abu_khithama"}],
                    [{"text":"لويس عطية الله","callback_data":"show_louis"}],
                    [{"text":"أبو بكر المدني","callback_data":"show_abu_bakr_madani_books"}],
                    [{"text":"حسين المعاضيدي","callback_data":"show_hussein_almadidi"}]
                     ]))

            # قسم أحلام النصر الدمشقية - القائمة الكاملة
            elif data == "show_ahlam_alnaser_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "🌸 اختر من مؤلفات أحلام النصر الدمشقية:",
                     reply_markup=kb([
                        [{"text":"📖 1 الباغوز، ومدرسة الابتلاء!","callback_data":"send_ahlam_alnaser_book_1"}],
                        [{"text":"📖 2 مَن سمح لهم أن يكونوا أبرياء؟!","callback_data":"send_ahlam_alnaser_book_2"}],
                        [{"text":"📖 3 يا أهل مصر؛ احذروا الأدوية!","callback_data":"send_ahlam_alnaser_book_3"}],
                        [{"text":"📖 4 بل أطعنا الله إذ أحرقناه!","callback_data":"send_ahlam_alnaser_book_4"}],
                        [{"text":"📖 5 دولة المنهج لا دولة الماديات","callback_data":"send_ahlam_alnaser_book_5"}],
                        [{"text":"📖 6 أخطأت يا أم ستيفن!","callback_data":"send_ahlam_alnaser_book_6"}],
                        [{"text":"📖 7 عمل المرأة، وكذبة التحرر!","callback_data":"send_ahlam_alnaser_book_7"}],
                        [{"text":"📖 8 توضيح لا بد منه","callback_data":"send_ahlam_alnaser_book_8"}],
                        [{"text":"📖 9 أتينا لنبقى.. وإن بلغت القلوب الحناجر!","callback_data":"send_ahlam_alnaser_book_9"}],
                        [{"text":"📖 10 منشورات في التربية","callback_data":"send_ahlam_alnaser_book_10"}],
                        [{"text":"📖 11 إنَّني بريئةٌ منكَ","callback_data":"send_ahlam_alnaser_book_11"}],
                        [{"text":"📖 12 ديوان أوار الحق لأحلام النصر","callback_data":"send_ahlam_alnaser_book_12"}],
                        [{"text":"📖 13 ديوان هدير المعامع لأحلام النصر","callback_data":"send_ahlam_alnaser_book_13"}],
                        [{"text":"📖 14 أفيـون السهولة، لأحلام النصر","callback_data":"send_ahlam_alnaser_book_14"}],
                        [{"text":"📖 15 رحلة علم وجهاد؛ سيرة المجاهد أبي أسامة الغريب","callback_data":"send_ahlam_alnaser_book_15"}],
                        [{"text":"📖 16 الغلاة.. وبقرة بني إسرائيل!","callback_data":"send_ahlam_alnaser_book_16"}],
                        [{"text":"📖 17 وِجاءُ الثغور في دفع شرور الكَفور","callback_data":"send_ahlam_alnaser_book_17"}],
                        [{"text":"📖 18 ديوان سحابة نقاء، لأحلام النصر","callback_data":"send_ahlam_alnaser_book_18"}],
                        [{"text":"📖 19 لا عزة إلا بالجهاد","callback_data":"send_ahlam_alnaser_book_19"}],
                        [{"text":"📖 20 بدايتي مع الدولة","callback_data":"send_ahlam_alnaser_book_20"}],
                        [{"text":"📖 21 ربعي بن عامر؛ بين شرعة الله وشرعة الأمم المتحدة","callback_data":"send_ahlam_alnaser_book_21"}],
                        [{"text":"📖 22 الانتصار","callback_data":"send_ahlam_alnaser_book_22"}],
                        [{"text":"📖 23 القائدالشهيد أبو طالب السنوار!","callback_data":"send_ahlam_alnaser_book_23"}],
                        [{"text":"📖 24 بيان مؤسسة أوار الحق","callback_data":"send_ahlam_alnaser_book_24"}],
                        [{"text":"📖 25 المرجئة يهود القبلة","callback_data":"send_ahlam_alnaser_book_25"}],
                        [{"text":"📖 26 تناطح البغال في ردغة الخبال","callback_data":"send_ahlam_alnaser_book_26"}],
                        [{"text":"📖 27 طالبان على خطى مرسي بقلم أحلام النصر","callback_data":"send_ahlam_alnaser_book_27"}],
                        [{"text":"📖 28 ليكون الدين كله لله، بقلم أحلام النصر","callback_data":"send_ahlam_alnaser_book_28"}],
                        [{"text":"📖 29 الجانب التعليمي، أحلام النصر","callback_data":"send_ahlam_alnaser_book_29"}],
                        [{"text":"📖 30 أمة الإسناد، لأحلام النصر","callback_data":"send_ahlam_alnaser_book_30"}],
                        [{"text":"📖 31 علام الخذلان؟!","callback_data":"send_ahlam_alnaser_book_31_a"}],
                        [{"text":"📖 32 فلسطين إلى متى يبقى الخطر آمنا","callback_data":"send_ahlam_alnaser_book_32"}],
                        [{"text":"📖 اثبت ولا تتردد، وبايع الهزبر لترشَد (2)","callback_data":"send_ahlam_alnaser_book_اثبت_ولا_تتردد"}],
                        [{"text":"📖 الذئاب المنفردة","callback_data":"send_ahlam_alnaser_book_الذئاب_المنفردة"}],
                        [{"text":"📖 الزرقاوي كما صحبته","callback_data":"send_ahlam_alnaser_book_الزرقاوي_كما_صحبته"}],
                        [{"text":"📖 الموت الزؤام لأعداء نبي الإسلام وشعر أتجرؤون","callback_data":"send_ahlam_alnaser_book_الموت_الزؤام"}],
                        [{"text":"📖 حرب دينية لا تصرفات فردية","callback_data":"send_ahlam_alnaser_book_حرب_دينية"}],
                        [{"text":"📖 حكم المنظومة التعليمية","callback_data":"send_ahlam_alnaser_book_حكم_المنظومة"}],
                        [{"text":"📖 حملة المناصرة رباط وجهاد","callback_data":"send_ahlam_alnaser_book_حملة_المناصرة"}],
                        [{"text":"📖 لا يصح إلا الصحيح، والمرتد لن يستريح","callback_data":"send_ahlam_alnaser_book_لا_يصح"}],
                        [{"text":"📖 تيسير التعليم لمريد قراءات القرآن الكريم 1","callback_data":"send_ahlam_alnaser_book_taysir_altaalim_1"}],
                        [{"text":"📖 كتاب التجويد","callback_data":"send_ahlam_alnaser_book_kitab_altajweed"}],
                        [{"text":"📚 قصة: عائد من الظلام (كل الأجزاء)","callback_data":"show_aed_min_althalam_parts"}],
                        [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            # معالجة إرسال كتب أحلام النصر
            elif data.startswith("send_ahlam_alnaser_book_"):
                book_map = {
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
                    "send_ahlam_alnaser_book_kitab_altajweed": ("أوار الحق/كتاب التجويد.pdf", "كتاب التجويد")
                }
                book_info = book_map.get(data)
                if book_info:
                    file_path, caption = book_info
                    full_path = f"قصائد المشروع/{file_path}"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, full_path, f"🌸 {caption} (أحلام النصر الدمشقية)")
                else:
                    answer_cbq(cbq_id, "❌ حدث خطأ: الكتاب المطلوب غير موجود.", show_alert=True)

            # باقي الأقسام الأساسية
            elif data == "show_osama_poems":
                answer_cbq(cbq_id)
                osama_poems = POEMS[:10] if POEMS else []
                keyboard = [[{"text": p.get("title", f"قصيدة {i+1}"), "callback_data": f"poem_{i}"}] for i, p in enumerate(osama_poems)]
                keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                edit(chat_id, msg_id, "قائمة القصائد:\n\n(أسامة بن لادن)", reply_markup=kb(keyboard))
            
            elif data == "show_harbi_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "⚔️ اختر من مؤلفات أبي بلال الحربي:",
                     reply_markup=kb([
                    [{"text":"📖 وقفات مع الشيخ المربي","callback_data":"send_harbi_pdf_1"}],
                    [{"text":"📖 ماذا فعلت بنا يا سعد؟","callback_data":"send_harbi_pdf_2"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))
            
            elif data == "send_harbi_pdf_1":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/وقفات مع الشيخ المربي.pdf", "📖 وقفات مع الشيخ المربي")
            elif data == "send_harbi_pdf_2":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/ماذا فعلت بنا يا سعد؟.pdf", "📖 ماذا فعلت بنا يا سعد؟")
            
            elif data == "show_abu_hamza_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "📚 اختر كتاباً لـ أبو حمزة المهاجر:",
                     reply_markup=kb([
                        [{"text":"📚 ديوان هموم وآلام","callback_data":"send_abu_hamza_homoom_w_alam"}],
                        [{"text":"📖 سير أعلام الشهداء","callback_data":"send_abu_hamza_seir_alam_shohada"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))
            
            elif data == "send_abu_hamza_homoom_w_alam":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/هموم وآلام أبو حمزة.pdf", "📚 ديوان هموم وآلام (أبو حمزة المهاجر)")
            elif data == "send_abu_hamza_seir_alam_shohada":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/سير-أعلام-الشُّهداء-1.pdf", "📖 كتاب: سير أعلام الشهداء (أبو حمزة المهاجر)")
            
            elif data == "show_abu_anas":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/يوميات مجاهد من الفلوجة.pdf", "📖 كتاب يوميات مجاهد من الفلوجة (أبو أنس الفلسطيني)")
            
        return jsonify({"status":"ok"})
    except Exception as e:
        print(f"Error in webhook: {e}")
        return jsonify({"status":"error"}), 500

application = app