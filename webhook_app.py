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
            
            if text == "/start":
                keyboard = kb([
                    [{"text":"انتقل إلى مادة الأرشيف","callback_data":"show_archive"}]
                ])
                send(chat_id, INTRO_MESSAGE, keyboard)
                return "OK", 200
        
        # معالجة Callback Queries
        elif upd.get("callback_query"):
            cbq = upd["callback_query"]
            cbq_id = cbq["id"]
            data = cbq.get("data", "")
            chat_id = cbq["message"]["chat"]["id"]
            msg_id = cbq["message"]["message_id"]
            
            # القائمة الرئيسية
            if data == "show_archive":
                answer_cbq(cbq_id)
                keyboard = kb([
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
                edit(chat_id, msg_id, "اختر مجموعة القصائد:", keyboard)
            
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
                keyboard = kb([
                    [{"text":"📖 وقفات مع الشيخ المربي","callback_data":"send_harbi_pdf_1"}],
                    [{"text":"📖 ماذا فعلت بنا يا سعد؟","callback_data":"send_harbi_pdf_2"}],
                    [{"text":"📜 قصيدة: إذا بزغت خيوط الشمس فينا","callback_data":"poem_20"}],
                    [{"text":"📜 قصيدة: وأرواح تطير بجوف طير","callback_data":"poem_21"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "⚔️ اختر من مؤلفات أبي بلال الحربي:", keyboard)
            
            elif data == "send_harbi_pdf_1":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/وقفات مع الشيخ المربي.pdf", "📖 وقفات مع الشيخ المربي")
            
            elif data == "send_harbi_pdf_2":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بلال الحربي/ماذا فعلت بنا يا سعد؟.pdf", "📖 ماذا فعلت بنا يا سعد؟")
            
            # قسم أبو حمزة المهاجر
            elif data == "show_abu_hamza_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📚 الجامع لكلمات أبي حمزة المهاجر","callback_data":"send_abu_hamza_aljami"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات أبي حمزة المهاجر:", keyboard)
            
            elif data == "send_abu_hamza_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو حمزة المهاجر/الجامع لكلمات أبي حمزة المهاجر.pdf", "📚 الجامع لكلمات أبي حمزة المهاجر")
            
            # قسم أبو أنس الفلسطيني
            elif data == "show_abu_anas":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📖 كتاب يوميات مجاهد من الفلوجة","callback_data":"send_abu_anas_book"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "🇵🇸 اختر من مؤلفات أبي أنس الفلسطيني:", keyboard)
            
            elif data == "send_abu_anas_book":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/يوميات مجاهد من الفلوجة.pdf", "📖 كتاب يوميات مجاهد من الفلوجة (أبو أنس الفلسطيني)")
            
            # قسم ميسرة الغريب
            elif data == "show_mysara_gharib_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📝 كتاب: رمزيات","callback_data":"send_mysara_ramziyat"}],
                    [{"text":"📝 كتاب: إنما شفاء العي السؤال","callback_data":"send_mysara_shifaa_alayi"}],
                    [{"text":"📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها","callback_data":"send_mysara_kurab"}],
                    [{"text":"📝 بدمائهم نصحوا1","callback_data":"send_mysara_bidmaihim"}],
                    [{"text":"📝 سلسلة: من خفايا التاريخ- الزرقاوي","callback_data":"send_mysara_zarqawi"}],
                    [{"text":"📝 كتاب: قـالـوا.. فـقـل!","callback_data":"send_mysara_qalou_faqal"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📝 اختر من مؤلفات ميسرة الغريب:", keyboard)
            
            elif data == "send_mysara_ramziyat":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/رَمْزِيَّات.pdf", "📝 كتاب: رمزيات (ميسرة الغريب)")
            
            elif data == "send_mysara_shifaa_alayi":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/إنما شفاء العيّ السؤال.pdf", "📝 كتاب: إنما شفاء العي السؤال (ميسرة الغريب)")
            
            elif data == "send_mysara_kurab":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/الكُرَبُ وسُبُلُ تَفْرِيجِها.pdf", "📝 كتاب: الكُرَبُ وسُبُلُ تَفْرِيجِها (ميسرة الغريب)")
            
            elif data == "send_mysara_bidmaihim":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/سلسلة بدمائهم نصحوا 1.. منهج حياة.pdf", "📝 بدمائهم نصحوا1 (ميسرة الغريب)")
            
            elif data == "send_mysara_zarqawi":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/سلسلة_من_خفايا_التاريخ_الزرقاوي.pdf", "📝 سلسلة: من خفايا التاريخ- الزرقاوي (ميسرة الغريب)")
            
            elif data == "send_mysara_qalou_faqal":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/ميسرة الغريب/قـالـوا.. فـقـل!.pdf", "📝 كتاب: قـالـوا.. فـقـل! (ميسرة الغريب)")
            
            # قسم أبو الحسن المهاجر
            elif data == "show_muhajir_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📚 الجامع لكلمات أبي الحسن المهاجر","callback_data":"send_muhajir_aljami"}],
                    [{"text":"📜 قصيدة: جيل المكرمات","callback_data":"poem_11"}],
                    [{"text":"📄 مقتطف حول علماء السوء","callback_data":"poem_12"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات أبي الحسن المهاجر:", keyboard)
            
            elif data == "send_muhajir_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو الحسن المهاجر/الجامع لكلمات أبي الحسن المهاجر.pdf", "📚 الجامع لكلمات أبي الحسن المهاجر")
            
            # قسم العدناني
            elif data == "show_adnani_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📖 الجامع لكلمات العدناني","callback_data":"send_adnani_aljami"}],
                    [{"text":"📜 قصيدة معركة الفلوجة الثانية","callback_data":"send_adnani_qasida"}],
                    [{"text":"📄 قصيدة: إنّا لريب الدهر","callback_data":"poem_10"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "🎙️ اختر من مؤلفات العدناني:", keyboard)
            
            elif data == "send_adnani_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/العدناني/الجامع للعدناني.pdf", "📖 الجامع لكلمات العدناني")
            
            elif data == "send_adnani_qasida":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/العدناني/قصيدة معركة الفلوجة الثانية.pdf", "📜 قصيدة معركة الفلوجة الثانية")
            
            # قسم أبو عمر المهاجر
            elif data == "show_abu_omar_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📜 قصيدة: لم يبق للدمع","callback_data":"poem_13"}],
                    [{"text":"📜 قصيدة: سنحكم بالشريعة كل شبر","callback_data":"poem_14"}],
                    [{"text":"📜 قصيدة: قوموا ضياغم دولة الإسلام","callback_data":"poem_15"}],
                    [{"text":"📄 قطعة: في غرب إفريقية الأبطالُ","callback_data":"poem_16"}],
                    [{"text":"📜 قصيدة: إن لي في السجون إخوان عز","callback_data":"poem_17"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📜 اختر من مؤلفات أبي عمر المهاجر:", keyboard)
            
            # قسم أبو حمزة القرشي
            elif data == "show_qurashi_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📚 الجامع لكلمات أبي حمزة القرشي","callback_data":"send_qurashi_aljami"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📚 اختر من مؤلفات أبي حمزة القرشي:", keyboard)
            
            elif data == "send_qurashi_aljami":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو حمزة القرشي/الجامع لكلمات أبي حمزة القرشي.pdf", "📚 الجامع لكلمات أبي حمزة القرشي")
            
            # قسم أبو بكر المدني
            elif data == "show_abu_bakr_madani_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"لفت الأنظار لما جاء في الفلوجتين من أخبار1","callback_data":"send_abu_bakr_madani_laft_alanzar"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📜 اختر كتاباً لـ أبو بكر المدني:", keyboard)
            
            elif data == "send_abu_bakr_madani_laft_alanzar":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/أبو بكر المدني/لفت_الأنظار_لما_جاء_في_الفلوجتين_من_أخبار_1.pdf", "📜 كتاب: لفت الأنظار لما جاء في الفلوجتين من أخبار1 (أبو بكر المدني)")
            
            # قسم حسين المعاضيدي
            elif data == "show_hussein_almadidi":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📖 كتاب: هنا أرض الخلافة","callback_data":"send_hussein_book"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "⚔️ اختر من مؤلفات حسين المعاضيدي:", keyboard)
            
            elif data == "send_hussein_book":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/حسين المعاضيدي/هنا أرض الخلافة- حسين المعاضيدي.pdf", "⚔️ كتاب: هنا أرض الخلافة (حسين المعاضيدي)")
            
            # قسم أبو خيثمة الشنقيطي
            elif data == "show_abu_khithama":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📘 ديوان الشاعر أبو خيثمة الشنقيطي","callback_data":"send_abu_khithama_book"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📘 اختر من مؤلفات أبو خيثمة الشنقيطي:", keyboard)
            
            elif data == "send_abu_khithama_book":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/قصائد دبجت بالدماء.pdf", "📘 ديوان الشاعر أبو خيثمة الشنقيطي")
            
            # قسم لويس عطية الله
            elif data == "show_louis":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📗 مجموعة مقالات لويس عطية الله","callback_data":"send_louis_book"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "📗 اختر من مؤلفات لويس عطية الله:", keyboard)
            
            elif data == "send_louis_book":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/لويس_مقالات.pdf", "📗 مجموعة مقالات لويس عطية الله")
            
            # قسم مرثد بن عبد الله
            elif data == "show_marthad_abdullah":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"✒️ بعض من قصائد مرثد بن عبد الله","callback_data":"send_marthad_book"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "✒️ اختر من مؤلفات مرثد بن عبد الله:", keyboard)
            
            elif data == "send_marthad_book":
                answer_cbq(cbq_id, "سيتم إرسال الملف")
                send_doc(chat_id, "قصائد المشروع/مـرثد بن عبد الله/بعض من قصائد مرثد بن عبد الله.pdf", "✒️ بعض من قصائد مرثد بن عبد الله")
            
            # قسم أحلام النصر الدمشقية
            elif data == "show_ahlam_alnaser_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📚 قصة: عائد من الظلام (كل الأجزاء)","callback_data":"show_aed_min_althalam_parts"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "🌸 اختر من مؤلفات أحلام النصر الدمشقية:", keyboard)
            
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
            
            # قسم الشاعر أبو مالك شيبة الحمد
            elif data == "show_shaybah_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📖 أزفتْ نهايةُ جبهةِ الجولاني","callback_data":"send_shaybah_book_1"}],
                    [{"text":"📖 أنا مع أبي بكر","callback_data":"send_shaybah_book_2"}],
                    [{"text":"📖 الديوان العـرّيســة الشعري","callback_data":"send_shaybah_book_3"}],
                    [{"text":"📖 الستينية فى ذكر سلاطين الخلافة العثمانية","callback_data":"send_shaybah_book_4"}],
                    [{"text":"📖 ديوان عبرة وعبير","callback_data":"send_shaybah_book_5"}],
                    [{"text":"📖 سلام و إكرام لدولة الإسلام","callback_data":"send_shaybah_book_6"}],
                    [{"text":"📖 على نهج الرسول","callback_data":"send_shaybah_book_7"}],
                    [{"text":"📖 قصيدة سلام على سجن كوبر","callback_data":"send_shaybah_book_8"}],
                    [{"text":"📖 قصيدة أرق بالسيف كل دم كفور","callback_data":"send_shaybah_book_9"}],
                    [{"text":"📖 قصيدة جحاجح القوقاز","callback_data":"send_shaybah_book_10"}],
                    [{"text":"📖 قصيدة ذكـرتـك يـا أسـامـة","callback_data":"send_shaybah_book_11"}],
                    [{"text":"📖 قصيدة رحل الشّهيد وما رحل","callback_data":"send_shaybah_book_12"}],
                    [{"text":"📖 قصيدة صرخة من أزواد","callback_data":"send_shaybah_book_13"}],
                    [{"text":"📖 قصيدة فارس الإيمان","callback_data":"send_shaybah_book_14"}],
                    [{"text":"📖 قصيدة متنا دعاة على أبواب عزتنا","callback_data":"send_shaybah_book_15"}],
                    [{"text":"📖 قصيدة متى يكسر الشعب أغلاله","callback_data":"send_shaybah_book_16"}],
                    [{"text":"📖 قصيدة نصرة لعبد الكريم الحميد","callback_data":"send_shaybah_book_17"}],
                    [{"text":"📖 مرثية آل الشيخ أسامة","callback_data":"send_shaybah_book_18"}],
                    [{"text":"📖 يا أسيراً خلفَ قضبانِ العدا","callback_data":"send_shaybah_book_19"}],
                    [{"text":"📖 يـا دارَ سِـرْتَـ الفاتحيـنَ","callback_data":"send_shaybah_book_20"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات الشاعر أبـو مـالك شيبـة الحمـد:", keyboard)
            
            elif data.startswith("send_shaybah_book_"):
                try:
                    book_num = data.split("_")[-1]
                    book_map = {
                        "1": ("أزفتْ نهايةُ جبهةِ الجولاني - شيبة الحمد.pdf", "أزفتْ نهايةُ جبهةِ الجولاني"),
                        "2": ("أنا مع أبي بكر- شعر شيبة الحمد.pdf", "أنا مع أبي بكر"),
                        "3": ("الديوان العـرّيســة الشعري للشيخ شيبة الحمد.pdf", "الديوان العـرّيســة الشعري"),
                        "4": ("الستينية فى ذكر سلاطين الخلافة العثمانية بقلم شيبة الحمد -للتعديل.pdf", "الستينية فى ذكر سلاطين الخلافة العثمانية"),
                        "5": ("ديوان عبرة وعبير، شيبة الحمد.pdf", "ديوان عبرة وعبير"),
                        "6": ("سلام و إكرام لدولة الإسلام.pdf", "سلام و إكرام لدولة الإسلام"),
                        "7": ("على نهج الرسول - أبو مالك شيبة الحمد.pdf", "على نهج الرسول"),
                        "8": ("قصيدة سلام على سجن كوبر شيبة الحمد.pdf", "قصيدة سلام على سجن كوبر"),
                        "9": ("قصيدة أرق بالسيف كل دم كفور،_شيبة الحمد.pdf", "قصيدة أرق بالسيف كل دم كفور"),
                        "10": ("قصيدة جحاجح القوقاز - شيبة الحمد.pdf", "قصيدة جحاجح القوقاز"),
                        "11": ("قصيدة ذكـرتـك يـا أسـامـة دموع القلب شـيـبـة الـحـمـد.pdf", "قصيدة ذكـرتـك يـا أسـامـة"),
                        "12": ("قصيدة رحل الشّهيد وما رحل، شيبة الحمد.pdf", "قصيدة رحل الشّهيد وما رحل"),
                        "13": ("قصيدة صرخة من أزواد، شيبة الحمد.pdf", "قصيدة صرخة من أزواد"),
                        "14": ("قصيدة فارس الإيمان، شيبة الحمد.pdf", "قصيدة فارس الإيمان"),
                        "15": ("قصيدة متنا دعاة على أبواب عزتنا، شيبة الحمد.pdf", "قصيدة متنا دعاة على أبواب عزتنا"),
                        "16": ("قصيدة متى يكسر الشعب أغلاله، شيبة الحمد.pdf", "قصيدة متى يكسر الشعب أغلاله"),
                        "17": ("قصيدة نصرة لعبد الكريم_ الحميد، شيبة الحمد.pdf", "قصيدة نصرة لعبد الكريم الحميد"),
                        "18": ("مرثية آل الشيخ أسامة للشاعر شيبة الحمد.pdf", "مرثية آل الشيخ أسامة"),
                        "19": ("يا أسيراً خلفَ قضبانِ العدا.pdf", "يا أسيراً خلفَ قضبانِ العدا"),
                        "20": ("يـا دارَ سِـرْتَـ الفاتحيـنَ للشيخ شيبة الحمد.pdf", "يـا دارَ سِـرْتَـ الفاتحيـنَ")
                    }
                    if book_num in book_map:
                        file_name, caption = book_map[book_num]
                        answer_cbq(cbq_id, "سيتم إرسال الملف")
                        send_doc(chat_id, f"قصائد المشروع/الشاعر أبـو مـالك شيبـة الحمـد/{file_name}", f"📖 {caption}")
                    else:
                        answer_cbq(cbq_id, "الكتاب غير موجود", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في إرسال الملف", show_alert=True)
            
            # قسم المهندس محمد الزهيري
            elif data == "show_zuhayri_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"📖 أعدنا القادسية في شموخٍ","callback_data":"send_zuhayri_book_1"}],
                    [{"text":"📖 ركزنا في ذرى الأمجاد رمحاً","callback_data":"send_zuhayri_book_2"}],
                    [{"text":"📖 ستزيد دعوتنا عزا وتمكينا","callback_data":"send_zuhayri_book_3"}],
                    [{"text":"📖 صليل الصوارم","callback_data":"send_zuhayri_book_4"}],
                    [{"text":"📖 عراق الله يزخر بالغياري","callback_data":"send_zuhayri_book_5"}],
                    [{"text":"📖 مَنْ مُبلغٍ كلبَ الروافض ياسراً","callback_data":"send_zuhayri_book_6"}],
                    [{"text":"📖 يكفي محمدا أن الله حافظه","callback_data":"send_zuhayri_book_7"}],
                    [{"text":"📖 قصيدة ستزيد دعوتنا عزا","callback_data":"send_zuhayri_book_8"}],
                    [{"text":"📖 قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً","callback_data":"send_zuhayri_book_9"}],
                    [{"text":"📖 قصيدة نسجت لكم بقاني الدم","callback_data":"send_zuhayri_book_10"}],
                    [{"text":"📖 نازلُ الأعماق للموت سعى","callback_data":"send_zuhayri_book_11"}],
                    [{"text":"📖 نسجت لكم بقاني الدم عهدا","callback_data":"send_zuhayri_book_12"}],
                    [{"text":"📖 هيهات ينــــزو كافـرٌ","callback_data":"send_zuhayri_book_13"}],
                    [{"text":"📖 يا دولة التوحيد أينع زرعنا","callback_data":"send_zuhayri_book_14"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "👷 اختر من مؤلفات المهندس محمد الزهيري:", keyboard)
            
            elif data.startswith("send_zuhayri_book_"):
                try:
                    book_num = data.split("_")[-1]
                    book_map = {
                        "1": ("أعدنا القادسية في شموخٍ - محمد الزهيري.pdf", "أعدنا القادسية في شموخٍ"),
                        "2": ("ركزنا في ذرى الأمجاد رمحاً - محمد الزهيري.pdf", "ركزنا في ذرى الأمجاد رمحاً"),
                        "3": ("ستزيد دعوتنا عزا وتمكينا -محمد الزهيري.pdf", "ستزيد دعوتنا عزا وتمكينا"),
                        "4": ("صليل الصوارم - محمد الزهيري.pdf", "صليل الصوارم"),
                        "5": ("عراق اﷲ یزخر بالغیارى محمد الزهيري.pdf", "عراق الله يزخر بالغياري"),
                        "6": ("قصيدة [مَنْ مُبلغٍ كلبَ الروافض ياسراً - نصرة لأم المؤمنين عائشة (رضي الله عنها)] للزهيري.pdf", "مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
                        "7": ("قصيدة يكفي محمدا أن الله حافظه للاخ محمد الزهيري.pdf", "يكفي محمدا أن الله حافظه"),
                        "8": ("قصيدة_ستزيد_دعوتنا_عزا_محمد_الزهيري.pdf", "قصيدة ستزيد دعوتنا عزا"),
                        "9": ("قصيدة_مَنْ_مُبلغٍ_كلبَ_الروافض_ياسراً_نصرة_لأم_المؤمنين_عائشة_رضي.pdf", "قصيدة مَنْ مُبلغٍ كلبَ الروافض ياسراً"),
                        "10": ("قصيدة_نسجت_لكم_بقاني_الدم_محمد_الزهيري.pdf", "قصيدة نسجت لكم بقاني الدم"),
                        "11": ("نازلُ الأعماق للموت سعى -محمد الزهيري.pdf", "نازلُ الأعماق للموت سعى"),
                        "12": ("نسجت لكم بقاني الدم عهدا -محمد الزهيري.pdf", "نسجت لكم بقاني الدم عهدا"),
                        "13": ("هيهات ينــــزو كافـرٌ - محمد الزهيري.pdf", "هيهات ينــــزو كافـرٌ"),
                        "14": ("يا دولة التوحيد أينع زرعنا - محمد الزهيري.pdf", "يا دولة التوحيد أينع زرعنا")
                    }
                    if book_num in book_map:
                        file_name, caption = book_map[book_num]
                        answer_cbq(cbq_id, "سيتم إرسال الملف")
                        send_doc(chat_id, f"قصائد المشروع/المهندس محمد الزهيري/{file_name}", f"📖 {caption}")
                    else:
                        answer_cbq(cbq_id, "الكتاب غير موجود", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في إرسال الملف", show_alert=True)
            
            # قسم بنت نجد
            elif data == "show_bint_najd_books":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"✍️ أمسِكْ لسانكَ يا قُنيبي","callback_data":"send_bint_najd_book_1"}],
                    [{"text":"✍️ فرعونُ نجد ستنتهي أيامهُ","callback_data":"send_bint_najd_book_2"}],
                    [{"text":"✍️ مادحة للعدناني هاجية للجولاني","callback_data":"send_bint_najd_book_3"}],
                    [{"text":"✍️ هذه دولة الإسلام، ياعشماوي","callback_data":"send_bint_najd_book_4"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "✍️ اختر من مؤلفات بنت نجد:", keyboard)
            
            elif data.startswith("send_bint_najd_book_"):
                try:
                    book_num = data.split("_")[-1]
                    book_map = {
                        "1": ("أمسِكْ لسانكَ يا قُنيبي.pdf", "أمسِكْ لسانكَ يا قُنيبي"),
                        "2": ("فرعونُ نجد ستنتهي أيامهُ.pdf", "فرعونُ نجد ستنتهي أيامهُ"),
                        "3": ("مادحة للعدناني هاجية للجولاني.pdf", "مادحة للعدناني هاجية للجولاني"),
                        "4": ("هذه دولة الإسلام، ياعشماوي - بنت نجد.pdf", "هذه دولة الإسلام، ياعشماوي")
                    }
                    if book_num in book_map:
                        file_name, caption = book_map[book_num]
                        answer_cbq(cbq_id, "سيتم إرسال الملف")
                        send_doc(chat_id, f"قصائد المشروع/بنت نجد/{file_name}", f"✍️ {caption}")
                    else:
                        answer_cbq(cbq_id, "الكتاب غير موجود", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في إرسال الملف", show_alert=True)
            
            # قسم العقاب المصري
            elif data == "show_oqab_masri":
                answer_cbq(cbq_id)
                keyboard = kb([
                    [{"text":"🦅 إلى ابْنَتي مَوَدَّة","callback_data":"send_oqab_book_1"}],
                    [{"text":"🦅 هنا الخلافة - ديوان شعري","callback_data":"send_oqab_book_2"}],
                    [{"text":"⬅️ رجوع","callback_data":"show_archive"}]
                ])
                edit(chat_id, msg_id, "🦅 اختر من مؤلفات العقاب المصري:", keyboard)
            
            elif data.startswith("send_oqab_book_"):
                try:
                    book_num = data.split("_")[-1]
                    book_map = {
                        "1": ("إلى ابْنَتي مَوَدَّة.pdf", "إلى ابْنَتي مَوَدَّة"),
                        "2": ("هنا الخلافة- ديوان شعري العقاب المصري.pdf", "هنا الخلافة - ديوان شعري")
                    }
                    if book_num in book_map:
                        file_name, caption = book_map[book_num]
                        answer_cbq(cbq_id, "سيتم إرسال الملف")
                        send_doc(chat_id, f"قصائد المشروع/العقاب المصري/{file_name}", f"🦅 {caption}")
                    else:
                        answer_cbq(cbq_id, "الكتاب غير موجود", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في إرسال الملف", show_alert=True)
            
            # معالجة القصائد النصية
            elif data.startswith("poem_"):
                try:
                    idx = int(data.split("_")[1])
                    if 0 <= idx < len(POEMS):
                        poem = POEMS[idx]
                        return_callback = "show_archive"
                        if 0 <= idx <= 9: 
                            return_callback = "show_osama_poems"
                        elif idx == 10: 
                            return_callback = "show_adnani_books"
                        elif 11 <= idx <= 12: 
                            return_callback = "show_muhajir_books"
                        elif 13 <= idx <= 19: 
                            return_callback = "show_abu_omar_books"
                        elif 20 <= idx <= 21: 
                            return_callback = "show_harbi_books"
                        
                        keyboard = kb([[{"text":"⬅️ رجوع","callback_data":return_callback}]])
                        edit(chat_id, msg_id, f"📖 **{poem.get('title', f'قصيدة {idx+1}')}**\n\n---\n\n{poem.get('content', '')}", keyboard)
                    else:
                        answer_cbq(cbq_id, "عذراً، القصيدة المطلوبة غير موجودة.", show_alert=True)
                except:
                    answer_cbq(cbq_id, "خطأ في عرض القصيدة", show_alert=True)
        
        return "OK", 200
    except Exception as e:
        print(f"خطأ في webhook: {e}")
        return "OK", 200

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# تعيين التطبيق للـ WSGI
application = app
