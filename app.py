
import os
import random
import string
import base64
import requests
from datetime import date, datetime, timedelta
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'future-500-years'

# تنظیمات دیتابیس رندر
db_url = 'postgresql+psycopg2://myuser:5VAUU122WDEqj8UepCJypXIpdA8Vl8ip@dpg-dbi7boui0phs73d2ime0-a.oregon-postgres.render.com/mydb_ecw3'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ----------------- مدل‌های دیتابیس -----------------
class Business(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    unique_code = db.Column(db.String(10), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    last_login = db.Column(db.Date)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='سطح ۱')
    resolved = db.Column(db.Boolean, default=False)
    is_business = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Business.query.get(int(user_id))

# ----------------- موتور هوش مصنوعی -----------------
def analyze_emotion(text):
    text = text.lower()
    if any(w in text for w in ['خوشحال', 'عالی', 'شاد', 'خوب', 'رضایت']):
        return 'رضایت 😊'
    if any(w in text for w in ['غمگین', 'خسته', 'بد', 'ناراضی', 'عصبی', 'پیر', 'ترس']):
        return 'نارضایتی 😢'
    return 'خنثی 😐'

def aura_brain(user_input, person_name="عزیز از دست رفته", is_business=False):
# بررسی می‌کنیم که آیا اصلاً توکن در سرور تعریف شده است یا نه
    hf_token = os.environ.get('HF_TOKEN')

    if not hf_token:
        return "سیستم هوش مصنوعی هنوز راه‌اندازی نشده است. لطفاً بعداً تلاش کنید."  
    if is_business:
        prompt = f"تو یک دستیار هوشمند کافه/هتل هستی. کاربر می‌گوید: {user_input}. یک پاسخ کوتاه، دوستانه و تجاری بده."
    else:
        prompt = f"تو نسخه‌ی {person_name} هستی که از دنیای دیگر با کاربر صحبت می‌کنی. کاربر می‌گوید: {user_input}. یک پاسخ بسیار احساسی، عرفانی و دلسوزانه بده. حداکثر ۳ جمله."

    try:
         API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        # ⚠️ در خط زیر، به جای hf_کلید_خود_را_اینجا_بچسبانید، کلیدی که ساختی را پیست کن
         headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}

        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 100, "return_full_text": False}
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)

        if response.status_code == 200:
            result = response.json()
            return result[0]['generated_text'].strip()
        else:
            return "ارتباط با جهان دیگر برقرار نشد. لطفاً دوباره تلاش کنید."
    except:
        return "ارتباط با جهان دیگر برقرار نشد. لطفاً دوباره تلاش کنید."


