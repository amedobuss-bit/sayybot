import os, requests, json
from flask import Flask, request, jsonify

# قراءة التوكن والسيكرت
def load_token_and_secret():
    bot_token = os.environ.get("TG_BOT_TOKEN", "").strip()
    secret_token = os.environ.get("SECRET_TOKEN", "").strip()
    
    if not bot_token:
        # محاولة قراءة من config.ini
        try:
            import configparser
            cfg = configparser.ConfigParser()
            cfg.read("config.ini", encoding="utf-8")
            bot_token = cfg.get("pyrogram", "bot_token")
            secret_token = cfg.get("webhook", "secret_token", fallback="default-secret-123")
        except:
            pass
    
    return bot_token, secret_token

BOT_TOKEN, SECRET = load_token_and_secret()
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

            # قسم أسامة بن لادن
            elif data == "show_osama_poems":
                answer_cbq(cbq_id)
                osama_poems = POEMS[:10] if POEMS else []
                keyboard = [[{"text": p.get("title", f"قصيدة {i+1}"), "callback_data": f"poem_{i}"}] for i, p in enumerate(osama_poems)]
                keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_archive"}])
                edit(chat_id, msg_id, "قائمة القصائد:\n\n(أسامة بن لادن)", reply_markup=kb(keyboard))

            # قسم أبو بلال الحربي
            elif data == "show_harbi_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "⚔️ اختر من مؤلفات أبي بلال الحربي:",
                     reply_markup=kb([
                         [{"text":"📖 وقفات مع الشيخ المربي","callback_data":"send_harbi_pdf_1"}],
                         [{"text":"📖 ماذا فعلت بنا يا سعد؟","callback_data":"send_harbi_pdf_2"}],
                         [{"text":"📜 قصيدة: إذا بزغت خيوط الشمس فينا","callback_data":"poem_20"}],
                         [{"text":"📜 قصيدة: وأرواح تطير بجوف طير","callback_data":"poem_21"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data == "send_harbi_pdf_1":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/وقفات مع الشيخ المربي.pdf", "📖 وقفات مع الشيخ المربي")
            elif data == "send_harbi_pdf_2":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/ماذا فعلت بنا يا سعد؟.pdf", "📖 ماذا فعلت بنا يا سعد؟")

            # قسم أبو حمزة المهاجر
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

            # قسم أبو أنس الفلسطيني
            elif data == "show_abu_anas":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/يوميات مجاهد من الفلوجة.pdf", "📖 كتاب يوميات مجاهد من الفلوجة (أبو أنس الفلسطيني)")

            # قسم ميسرة الغريب
            elif data == "show_mysara_gharib_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "📝 اختر كتاباً لـ ميسرة الغريب:",
                     reply_markup=kb([
                         [{"text":"كتاب: رمزيات","callback_data":"send_mysara_ramziyat"}],
                         [{"text":"كتاب: إنما شفاء العي السؤال","callback_data":"send_mysara_shifaa_alayi"}],
                         [{"text":"كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها","callback_data":"send_mysara_kurab"}],
                         [{"text":"بدمائهم نصحوا1","callback_data":"send_mysara_bidmaihim"}],
                         [{"text":"سلسلة: من خفايا التاريخ- الزرقاوي","callback_data":"send_mysara_zarqawi"}],
                         [{"text":"كتاب: قـالـوا.. فـقـل!","callback_data":"send_mysara_qalou_faqal"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data.startswith("send_mysara_"):
                book_map = {
                    "send_mysara_ramziyat": ("ميسرة الغريب/رَمْزِيَّات.pdf", "📝 كتاب: رمزيات"),
                    "send_mysara_shifaa_alayi": ("ميسرة الغريب/إنما شفاء العيّ السؤال.pdf", "📝 كتاب: إنما شفاء العي السؤال"),
                    "send_mysara_kurab": ("ميسرة الغريب/الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf", "📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها"),
                    "send_mysara_bidmaihim": ("ميسرة الغريب/سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf", "📝 بدمائهم نصحوا1"),
                    "send_mysara_zarqawi": ("ميسرة الغريب/سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf", "📝 سلسلة: من خفايا التاريخ- الزرقاوي"),
                    "send_mysara_qalou_faqal": ("ميسرة الغريب/قـالـوا.. فـقـل!.pdf", "📝 كتاب: قـالـوا.. فـقـل!"),
                }
                file_info = book_map.get(data)
                if file_info:
                    path, caption = file_info
                    full_path = f"قصائد المشروع/{path}"
                    full_caption = f"{caption} (ميسرة الغريب)"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, full_path, full_caption)

            # قسم أبو الحسن المهاجر
            elif data == "show_muhajir_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات أبي الحسن المهاجر:",
                     reply_markup=kb([
                         [{"text":"📚 الجامع لكلمات أبي الحسن المهاجر","callback_data":"send_muhajir_aljami"}],
                         [{"text":"📜 قصيدة: جيل المكرمات","callback_data":"poem_11"}],
                         [{"text":"📄 مقتطف حول علماء السوء","callback_data":"poem_12"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data == "send_muhajir_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو الحسن المهاجر/الجامع لكلمات أبي الحسن المهاجر.pdf", "📚 الجامع لكلمات أبي الحسن المهاجر")

            # قسم العدناني
            elif data == "show_adnani_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "🎙️ اختر من مؤلفات العدناني:",
                     reply_markup=kb([
                         [{"text":"📖 الجامع لكلمات العدناني","callback_data":"send_adnani_aljami"}],
                         [{"text":"📜 قصيدة معركة الفلوجة الثانية","callback_data":"send_adnani_qasida"}],
                         [{"text":"📄 قصيدة: إنّا لريب الدهر","callback_data":"poem_10"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data == "send_adnani_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/العدناني/الجامع للعدناني.pdf", "📖 الجامع لكلمات العدناني")
            elif data == "send_adnani_qasida":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/العدناني/قصيدة معركة الفلوجة الثانية.pdf", "📜 قصيدة معركة الفلوجة الثانية")

            # قسم أبو عمر المهاجر
            elif data == "show_abu_omar_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "👤 اختر من مؤلفات أبي عمر المهاجر:",
                     reply_markup=kb([
                         [{"text":"📜 قصيدة: لم يبق للدمع","callback_data":"poem_13"}],
                         [{"text":"📜 قصيدة: سنحكم بالشريعة كل شبر","callback_data":"poem_14"}],
                         [{"text":"📜 قصيدة: قوموا ضياغم دولة الإسلام","callback_data":"poem_15"}],
                         [{"text":"📄 قطعة: في غرب إفريقية الأبطالُ","callback_data":"poem_16"}],
                         [{"text":"📜 قصيدة: إن لي في السجون إخوان عز","callback_data":"poem_17"}],
                         [{"text":"📄 مقتطف: رسالة رابعة","callback_data":"poem_18"}],
                         [{"text":"📜 قصيدة: عين جودي","callback_data":"poem_19"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            # قسم أبو حمزة القرشي
            elif data == "show_qurashi_books":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو حمزة القرشي/الجامع لكلمات أبي حمزة القرشي.pdf", "🗣️ الجامع لكلمات أبي حمزة القرشي")

            # قسم أبو بكر المدني
            elif data == "show_abu_bakr_madani_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "📜 اختر كتاباً لـ أبو بكر المدني:",
                     reply_markup=kb([
                         [{"text":"لفت الأنظار لما جاء في الفلوجتين من أخبار1","callback_data":"send_abu_bakr_madani_laft_alanzar"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data == "send_abu_bakr_madani_laft_alanzar":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بكر المدني/لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf", "📜 كتاب: لفت الأنظار لما جاء في الفلوجتين من أخبار1 (أبو بكر المدني)")

            # قسم حسين المعاضيدي
            elif data == "show_hussein_almadidi":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/حسين المعاضيدي/هنا أرض الخلافة- حسين المعاضيدي.pdf", "⚔️ كتاب: هنا أرض الخلافة (حسين المعاضيدي)")

            # قسم أبو خيثمة
            elif data == "show_abu_khithama":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/قصائد دبجت بالدماء.pdf", "📘 ديوان الشاعر أبو خيثمة الشنقيطي")

            # قسم لويس
            elif data == "show_louis":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/لويس_مقالات.pdf", "📗 مجموعة مقالات لويس عطية الله")

            # قسم مرثد بن عبد الله
            elif data == "show_marthad_abdullah":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/مـرثد بن عبد الله/بعض من قصائد مرثد بن عبد الله.pdf", "✒️ بعض من قصائد مرثد بن عبد الله")

            # قسم أحلام النصر الدمشقية
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

            elif data == "show_aed_min_althalam_parts":
                answer_cbq(cbq_id)
                keyboard = [[{"text": f"الجزء {i}", "callback_data": f"send_aed_min_althalam_part_{i}"}] for i in range(1, 36)]
                keyboard.append([{"text":"⬅️ رجوع","callback_data":"show_ahlam_alnaser_books"}])
                edit(chat_id, msg_id, "📚 قصة: عائد من الظلام - اختر الجزء:", reply_markup=kb(keyboard))

            elif data.startswith("send_aed_min_althalam_part_"):
                try:
                    part_num = data.split("_")[-1]
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, f"قصائد المشروع/أوار الحق/أجزاء قصة عائد من الظلام/AMT-E{part_num}.pdf", f"🌸 قصة: عائد من الظلام - الجزء {part_num}")
                except:
                    answer_cbq(cbq_id, "خطأ في إرسال الملف", show_alert=True)

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

            # قسم الشاعر أبو مالك شيبة الحمد
            elif data == "show_shaybah_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات الشاعر أبـو مـالك شيبـة الحمـد:",
                     reply_markup=kb([
                         [{"text":"📖 أزفتْ نهايةُ جبهةِ الجولاني","callback_data":"send_shaybah_book_1"}],
                         [{"text":"📖 أنا مع أبي بكر","callback_data":"send_shaybah_book_2"}],
                         [{"text":"📖 الديوان العـرّيســة الشعري","callback_data":"send_shaybah_book_3"}],
                         [{"text":"📖 الستينية فى ذكر سلاطين الخلافة العثمانية","callback_data":"send_shaybah_book_4"}],
                         [{"text":"📖 ديوان عبرة وعبير","callback_data":"send_shaybah_book_5"}],
                         [{"text":"📖 سلام و إكرام لدولة الإسلام","callback_data":"send_shaybah_book_6"}],
                         [{"text":"📖 على نهج الرسول","callback_data":"send_shaybah_book_7"}],
                         [{"text":"📜 قصيدة سلام على سجن كوبر","callback_data":"send_shaybah_book_8"}],
                         [{"text":"📜 قصيدة أرق بالسيف كل دم كفور","callback_data":"send_shaybah_book_9"}],
                         [{"text":"📜 قصيدة جحاجح القوقاز","callback_data":"send_shaybah_book_10"}],
                         [{"text":"📜 قصيدة ذكـرتـك يـا أسـامـة","callback_data":"send_shaybah_book_11"}],
                         [{"text":"📜 قصيدة رحل الشّهيد وما رحل","callback_data":"send_shaybah_book_12"}],
                         [{"text":"📜 قصيدة صرخة من أزواد","callback_data":"send_shaybah_book_13"}],
                         [{"text":"📜 قصيدة فارس الإيمان","callback_data":"send_shaybah_book_14"}],
                         [{"text":"📜 قصيدة متنا دعاة على أبواب عزتنا","callback_data":"send_shaybah_book_15"}],
                         [{"text":"📜 قصيدة متى يكسر الشعب أغلاله","callback_data":"send_shaybah_book_16"}],
                         [{"text":"📜 قصيدة نصرة لعبد الكريم الحميد","callback_data":"send_shaybah_book_17"}],
                         [{"text":"📜 مرثية آل الشيخ أسامة","callback_data":"send_shaybah_book_18"}],
                         [{"text":"📜 يا أسيراً خلفَ قضبانِ العدا","callback_data":"send_shaybah_book_19"}],
                         [{"text":"📜 يـا دارَ سِـرْتَـ الفاتحيـنَ","callback_data":"send_shaybah_book_20"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data.startswith("send_shaybah_book_"):
                book_map = {
                    "send_shaybah_book_1": ("أزفتْ نهايةُ جبهةِ الجولاني - شيبة الحمد.pdf", "📖 أزفتْ نهايةُ جبهةِ الجولاني"),
                    "send_shaybah_book_2": ("أنا مع أبي بكر- شعر شيبة الحمد.pdf", "📖 أنا مع أبي بكر"),
                    "send_shaybah_book_3": ("الديوان العـرّيســة الشعري للشيخ شيبة الحمد.pdf", "📖 الديوان العـرّيســة الشعري"),
                    "send_shaybah_book_4": ("الستينية فى ذكر سلاطين الخلافة العثمانية بقلم شيبة الحمد -للتعديل.pdf", "📖 الستينية فى ذكر سلاطين الخلافة العثمانية"),
                    "send_shaybah_book_5": ("ديوان عبرة وعبير، شيبة الحمد.pdf", "📖 ديوان عبرة وعبير"),
                    "send_shaybah_book_6": ("سلام و إكرام لدولة الإسلام.pdf", "📖 سلام و إكرام لدولة الإسلام"),
                    "send_shaybah_book_7": ("على نهج الرسول - أبو مالك شيبة الحمد.pdf", "📖 على نهج الرسول"),
                    "send_shaybah_book_8": ("قصيدة سلام على سجن كوبر شيبة الحمد.pdf", "📜 قصيدة سلام على سجن كوبر"),
                    "send_shaybah_book_9": ("قصيدة أرق بالسيف كل دم كفور،_شيبة الحمد.pdf", "📜 قصيدة أرق بالسيف كل دم كفور"),
                    "send_shaybah_book_10": ("قصيدة جحاجح القوقاز - شيبة الحمد.pdf", "📜 قصيدة جحاجح القوقاز"),
                    "send_shaybah_book_11": ("قصيدة ذكـرتـك يـا أسـامـة دموع القلب شـيـبـة الـحـمـد.pdf", "📜 قصيدة ذكـرتـك يـا أسـامـة"),
                    "send_shaybah_book_12": ("قصيدة رحل الشّهيد وما رحل، شيبة الحمد.pdf", "📜 قصيدة رحل الشّهيد وما رحل"),
                    "send_shaybah_book_13": ("قصيدة صرخة من أزواد، شيبة الحمد.pdf", "📜 قصيدة صرخة من أزواد"),
                    "send_shaybah_book_14": ("قصيدة فارس الإيمان، شيبة الحمد.pdf", "📜 قصيدة فارس الإيمان"),
                    "send_shaybah_book_15": ("قصيدة متنا دعاة على أبواب عزتنا، شيبة الحمد.pdf", "📜 قصيدة متنا دعاة على أبواب عزتنا"),
                    "send_shaybah_book_16": ("قصيدة متى يكسر الشعب أغلاله، شيبة الحمد.pdf", "📜 قصيدة متى يكسر الشعب أغلاله"),
                    "send_shaybah_book_17": ("قصيدة نصرة لعبد الكريم_ الحميد، شيبة الحمد.pdf", "📜 قصيدة نصرة لعبد الكريم الحميد"),
                    "send_shaybah_book_18": ("مرثية آل الشيخ أسامة للشاعر شيبة الحمد.pdf", "📜 مرثية آل الشيخ أسامة"),
                    "send_shaybah_book_19": ("يا أسيراً خلفَ قضبانِ العدا.pdf", "📜 يا أسيراً خلفَ قضبانِ العدا"),
                    "send_shaybah_book_20": ("يـا دارَ سِـرْتَـ الفاتحيـنَ للشيخ شيبة الحمد.pdf", "📜 يـا دارَ سِـرْتَـ الفاتحيـنَ")
                }
                book_info = book_map.get(data)
                if book_info:
                    file_name, caption = book_info
                    path = f"قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/{file_name}"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, path, f"📖 {caption}")

            # قسم المهندس محمد الزهيري
            elif data == "show_zuhayri_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "👷 اختر من مؤلفات المهندس محمد الزهيري:",
                     reply_markup=kb([
                         [{"text":"📖 أعدنا القادسية في شموخٍ","callback_data":"send_zuhayri_book_1"}],
                         [{"text":"📖 ركزنا في ذرى الأمجاد رمحاً","callback_data":"send_zuhayri_book_2"}],
                         [{"text":"📖 ستزيد دعوتنا عزا وتمكينا","callback_data":"send_zuhayri_book_3"}],
                         [{"text":"📖 صليل الصوارم","callback_data":"send_zuhayri_book_4"}],
                         [{"text":"📖 عراق الله يزخر بالغياري","callback_data":"send_zuhayri_book_5"}],
                         [{"text":"📜 قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً","callback_data":"send_zuhayri_book_6"}],
                         [{"text":"📜 قصيدة يكفي محمدا أن الله حافظه","callback_data":"send_zuhayri_book_7"}],
                         [{"text":"📜 قصيدة ستزيد دعوتنا عزا","callback_data":"send_zuhayri_book_8"}],
                         [{"text":"📜 قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً","callback_data":"send_zuhayri_book_9"}],
                         [{"text":"📜 قصيدة نسجت لكم بقاني الدم","callback_data":"send_zuhayri_book_10"}],
                         [{"text":"📜 قصيدة نازلُ الأعماق للموت سعى","callback_data":"send_zuhayri_book_11"}],
                         [{"text":"📜 قصيدة نسجت لكم بقاني الدم عهدا","callback_data":"send_zuhayri_book_12"}],
                         [{"text":"📜 قصيدة هيهات ينــــزو كافـرٌ","callback_data":"send_zuhayri_book_13"}],
                         [{"text":"📜 قصيدة يا دولة التوحيد أينع زرعنا","callback_data":"send_zuhayri_book_14"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data.startswith("send_zuhayri_book_"):
                book_map = {
                    "send_zuhayri_book_1": ("أعدنا القادسية في شموخٍ - محمد الزهيري.pdf", "📖 أعدنا القادسية في شموخٍ"),
                    "send_zuhayri_book_2": ("ركزنا في ذرى الأمجاد رمحاً - محمد الزهيري.pdf", "📖 ركزنا في ذرى الأمجاد رمحاً"),
                    "send_zuhayri_book_3": ("ستزيد دعوتنا عزا وتمكينا -محمد الزهيري.pdf", "📖 ستزيد دعوتنا عزا وتمكينا"),
                    "send_zuhayri_book_4": ("صليل الصوارم - محمد الزهيري.pdf", "📖 صليل الصوارم"),
                    "send_zuhayri_book_5": ("عراق اﷲ یزخر بالغیارى محمد الزهيري.pdf", "📖 عراق الله يزخر بالغياري"),
                    "send_zuhayri_book_6": ("قصيدة [مَنْ مُبلغٍ كلبَ الروافض ياسراً - نصرة لأم المؤمنين عائشة (رضي الله عنها)] للزهيري.pdf", "📜 مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
                    "send_zuhayri_book_7": ("قصيدة يكفي محمدا أن الله حافظه للاخ محمد الزهيري.pdf", "📜 يكفي محمدا أن الله حافظه"),
                    "send_zuhayri_book_8": ("قصيدة_ستزيد_دعوتنا_عزا_محمد_الزهيري.pdf", "📜 قصيدة ستزيد دعوتنا عزا"),
                    "send_zuhayri_book_9": ("قصيدة_مَنْ_مُبلغٍ_كلبَ_الروافض_ياسراً_نصرة_لأم_المؤمنين_عائشة_رضي.pdf", "📜 قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
                    "send_zuhayri_book_10": ("قصيدة_نسجت_لكم_بقاني_الدم_محمد_الزهيري.pdf", "📜 قصيدة نسجت لكم بقاني الدم"),
                    "send_zuhayri_book_11": ("نازلُ الأعماق للموت سعى -محمد الزهيري.pdf", "📜 نازلُ الأعماق للموت سعى"),
                    "send_zuhayri_book_12": ("نسجت لكم بقاني الدم عهدا -محمد الزهيري.pdf", "📜 نسجت لكم بقاني الدم عهدا"),
                    "send_zuhayri_book_13": ("هيهات ينــــزو كافـرٌ - محمد الزهيري.pdf", "📜 هيهات ينــــزو كافـرٌ"),
                    "send_zuhayri_book_14": ("يا دولة التوحيد أينع زرعنا - محمد الزهيري.pdf", "📜 يا دولة التوحيد أينع زرعنا")
                }
                book_info = book_map.get(data)
                if book_info:
                    file_name, caption = book_info
                    path = f"قصائد المشروع/المهندس محمد الزهيري/{file_name}"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, path, f"📖 {caption}")

            # قسم بنت نجد
            elif data == "show_bint_najd_books":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات بنت نجد:",
                     reply_markup=kb([
                         [{"text":"✍️ أمسِكْ لسانكَ يا قُنيبي","callback_data":"send_bint_najd_book_1"}],
                         [{"text":"✍️ فرعونُ نجد ستنتهي أيامهُ","callback_data":"send_bint_najd_book_2"}],
                         [{"text":"✍️ مادحة للعدناني هاجية للجولاني","callback_data":"send_bint_najd_book_3"}],
                         [{"text":"✍️ هذه دولة الإسلام، ياعشماوي","callback_data":"send_bint_najd_book_4"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data.startswith("send_bint_najd_book_"):
                book_map = {
                    "send_bint_najd_book_1": ("أمسِكْ لسانكَ يا قُنيبي.pdf", "✍️ أمسِكْ لسانكَ يا قُنيبي"),
                    "send_bint_najd_book_2": ("فرعونُ نجد ستنتهي أيامهُ.pdf", "✍️ فرعونُ نجد ستنتهي أيامهُ"),
                    "send_bint_najd_book_3": ("مادحة للعدناني هاجية للجولاني.pdf", "✍️ مادحة للعدناني هاجية للجولاني"),
                    "send_bint_najd_book_4": ("هذه دولة الإسلام، ياعشماوي - بنت نجد.pdf", "✍️ هذه دولة الإسلام، ياعشماوي")
                }
                book_info = book_map.get(data)
                if book_info:
                    file_name, caption = book_info
                    path = f"قصائد المشروع/بنت نجد/{file_name}"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, path, f"✍️ {caption}")

            # قسم العقاب المصري
            elif data == "show_oqab_masri":
                answer_cbq(cbq_id)
                edit(chat_id, msg_id, "🦅 اختر من مؤلفات العقاب المصري:",
                     reply_markup=kb([
                         [{"text":"🦅 إلى ابْنَتي مَوَدَّة","callback_data":"send_oqab_book_1"}],
                         [{"text":"🦅 هنا الخلافة - ديوان شعري","callback_data":"send_oqab_book_2"}],
                         [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                     ]))

            elif data.startswith("send_oqab_book_"):
                book_map = {
                    "send_oqab_book_1": ("إلى ابْنَتي مَوَدَّة.pdf", "🦅 إلى ابْنَتي مَوَدَّة"),
                    "send_oqab_book_2": ("هنا الخلافة- ديوان شعري العقاب المصري.pdf", "🦅 هنا الخلافة - ديوان شعري")
                }
                book_info = book_map.get(data)
                if book_info:
                    file_name, caption = book_info
                    path = f"قصائد المشروع/العقاب المصري/{file_name}"
                    answer_cbq(cbq_id, "سيتم إرسال الملف")
                    send_doc(chat_id, path, f"🦅 {caption}")

            # معالجة القصائد النصية
            elif data.startswith("poem_"):
                try:
                    idx = int(data.split("_")[1])
                    if 0 <= idx < len(POEMS):
                        poem = POEMS[idx]
                        poem_text = f"📖 **{poem.get('title', f'قصيدة {idx+1}')}**\n\n---\n\n{poem.get('content', '')}"
                        
                        # تحديد زر الرجوع المناسب
                        return_callback = "show_archive"
                        if 0 <= idx <= 9: return_callback = "show_osama_poems"
                        elif idx == 10: return_callback = "show_adnani_books"
                        elif 11 <= idx <= 12: return_callback = "show_muhajir_books"
                        elif 13 <= idx <= 19: return_callback = "show_abu_omar_books"
                        elif idx == 20: return_callback = "show_harbi_books"
                        
                        edit(chat_id, msg_id, poem_text, 
                             reply_markup=kb([[{"text":"⬅️ رجوع","callback_data":return_callback}]]))
                    else:
                        answer_cbq(cbq_id, "عذراً، القصيدة المطلوبة غير موجودة.", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في عرض القصيدة", show_alert=True)

        return jsonify({"status":"ok"})
    except Exception as e:
        print(f"Error in webhook: {e}")
        return jsonify({"status":"error"}), 500

application = app
