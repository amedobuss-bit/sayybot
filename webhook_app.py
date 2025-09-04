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
def load_poems():
    try:
        with open("poems.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading poems: {e}")
        return []

POEMS = load_poems()

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
    try:
        tg("sendMessage", chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error sending message: {e}")

def edit(chat_id, msg_id, text, reply_markup=None):
    try:
        tg("editMessageText", chat_id=chat_id, message_id=msg_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error editing message: {e}")

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
                try:
                    if text.startswith("/start"):
                        send(
                            chat_id,
                            INTRO_MESSAGE,
                            reply_markup=kb([[{"text":"انتقل إلى مادة الأرشيف","callback_data":"show_archive"}]])
                        )
                    elif text.startswith("/help"):
                        send(chat_id, "الأوامر:\n/start لبدء البوت\n/help للمساعدة")
                    elif text == "انتقال للمواد" or "انتقال" in text or "المواد" in text:
                        send(
                            chat_id,
                            "اختر مجموعة القصائد:",
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
                            ])
                        )
                    else:
                        send(chat_id, "اكتب /start لبدء البوت أو /help للمساعدة")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    send(chat_id, "حدث خطأ، حاول مرة أخرى")
        
        # معالجة Callback Queries
        cbq = upd.get("callback_query")
        if cbq:
            try:
                cbq_id = cbq.get("id")
                from_msg = cbq.get("message") or {}
                chat_id = (from_msg.get("chat") or {}).get("id")
                msg_id = from_msg.get("message_id")
                data = cbq.get("data") or ""
                
                if not chat_id or not cbq_id:
                    return jsonify({"status":"ok"})

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
                    # تحميل القصائد ديناميكياً
                    current_poems = load_poems()
                    # عرض قصائد أسامة بن لادن فقط
                    osama_poems = [p for p in current_poems if p.get("author") == "أسامة بن لادن"]
                    keyboard = []
                    
                    # إضافة القصائد مع تحسين العرض
                    for i, poem in enumerate(osama_poems):
                        title = poem.get("title", f"قصيدة {i+1}")
                        keyboard.append([{"text": f"📜 {title}", "callback_data": f"poem_{current_poems.index(poem)}"}])
                    
                    keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                    
                    # إضافة عدد القصائد في الرسالة
                    poem_count = len(osama_poems)
                    total_poems = len(current_poems)
                    edit(chat_id, msg_id, f"قائمة القصائد:\n\n(أسامة بن لادن)\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}", reply_markup=kb(keyboard))
                
                elif data == "show_harbi_books":
                    answer_cbq(cbq_id)
                    # تحميل القصائد ديناميكياً
                    current_poems = load_poems()
                    # عرض قصائد أبو بلال الحربي مع الكتب
                    harbi_poems = [p for p in current_poems if p.get("author") == "أبو بلال الحربي"]
                    keyboard = []
                    
                    # إضافة القصائد
                    for i, poem in enumerate(harbi_poems):
                        title = poem.get("title", f"قصيدة {i+1}")
                        keyboard.append([{"text": f"📜 {title}", "callback_data": f"poem_{current_poems.index(poem)}"}])
                    
                    # إضافة الكتب
                    keyboard.append([{"text":"📖 وقفات مع الشيخ المربي","callback_data":"send_harbi_pdf_1"}])
                    keyboard.append([{"text":"📖 ماذا فعلت بنا يا سعد؟","callback_data":"send_harbi_pdf_2"}])
                    keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                    
                    # إضافة عدد القصائد في الرسالة
                    poem_count = len(harbi_poems)
                    total_poems = len(current_poems)
                    edit(chat_id, msg_id, f"⚔️ اختر من مؤلفات أبي بلال الحربي:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}", reply_markup=kb(keyboard))
                
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
                
                # باقي الأقسام المفقودة
                elif data == "show_mysara_gharib_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات ميسرة الغريب:",
                         reply_markup=kb([
                            [{"text":"📖 إنما شفاء العيّ السؤال","callback_data":"send_mysara_book_1"}],
                            [{"text":"📖 الكُرَبُ وسُبُلُ تَفْرِيجِها","callback_data":"send_mysara_book_2"}],
                            [{"text":"📖 يوميات مجاهد من الفلوجة","callback_data":"send_mysara_book_3"}],
                            [{"text":"📖 موسوعة أبو زبيدة الأمنية","callback_data":"send_mysara_book_4"}],
                            [{"text":"📖 قـالـوا.. فـقـل!","callback_data":"send_mysara_book_5"}],
                            [{"text":"📖 سلسلة من خفايا التاريخ الزرقاوي","callback_data":"send_mysara_book_6"}],
                            [{"text":"📖 سلسلة بدمائهم نصحوا 1.. منهج حياة","callback_data":"send_mysara_book_7"}],
                            [{"text":"📖 رَمْزِيَّات","callback_data":"send_mysara_book_8"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_mysara_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/إنما شفاء العيّ السؤال.pdf", "📖 إنما شفاء العيّ السؤال (ميسرة الغريب)")
                elif data == "send_mysara_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf", "📖 الكُرَبُ وسُبُلُ تَفْرِيجِها (ميسرة الغريب)")
                elif data == "send_mysara_book_3":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/يوميات مجاهد من الفلوجة .pdf", "📖 يوميات مجاهد من الفلوجة (ميسرة الغريب)")
                elif data == "send_mysara_book_4":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/موسوعة أبو زبيدة الأمنية.pdf", "📖 موسوعة أبو زبيدة الأمنية (ميسرة الغريب)")
                elif data == "send_mysara_book_5":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/قـالـوا.. فـقـل!.pdf", "📖 قـالـوا.. فـقـل! (ميسرة الغريب)")
                elif data == "send_mysara_book_6":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf", "📖 سلسلة من خفايا التاريخ الزرقاوي (ميسرة الغريب)")
                elif data == "send_mysara_book_7":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf", "📖 سلسلة بدمائهم نصحوا 1.. منهج حياة (ميسرة الغريب)")
                elif data == "send_mysara_book_8":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/رَمْزِيَّات.pdf", "📖 رَمْزِيَّات (ميسرة الغريب)")
                
                elif data == "show_muhajir_books":
                    answer_cbq(cbq_id)
                    # تحميل القصائد ديناميكياً
                    current_poems = load_poems()
                    # عرض قصائد أبو الحسن المهاجر مع الكتب
                    muhajir_poems = [p for p in current_poems if p.get("author") == "أبو الحسن المهاجر"]
                    keyboard = []
                    
                    # إضافة القصائد
                    for i, poem in enumerate(muhajir_poems):
                        title = poem.get("title", f"قصيدة {i+1}")
                        keyboard.append([{"text": f"📜 {title}", "callback_data": f"poem_{current_poems.index(poem)}"}])
                    
                    # إضافة الكتب
                    keyboard.append([{"text":"📖 الجامع لكلمات أبي الحسن المهاجر","callback_data":"send_muhajir_book_1"}])
                    keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                    
                    # إضافة عدد القصائد في الرسالة
                    poem_count = len(muhajir_poems)
                    total_poems = len(current_poems)
                    edit(chat_id, msg_id, f"📚 اختر من مؤلفات أبو الحسن المهاجر:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}", reply_markup=kb(keyboard))
                
                elif data == "send_muhajir_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/أبو الحسن المهاجر/الجامع لكلمات أبي الحسن المهاجر.pdf", "📖 الجامع لكلمات أبي الحسن المهاجر")
                
                elif data == "show_adnani_books":
                    answer_cbq(cbq_id)
                    # تحميل القصائد ديناميكياً
                    current_poems = load_poems()
                    # عرض قصائد العدناني مع الكتب
                    adnani_poems = [p for p in current_poems if p.get("author") == "العدنان"]
                    keyboard = []
                    
                    # إضافة القصائد
                    for i, poem in enumerate(adnani_poems):
                        title = poem.get("title", f"قصيدة {i+1}")
                        keyboard.append([{"text": f"📜 {title}", "callback_data": f"poem_{current_poems.index(poem)}"}])
                    
                    # إضافة الكتب
                    keyboard.append([{"text":"📖 قصيدة معركة الفلوجة الثانية","callback_data":"send_adnani_book_1"}])
                    keyboard.append([{"text":"📖 الجامع للعدناني","callback_data":"send_adnani_book_2"}])
                    keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                    
                    # إضافة عدد القصائد في الرسالة
                    poem_count = len(adnani_poems)
                    total_poems = len(current_poems)
                    edit(chat_id, msg_id, f"📚 اختر من مؤلفات العدناني:\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}", reply_markup=kb(keyboard))
                
                elif data == "send_adnani_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/العدناني/قصيدة معركة الفلوجة الثانية.pdf", "📖 قصيدة معركة الفلوجة الثانية (العدناني)")
                elif data == "send_adnani_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/العدناني/الجامع للعدناني.pdf", "📖 الجامع للعدناني")
                
                elif data == "show_qurashi_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات أبو حمزة القرشي:",
                         reply_markup=kb([
                            [{"text":"📖 الجامع لكلمات أبي حمزة القرشي","callback_data":"send_qurashi_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_qurashi_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/أبو حمزة القرشي/الجامع لكلمات أبي حمزة القرشي.pdf", "📖 الجامع لكلمات أبي حمزة القرشي")
                
                elif data == "show_abu_omar_books":
                    answer_cbq(cbq_id)
                    # تحميل القصائد ديناميكياً
                    current_poems = load_poems()
                    # عرض قصائد أبو عمر المهاجر فقط
                    abu_omar_poems = [p for p in current_poems if p.get("author") == "أبو عمر المهاجر"]
                    keyboard = []
                    
                    # إضافة القصائد مع تحسين العرض
                    for i, poem in enumerate(abu_omar_poems):
                        title = poem.get("title", f"قصيدة {i+1}")
                        keyboard.append([{"text": f"📜 {title}", "callback_data": f"poem_{current_poems.index(poem)}"}])
                    
                    keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                    
                    # إضافة عدد القصائد في الرسالة مع تشخيص إضافي
                    poem_count = len(abu_omar_poems)
                    total_poems = len(current_poems)
                    edit(chat_id, msg_id, f"📚 القصائد المتاحة:\n\n(أبو عمر المهاجر)\n\nعدد القصائد: {poem_count}\nإجمالي القصائد في الملف: {total_poems}", reply_markup=kb(keyboard))
                
                elif data == "show_shaybah_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات الشاعر أبو مالك شيبة الحمد:",
                         reply_markup=kb([
                            [{"text":"📖 الستينية فى ذكر سلاطين الخلافة العثمانية","callback_data":"send_shaybah_book_1"}],
                            [{"text":"📖 يا أسيراً خلفَ قضبانِ العدا","callback_data":"send_shaybah_book_2"}],
                            [{"text":"📖 مرثية آل الشيخ أسامة","callback_data":"send_shaybah_book_3"}],
                            [{"text":"📖 الديوان العـرّيســة الشعري","callback_data":"send_shaybah_book_4"}],
                            [{"text":"📖 قصيدة جحاجح القوقاز","callback_data":"send_shaybah_book_5"}],
                            [{"text":"📖 أنا مع أبي بكر","callback_data":"send_shaybah_book_6"}],
                            [{"text":"📖 سلام و إكرام لدولة الإسلام","callback_data":"send_shaybah_book_7"}],
                            [{"text":"📖 قصيدة سلام على سجن كوبر","callback_data":"send_shaybah_book_8"}],
                            [{"text":"📖 يـا دارَ سِـرْتَ الفاتحيـنَ","callback_data":"send_shaybah_book_9"}],
                            [{"text":"📖 قصيدة ذكـرتـك يـا أسـامـة دموع القلب","callback_data":"send_shaybah_book_10"}],
                            [{"text":"📖 على نهج الرسول","callback_data":"send_shaybah_book_11"}],
                            [{"text":"📖 أزفتْ نهايةُ جبهةِ الجولاني","callback_data":"send_shaybah_book_12"}],
                            [{"text":"📖 قصيدة رحل الشّهيد وما رحل","callback_data":"send_shaybah_book_13"}],
                            [{"text":"📖 قصيدة صرخة من أزواد","callback_data":"send_shaybah_book_14"}],
                            [{"text":"📖 قصيدة متنا دعاة على أبواب عزتنا","callback_data":"send_shaybah_book_15"}],
                            [{"text":"📖 قصيدة نصرة لعبد الكريم الحميد","callback_data":"send_shaybah_book_16"}],
                            [{"text":"📖 ديوان عبرة وعبير","callback_data":"send_shaybah_book_17"}],
                            [{"text":"📖 قصيدة فارس الإيمان","callback_data":"send_shaybah_book_18"}],
                            [{"text":"📖 قصيدة متى يكسر الشعب أغلاله","callback_data":"send_shaybah_book_19"}],
                            [{"text":"📖 قصيدة أرق بالسيف كل دم كفور","callback_data":"send_shaybah_book_20"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_shaybah_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/الستينية فى ذكر سلاطين الخلافة العثمانية بقلم شيبة الحمد -للتعديل.pdf", "📖 الستينية فى ذكر سلاطين الخلافة العثمانية (شيبة الحمد)")
                elif data == "send_shaybah_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/يا أسيراً خلفَ قضبانِ العدا.pdf", "📖 يا أسيراً خلفَ قضبانِ العدا (شيبة الحمد)")
                elif data == "send_shaybah_book_3":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/مرثية آل الشيخ أسامة للشاعر شيبة الحمد.pdf", "📖 مرثية آل الشيخ أسامة (شيبة الحمد)")
                elif data == "send_shaybah_book_4":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/الديوان العـرّيســة الشعري للشيخ شيبة الحمد.pdf", "📖 الديوان العـرّيســة الشعري (شيبة الحمد)")
                elif data == "send_shaybah_book_5":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة جحاجح القوقاز - شيبة الحمد.pdf", "📖 قصيدة جحاجح القوقاز (شيبة الحمد)")
                elif data == "send_shaybah_book_6":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/أنا مع أبي بكر- شعر شيبة الحمد.pdf", "📖 أنا مع أبي بكر (شيبة الحمد)")
                elif data == "send_shaybah_book_7":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/سلام و إكرام لدولة الإسلام.pdf", "📖 سلام و إكرام لدولة الإسلام (شيبة الحمد)")
                elif data == "send_shaybah_book_8":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة  سلام على سجن كوبر شيبة الحمد.pdf", "📖 قصيدة سلام على سجن كوبر (شيبة الحمد)")
                elif data == "send_shaybah_book_9":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/يـا دارَ سِـرْتَ  الفاتحيـنَ للشيخ شيبة الحمد.pdf", "📖 يـا دارَ سِـرْتَ الفاتحيـنَ (شيبة الحمد)")
                elif data == "send_shaybah_book_10":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة ذكـرتـك يـا أسـامـة دموع القلب شـيـبـة الـحـمـد.pdf", "📖 قصيدة ذكـرتـك يـا أسـامـة دموع القلب (شيبة الحمد)")
                elif data == "send_shaybah_book_11":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/على نهج الرسول - أبو مالك شيبة الحمد.pdf", "📖 على نهج الرسول (شيبة الحمد)")
                elif data == "send_shaybah_book_12":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/أزفتْ نهايةُ جبهةِ الجولاني - شيبة الحمد.pdf", "📖 أزفتْ نهايةُ جبهةِ الجولاني (شيبة الحمد)")
                elif data == "send_shaybah_book_13":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة رحل الشّهيد وما رحل، شيبة الحمد.pdf", "📖 قصيدة رحل الشّهيد وما رحل (شيبة الحمد)")
                elif data == "send_shaybah_book_14":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة صرخة من أزواد، شيبة الحمد.pdf", "📖 قصيدة صرخة من أزواد (شيبة الحمد)")
                elif data == "send_shaybah_book_15":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة متنا دعاة على أبواب عزتنا، شيبة الحمد.pdf", "📖 قصيدة متنا دعاة على أبواب عزتنا (شيبة الحمد)")
                elif data == "send_shaybah_book_16":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة نصرة لعبد الكريم_ الحميد، شيبة الحمد.pdf", "📖 قصيدة نصرة لعبد الكريم الحميد (شيبة الحمد)")
                elif data == "send_shaybah_book_17":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/ديوان عبرة وعبير، شيبة الحمد.pdf", "📖 ديوان عبرة وعبير (شيبة الحمد)")
                elif data == "send_shaybah_book_18":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة فارس الإيمان، شيبة الحمد.pdf", "📖 قصيدة فارس الإيمان (شيبة الحمد)")
                elif data == "send_shaybah_book_19":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة متى يكسر الشعب أغلاله، شيبة الحمد.pdf", "📖 قصيدة متى يكسر الشعب أغلاله (شيبة الحمد)")
                elif data == "send_shaybah_book_20":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/قصيدة أرق بالسيف كل دم كفور،_شيبة الحمد.pdf", "📖 قصيدة أرق بالسيف كل دم كفور (شيبة الحمد)")
                
                elif data == "show_zuhayri_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات المهندس محمد الزهيري:",
                         reply_markup=kb([
                            [{"text":"📖 نسجت لكم بقاني الدم عهدا","callback_data":"send_zuhayri_book_1"}],
                            [{"text":"📖 ستزيد دعوتنا عزا وتمكينا","callback_data":"send_zuhayri_book_2"}],
                            [{"text":"📖 عراق الله یزخر بالغیارى","callback_data":"send_zuhayri_book_3"}],
                            [{"text":"📖 مَنْ مُبلغٍ كلبَ الروافض ياسراً","callback_data":"send_zuhayri_book_4"}],
                            [{"text":"📖 ركزنا في ذرى الأمجاد رمحاً","callback_data":"send_zuhayri_book_5"}],
                            [{"text":"📖 أعدنا القادسية في شموخٍ","callback_data":"send_zuhayri_book_6"}],
                            [{"text":"📖 يا دولة التوحيد أينع زرعنا","callback_data":"send_zuhayri_book_7"}],
                            [{"text":"📖 هيهات ينــــزو كافـرٌ","callback_data":"send_zuhayri_book_8"}],
                            [{"text":"📖 نازلُ الأعماق للموت سعى","callback_data":"send_zuhayri_book_9"}],
                            [{"text":"📖 يكفي محمدا أن الله حافظه","callback_data":"send_zuhayri_book_10"}],
                            [{"text":"📖 صليل الصوارم","callback_data":"send_zuhayri_book_11"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_zuhayri_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/نسجت لكم بقاني الدم عهدا -محمد الزهيري.pdf", "📖 نسجت لكم بقاني الدم عهدا (محمد الزهيري)")
                elif data == "send_zuhayri_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/ستزيد دعوتنا عزا وتمكينا -محمد الزهيري.pdf", "📖 ستزيد دعوتنا عزا وتمكينا (محمد الزهيري)")
                elif data == "send_zuhayri_book_3":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/عراق اﷲ یزخر بالغیارى محمد الزهيري.pdf", "📖 عراق الله یزخر بالغیارى (محمد الزهيري)")
                elif data == "send_zuhayri_book_4":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/قصيدة_مَنْ_مُبلغٍ_كلبَ_الروافض_ياسراً_نصرة_لأم_المؤمنين_عائشة_رضي.pdf", "📖 مَنْ مُبلغٍ كلبَ الروافض ياسراً (محمد الزهيري)")
                elif data == "send_zuhayri_book_5":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/ركزنا في ذرى الأمجاد رمحاً - محمد الزهيري.pdf", "📖 ركزنا في ذرى الأمجاد رمحاً (محمد الزهيري)")
                elif data == "send_zuhayri_book_6":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/أعدنا القادسية في شموخٍ - محمد الزهيري.pdf", "📖 أعدنا القادسية في شموخٍ (محمد الزهيري)")
                elif data == "send_zuhayri_book_7":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/يا دولة التوحيد أينع زرعنا - محمد الزهيري.pdf", "📖 يا دولة التوحيد أينع زرعنا (محمد الزهيري)")
                elif data == "send_zuhayri_book_8":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/هيهات ينــــزو كافـرٌ - محمد الزهيري.pdf", "📖 هيهات ينــــزو كافـرٌ (محمد الزهيري)")
                elif data == "send_zuhayri_book_9":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/نازلُ الأعماق للموت سعى -محمد الزهيري.pdf", "📖 نازلُ الأعماق للموت سعى (محمد الزهيري)")
                elif data == "send_zuhayri_book_10":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/قصيدة يكفي محمدا أن الله حافظه للاخ محمد الزهيري.pdf", "📖 يكفي محمدا أن الله حافظه (محمد الزهيري)")
                elif data == "send_zuhayri_book_11":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/المهندس محمد الزهيري/صليل الصوارم - محمد الزهيري.pdf", "📖 صليل الصوارم (محمد الزهيري)")
                
                elif data == "show_bint_najd_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات بنت نجد:",
                         reply_markup=kb([
                            [{"text":"📖 مادحة للعدناني هاجية للجولاني","callback_data":"send_bint_najd_book_1"}],
                            [{"text":"📖 أمسِكْ لسانكَ يا قُنيبي","callback_data":"send_bint_najd_book_2"}],
                            [{"text":"📖 فرعونُ نجد ستنتهي أيامهُ","callback_data":"send_bint_najd_book_3"}],
                            [{"text":"📖 هذه دولة الإسلام، ياعشماوي","callback_data":"send_bint_najd_book_4"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_bint_najd_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/بنت نجد/مادحة للعدناني هاجية للجولاني.pdf", "📖 مادحة للعدناني هاجية للجولاني (بنت نجد)")
                elif data == "send_bint_najd_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/بنت نجد/أمسِكْ لسانكَ يا قُنيبي.pdf", "📖 أمسِكْ لسانكَ يا قُنيبي (بنت نجد)")
                elif data == "send_bint_najd_book_3":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/بنت نجد/فرعونُ نجد ستنتهي أيامهُ.pdf", "📖 فرعونُ نجد ستنتهي أيامهُ (بنت نجد)")
                elif data == "send_bint_najd_book_4":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/بنت نجد/هذه دولة الإسلام، ياعشماوي - بنت نجد.pdf", "📖 هذه دولة الإسلام، ياعشماوي (بنت نجد)")
                
                elif data == "show_oqab_masri":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات العقاب المصري:",
                         reply_markup=kb([
                            [{"text":"📖 إلى ابْنَتي مَوَدَّة","callback_data":"send_oqab_book_1"}],
                            [{"text":"📖 هنا الخلافة- ديوان شعري","callback_data":"send_oqab_book_2"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_oqab_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/العقاب المصري/إلى ابْنَتي مَوَدَّة.pdf", "📖 إلى ابْنَتي مَوَدَّة (العقاب المصري)")
                elif data == "send_oqab_book_2":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/العقاب المصري/هنا الخلافة- ديوان شعري العقاب المصري.pdf", "📖 هنا الخلافة- ديوان شعري (العقاب المصري)")
                
                elif data == "show_marthad_abdullah":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات مرثد بن عبد الله:",
                         reply_markup=kb([
                            [{"text":"📖 بعض من قصائد مرثد بن عبد الله","callback_data":"send_marthad_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_marthad_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/مـرثد بن عبد الله/بعض من قصائد مرثد بن عبد الله.pdf", "📖 بعض من قصائد مرثد بن عبد الله")
                
                elif data == "show_abu_khithama":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات أبو خيثمة الشنقيطي:",
                         reply_markup=kb([
                            [{"text":"📖 قصائد دبجت بالدماء","callback_data":"send_abu_khithama_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_abu_khithama_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/قصائد دبجت بالدماء.pdf", "📖 قصائد دبجت بالدماء (أبو خيثمة الشنقيطي)")
                
                elif data == "show_louis":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات لويس عطية الله:",
                         reply_markup=kb([
                            [{"text":"📖 لويس مقالات","callback_data":"send_louis_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_louis_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/لويس_مقالات.pdf", "📖 لويس مقالات (لويس عطية الله)")
                
                elif data == "show_abu_bakr_madani_books":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات أبو بكر المدني:",
                         reply_markup=kb([
                            [{"text":"📖 لفت الأنظار لما جاء في الفلوجتين من أخبار","callback_data":"send_abu_bakr_madani_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_abu_bakr_madani_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/أبو بكر المدني/لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf", "📖 لفت الأنظار لما جاء في الفلوجتين من أخبار (أبو بكر المدني)")
                
                elif data == "show_hussein_almadidi":
                    answer_cbq(cbq_id)
                    edit(chat_id, msg_id, "📚 اختر من مؤلفات حسين المعاضيدي:",
                         reply_markup=kb([
                            [{"text":"📖 هنا أرض الخلافة","callback_data":"send_hussein_book_1"}],
                            [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                         ]))
                
                elif data == "send_hussein_book_1":
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, "قصائد المشروع/حسين المعاضيدي/هنا أرض الخلافة- حسين المعاضيدي.pdf", "📖 هنا أرض الخلافة (حسين المعاضيدي)")

                # معالجة قصائد حسب المؤلفين
                elif data.startswith("poem_"):
                    try:
                        # تحميل القصائد ديناميكياً
                        current_poems = load_poems()
                        poem_index = int(data.split("_")[1])
                        if 0 <= poem_index < len(current_poems):
                            poem = current_poems[poem_index]
                            title = poem.get("title", f"قصيدة {poem_index + 1}")
                            content = poem.get("content", "المحتوى غير متوفر")
                            author = poem.get("author", "غير محدد")
                            
                            # تقسيم المحتوى إذا كان طويلاً (أكثر من 4000 حرف)
                            if len(content) > 4000:
                                # إرسال العنوان أولاً
                                title_message = f"📖 **{title}**\n\n✍️ {author}"
                                send(chat_id, title_message)
                                
                                # تقسيم المحتوى إلى أجزاء
                                parts = [content[i:i+4000] for i in range(0, len(content), 4000)]
                                for i, part in enumerate(parts):
                                    part_message = f"--- الجزء {i+1} ---\n\n{part}"
                                    send(chat_id, part_message)
                            else:
                                # إرسال القصيدة كاملة
                                poem_message = f"📖 **{title}**\n\n---\n\n{content}\n\n✍️ {author}"
                                send(chat_id, poem_message)
                            
                            # إجابة على callback query
                            answer_cbq(cbq_id, "تم إرسال القصيدة")
                            
                            print(f"تم إرسال قصيدة: {title} للمستخدم {chat_id}")
                        else:
                            answer_cbq(cbq_id, f"❌ القصيدة غير موجودة (المؤشر: {poem_index}, العدد الإجمالي: {len(current_poems)})", show_alert=True)
                    except Exception as e:
                        print(f"خطأ في إرسال القصيدة: {e}")
                        answer_cbq(cbq_id, f"❌ خطأ في تحميل القصيدة: {str(e)}", show_alert=True)
                

                
            except Exception as e:
                print(f"Error processing callback query: {e}")
                try:
                    answer_cbq(cbq_id, "حدث خطأ، حاول مرة أخرى")
                except:
                    pass
            
        return jsonify({"status":"ok"})
    except Exception as e:
        print(f"Error in webhook: {e}")
        return jsonify({"status":"error"}), 500

application = app