# ----------------- CSS -----------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background: radial-gradient(circle at center, #1a2a6c, #0d0d2b, #000); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #fff; overflow-x: hidden; perspective: 1000px; }
.glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.2); padding: 40px; width: 100%; max-width: 600px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; z-index: 10; position: relative; overflow: hidden; }
h1 { font-size: 2.5rem; margin-bottom: 20px; text-shadow: 0 0 20px #00ffcc; }
input, select, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; font-family: 'Vazirmatn', Tahoma; outline: none; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); }
button { cursor: pointer; font-weight: bold; background: #00ffcc; color: #000; transition: 0.3s; border-radius: 30px; }
button:hover { transform: scale(1.05); box-shadow: 0 0 20px #00ffcc; }
a { text-decoration: none; display: block; margin-top: 15px; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; transition: 0.3s; }
a:hover { color: #fff; }
.msg { padding: 15px; margin-top: 15px; border-radius: 10px; text-align: right; background: rgba(255,255,255,0.05); border-left: 4px solid #00ffcc; }
.secret-star { position: fixed; top: 20px; left: 20px; font-size: 30px; color: gold; cursor: pointer; z-index: 100; animation: pulse 2s infinite; text-decoration: none;}
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
.typing-effect { overflow: hidden; border-right: .15em solid #00ffcc; white-space: nowrap; letter-spacing: .05em; animation: typing 3s steps(40, end); color: #00ffcc; font-size: 1.1rem; display: inline-block; }
@keyframes typing { from { width: 0 } to { width: 100% } }
.future-image { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin: 15px auto; border: 3px solid #00ffcc; box-shadow: 0 0 30px #00ffcc; filter: grayscale(100%) sepia(30%) blur(1px); transition: 0.5s; }
.emoji-btn { font-size: 2.5rem; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; cursor: pointer; transition: all 0.3s ease; color: #fff; margin: 5px; }
.emoji-btn:hover { transform: scale(1.2); background: rgba(0,255,204,0.2); border-color: #00ffcc; box-shadow: 0 0 20px #00ffcc; }
.emoji-btn.selected { transform: scale(1.2); background: #00ffcc; color: #000; box-shadow: 0 0 30px #00ffcc; }
.qr-section { background: rgba(0, 255, 204, 0.1); border: 1px dashed #00ffcc; padding: 20px; border-radius: 20px; margin-bottom: 30px; text-align: center; }
.qr-image { width: 150px; height: 150px; border-radius: 10px; margin-top: 15px; border: 2px solid #00ffcc; display: none; }
.bg-video { position: fixed; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -1; opacity: 0.15; filter: blur(5px); }
.feedback-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; margin-bottom: 15px; }
.emotion-tag { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; background: #00ffcc; color: #000; font-weight: bold; }
.emotion-negative { background: #ff0080; color: #fff; }
"""

# ----------------- قالب‌های HTML -----------------
HTML_HOME = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class="secret-star" onclick="window.location.href='/login'" title="ورود مدیران">★</div>
<div class='glass-container'>
<h1>OMNI-PLATFORM</h1>
<p style="margin-bottom: 20px;">به دنیای آینده خوش آمدید.</p>
<a href='/feedback' style="background: rgba(0,255,204,0.2); padding: 15px; border-radius: 15px; border: 1px solid #00ffcc;">آینه احساسی</a>
<a href='/time-capsule'>تالار جاودانگی</a>
<a href='/memory-portal'>پورتال خاطرات</a>
<a href='/register'>ثبت‌نام کسب‌وکار</a>
</div>
</body></html>
"""

HTML_FEEDBACK = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """
.feedback-box { display: flex; flex-direction: column; gap: 20px; }
.emoji-container { display: flex; justify-content: space-between; margin: 20px 0; }
</style></head><body>
<div class='glass-container'>
<h1>آینه احساسی</h1>
<p>امروز چه احساسی داری؟</p>
<form method='POST' enctype="multipart/form-data" class='feedback-box'>
<div class='emoji-container'>
<button type='button' class='emoji-btn' onclick="selectEmoji(this, '😡')">😡</button>
<button type='button' class='emoji-btn' onclick="selectEmoji(this, '☹️')">☹️</button>
<button type='button' class='emoji-btn' onclick="selectEmoji(this, '😐')">😐</button>
<button type='button' class='emoji-btn' onclick="selectEmoji(this, '🙂')">🙂</button>
<button type='button' class='emoji-btn' onclick="selectEmoji(this, '😍')">😍</button>
</div>
<input type='hidden' name='selected_emoji' id='selected_emoji' value=''>
<p style="font-size:0.9rem; opacity:0.8; text-align:right;">(اختیاری) عکسی از خودت آپلود کن:</p>
<input type='file' name='user_image' accept='image/*' style="background: rgba(255,255,255,0.05); border: 1px dashed #00ffcc; padding: 10px;">
<textarea name='message' placeholder='هر چیزی که در دلت داری بنویس... (مثلاً نگران آینده‌ام)' style='background: rgba(0,0,0,0.3); height: 100px;'></textarea>
<button type='submit' style='background: #00ffcc; font-size: 1.2rem;'>ارسال و دریافت پاسخ از آینده</button>
</form>
<a href='/'>BACK TO HOME</a>
</div>
<script>
function selectEmoji(btn, emoji) {
const btns = document.querySelectorAll('.emoji-btn');
btns.forEach(b => b.classList.remove('selected'));
btn.classList.add('selected');
document.getElementById('selected_emoji').value = emoji;
}
</script>
</body></html>
"""

HTML_CAPSULE = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1 style="text-shadow: 0 0 20px #00ffcc;">تالار جاودانگی</h1>
<p style="color:#00ffcc; margin-bottom: 20px;">عکسی از عزیز از دست رفته‌ات آپلود کن و با او حرف بزن...</p>
<form method='POST' enctype="multipart/form-data">
<input type='text' name='name' placeholder='نام عزیز شما' required style="background: rgba(255,255,255,0.05); border: 1px solid #00ffcc;">
<input type='file' name='user_image' accept='image/*' style="background: rgba(255,255,255,0.05); border: 1px dashed #00ffcc; padding: 10px;">
<textarea name='message' placeholder='سلام... دلم برایت تنگ شده...' required style="background: rgba(255,255,255,0.05); border: 1px solid #00ffcc;"></textarea>
<button type='submit' style="box-shadow: 0 0 20px #00ffcc;">ارسال پیام به جهان دیگر</button>
</form>
<a href='/'>BACK TO HOME</a>
</div>
</body></html>
"""

HTML_PORTAL = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """
.chat-box { max-height: 200px; overflow-y: auto; margin-bottom: 20px; padding: 10px; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;}
.postcard-section { background: rgba(0, 255, 204, 0.1); border: 1px dashed #00ffcc; border-radius: 15px; padding: 15px; margin-top: 20px; }
</style></head><body>
<div class='glass-container'>
<h1>پورتال خاطرات</h1>
<div class="chat-box">
{% for c in chats %}
<div class='msg' style="border-left-color: #ff0080;"><b>YOU:</b> {{ c.user }}</div>
<div class='msg' style="border-left-color: #00ffcc;"><b>AI:</b> {{ c.ai }}</div>
{% endfor %}
</div>
<form method='POST' action='/memory-portal'>
<input type='text' name='message' placeholder='اینجا تایپ کنید...' required style="border: 1px solid #00ffcc;">
<button type='submit' style="box-shadow: 0 0 20px #00ffcc;">SEND</button>
</form>
<div class="postcard-section">
<h3 style="color: #ffcc00;">📸 ساخت کارت پستال</h3>
<form method='POST' action='/make-postcard' enctype="multipart/form-data">
<input type='file' name='postcard_image' accept='image/*' required style="background: rgba(255,255,255,0.05); border: 1px solid #ffcc00;">
<button type='submit' style="background: #ffcc00; color: #000;">ساخت کارت پستال</button>
</form>
</div>
<a href='/'>BACK TO HOME</a>
</div>
</body></html>
"""

HTML_LOGIN = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>ورود مدیران</h1>
<form method='POST'>
<input type='text' name='username' placeholder='USERNAME' required>
<input type='password' name='password' placeholder='PASSWORD' required>
<button type='submit'>ACCESS</button>
</form>
<a href='/register'>ثبت‌نام کسب‌وکار جدید</a>
</div>
</body></html>
"""

HTML_REGISTER = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>ثبت کسب‌وکار</h1>
<form method='POST'>
<input type='text' name='name' placeholder='نام مجموعه' required>
<input type='text' name='username' placeholder='USERNAME' required>
<input type='password' name='password' placeholder='PASSWORD' required>
<button type='submit'>INIT</button>
</form>
<a href='/login'>ورود</a>
</div>
</body></html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1 style='text-align:center;'>پنل مدیریت {{ name }}</h1>
<div class='qr-section'>
<h3>📱 QR کد اختصاصی کسب‌وکار شما</h3>
<button onclick="generateQR('{{ code }}')" style='background: #00ffcc; color: #000; padding: 10px 20px; font-weight: bold;'>تولید QR Code</button>
<br>
<img id="qr-img" class='qr-image' src="" alt="QR Code">
</div>
<h3>آخرین نظرات مشتریان:</h3>
<div style='max-height: 300px; overflow-y: auto;'>
{% for f in feedbacks %}
<div class='feedback-card'>
<span class='emotion-tag {% if "نارضایتی" in f.emotion %}emotion-negative{% endif %}'>{{ f.emotion }}</span>
<p style='margin-top:10px;'>{{ f.message }}</p>
</div>
{% endfor %}
</div>
<a href='/logout' style='color:#ff0080;'>خروج از سیستم</a>
</div>
<script>
function generateQR(bizCode) {
const link = `https://my-site-app-nyc3.onrender.com/feedback?biz=${bizCode}`;
const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(link)}`;
const img = document.getElementById('qr-img');
img.src = qrApiUrl;
img.style.display = 'inline-block';
}
</script>
</body></html>
"""

# ----------------- مسیرهای Flask -----------------
@app.route('/')
def index():
    return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_b = Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], unique_code=code)
        db.session.add(new_b)
        db.session.commit()
        return f"<h1 style='color:#00ffcc; text-align:center; margin-top:50px;'>ثبت‌نام موفق! کد: {code}</h1><a href='/login' style='display:block; text-align:center; color:white;'>ورود</a>"
    return HTML_REGISTER

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Business.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        return "<h1 style='color:red; text-align:center;'>رمز اشتباه است.</h1>"
    return HTML_LOGIN

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template_string(HTML_DASHBOARD, name=current_user.name, code=current_user.unique_code, feedbacks=feedbacks)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        selected_emoji = request.form.get('selected_emoji', '')
        message = request.form.get('message', '')
        
        if selected_emoji and not message:
            message = f"مشتری با ایموجی {selected_emoji} پاسخ داد."

        if message:
            emotion = analyze_emotion(message)
            if selected_emoji:
                if selected_emoji in ['😡', '☹️']: emotion = 'نارضایتی 😢'
                elif selected_emoji in ['😍', '🙂']: emotion = 'رضایت 😊'
            
            is_business = request.args.get('biz') == '1'
            new_f = Feedback(message=message, emotion=emotion, is_business=is_business)
            db.session.add(new_f)
            db.session.commit()
            
            image_html = ""
            if 'user_image' in request.files:
                file = request.files['user_image']
                if file and file.filename != '':
                    img_data = base64.b64encode(file.read()).decode('utf-8')
                    image_html = f"<img src='data:image/jpeg;base64,{img_data}' class='future-image'>"
            
            if is_business:
                if 'نارضایتی' in emotion:
                    response = f"<h2 style='color:#ff0080;'>متاسفیم!</h2><p>کد تخفیف: <b>OMNI50</b></p>"
                else:
                    response = f"<h2 style='color:#00ffcc;'>ممنون!</h2>"
            else:
                ai_response = aura_brain(message, "نسخه ۲۰ سال بعد شما", is_business)
                response = f"""
                <video autoplay loop muted class='bg-video'><source src='https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4' type='video/mp4'></video>
                {image_html}
                <div class='msg'><b>پیام از آینده:</b><br><span class='typing-effect'>{ai_response}</span></div>
                """

            return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body><div class='glass-container'>{response}<a href='/'>بازگشت</a></div></body></html>"

    return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
    if request.method == 'POST':
        name = request.form.get('name', 'عزیز از دست رفته')
        message = request.form.get('message', '')
        
        image_html = ""
        if 'user_image' in request.files:
            file = request.files['user_image']
            if file and file.filename != '':
                img_data = base64.b64encode(file.read()).decode('utf-8')
                image_html = f"<img src='data:image/jpeg;base64,{img_data}' class='future-image'>"
        
        if message:
            ai_response = aura_brain(message, name, False)
            return f"""
            <html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head>
            <body>
            <video autoplay loop muted class='bg-video'><source src='https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4' type='video/mp4'></video>
            <div class='glass-container' style='max-width: 750px;'>
            <h1 style='color:#00ffcc;'>ارتباط برقرار شد</h1>
            {image_html}
            <div class='msg'><b>شما:</b> {message}</div>
            <div class='msg' style='background: rgba(255,204,0,0.1);'><b>{name}:</b><br><br><span class='typing-effect'>{ai_response}</span></div>
            <a href='/'>بازگشت</a>
            </div>
            </body></html>
            """
    return HTML_CAPSULE

@app.route('/memory-portal', methods=['GET', 'POST'])
def memory_portal():
    if request.method == 'POST':
        if 'chats' not in session:
            session['chats'] = []
        
        message = request.form.get('message', '')
        ai_response = aura_brain(message, "دوست قدیمی", False)

        session['chats'].append({'user': message, 'ai': ai_response})
        session.modified = True
        return redirect(url_for('memory_portal'))
    
    return render_template_string(HTML_PORTAL, chats=session.get('chats', []))

@app.route('/make-postcard', methods=['POST'])
def make_postcard():
    if 'postcard_image' in request.files:
        file = request.files['postcard_image']
        if file and file.filename != '':
            img_data = base64.b64encode(file.read()).decode('utf-8')
            return f"""
            <html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}
            .postcard-frame {{ background: #fff; padding: 15px; border-radius: 10px; box-shadow: 0 20px 50px rgba(0,0,0,0.8); display: inline-block; }}
            </style></head>
            <body style="background: #000; display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div class='glass-container'>
            <h2 style="color:#00ffcc;">کارت پستال شما آماده شد!</h2>
            <div class='postcard-frame'>
            <img src='data:image/jpeg;base64,{img_data}' style="max-width: 300px; border-radius: 5px;">
            <h3 style="color: #000; margin-top: 10px;">OMNI-PLATFORM</h3>
            </div>
            <a href='/memory-portal' style="color:#00ffcc;">بازگشت</a>
            </div>
            </body></html>
            """
    return redirect(url_for('memory_portal'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
