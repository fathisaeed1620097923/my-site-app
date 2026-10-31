
import os
import random
import string
import base64
from datetime import date
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'future-500-years')

# تنظیمات دیتابیس رندر
db_url = 'postgresql://myuser:5VAUU122WDEqj8UepCJypXIpdA8Vl8ip@dpg-dbi7boui0phs73d2ime0-a.oregon-postgres.render.com/mydb_ecw3'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

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

class TimeCapsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id): return Business.query.get(int(user_id))

def analyze_emotion(text):
    text = text.lower()
    if any(w in text for w in ['خوشحال', 'عالی', 'شاد', 'خوب', 'رضایت', 'معرکه']): return 'رضایت 😊'
    if any(w in text for w in ['غمگین', 'خسته', 'بد', 'ناراضی', 'عصبانی', 'افتضاح']): return 'ناراضی 😢'
    return 'خنثی 😐'

def aura_brain(user_input):
    text = user_input.lower()
    if "خسته" in text: return "من اینجا هستم تا کمکت کنم. انرژی را از من بگیر."
    if "خوشحال" in text: return "شادی تو عالیه! این فرکانس را بالا نگه دار."
    return "من به تو گوش می‌دهم. بگو..."

# ----------------- CSS -----------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background: radial-gradient(circle at center, #1a2a6c, #0d0d2b, #000); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; overflow-x: hidden; perspective: 1000px; color: #fff; transition: background 1s ease; }
.glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.2); padding: 40px; width: 100%; max-width: 600px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; z-index: 10; transition: transform 0.1s ease-out; transform-style: preserve-3d; position: relative; overflow: hidden; }
h1 { font-size: 2.5rem; margin-bottom: 20px; transform: translateZ(50px); text-shadow: 0 0 20px #00ffcc; }
input, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; font-family: 'Vazirmatn', Tahoma; outline: none; transform: translateZ(30px); background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); transition: 0.3s; }
input:focus, textarea:focus { border-color: #00ffcc; box-shadow: 0 0 15px rgba(0,255,204,0.3); }
button { cursor: pointer; font-weight: bold; border-radius: 30px; background: #00ffcc; color: #000; }
button:hover { transform: scale(1.05); box-shadow: 0 0 20px #00ffcc; }
a { text-decoration: none; display: block; margin-top: 15px; font-size: 1.1rem; transform: translateZ(20px); color: #00ffcc; text-shadow: 0 0 10px #00ffcc; transition: 0.3s; }
a:hover { color: #fff; text-shadow: 0 0 20px #fff; }
.msg { padding: 15px; margin-top: 15px; border-radius: 10px; text-align: right; background: rgba(255,255,255,0.05); border-left: 4px solid #00ffcc; }

/* افکت تایپ */
.typing-effect { overflow: hidden; border-right: .15em solid #00ffcc; white-space: nowrap; letter-spacing: .05em; animation: typing 4s steps(60, end); color: #00ffcc; font-size: 1.1rem; display: inline-block; }
@keyframes typing { from { width: 0 } to { width: 100% } }

/* افکت گلیچ (لرزش) */
.glitch-active { animation: glitch-anim 0.5s cubic-bezier(.25, .46, .45, .94) both infinite; }
@keyframes glitch-anim {
0% { transform: translate(0); }
20% { transform: translate(-5px, 5px); }
40% { transform: translate(-5px, -5px); }
60% { transform: translate(5px, 5px); }
80% { transform: translate(5px, -5px); }
100% { transform: translate(0); }
}

/* افکت ترک خوردن شیشه */
.cracked::before {
content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
background-image: url('https://www.transparenttextures.com/patterns/cracks.png');
opacity: 0.4; pointer-events: none; mix-blend-mode: screen; z-index: 20;
animation: crack-appear 0.3s ease-out;
}
@keyframes crack-appear { from { opacity: 0; transform: scale(1.1); } to { opacity: 0.4; transform: scale(1); } }

/* پوسته‌های زنده */
.angel-theme { background: radial-gradient(circle at center, #003366, #001a33, #000) !important; }
.zombie-theme { background: radial-gradient(circle at center, #4a0000, #1a0000, #000) !important; }

/* استایل عکس پیری */
.future-image { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin: 15px auto; border: 3px solid #00ffcc; box-shadow: 0 0 30px #00ffcc; filter: grayscale(100%) sepia(30%) blur(1px); transition: 0.5s; }
"""

# ----------------- JS -----------------
JS = """
document.addEventListener('mousemove', (e) => {
const galaxy = document.querySelector('.galaxy');
if (galaxy) {
const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
galaxy.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
}
});
function toggleMenu() {
const universe = document.querySelector('.universe');
if (universe) universe.classList.toggle('open');
}

// رویداد تصادفی سیاره هدیه
function spawnGift() {
const gift = document.createElement('div');
gift.style.cssText = "position:fixed; bottom:20px; left:20px; width:60px; height:60px; background:gold; border-radius:50%; box-shadow:0 0 30px gold; cursor:pointer; z-index:9999; display:flex; align-items:center; justify-content:center; font-size:30px; animation:pulse 1s infinite;";
gift.innerHTML = "🎁";
gift.onclick = function() { alert("شما ۵۰ سکه کوانتومی جایزه گرفتید! 🌌"); this.remove(); };
document.body.appendChild(gift);
setTimeout(() => { if(gift.parentNode) gift.remove(); }, 10000);
}
setInterval(() => {
if (Math.random() > 0.7 && document.querySelector('.galaxy')) spawnGift();
}, 120000);
"""

# ----------------- قالب‌های HTML -----------------

# صفحه اصلی (کهکشان با صدا)
HTML_HOME = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>
""" + CSS + """
body { background: radial-gradient(circle at center, #0b0b2a, #000); overflow: hidden; }
.galaxy { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; transition: transform 0.1s ease-out; transform-style: preserve-3d; }
.core-sun { width: 150px; height: 150px; background: radial-gradient(circle at 30% 30%, #ffcc00, #ff6600, #cc0000); border-radius: 50%; box-shadow: 0 0 60px #ff6600, 0 0 100px #ff3300; cursor: pointer; position: absolute; z-index: 10; transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: translateZ(50px); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 60px #ff6600, 0 0 100px #ff3300; } 50% { box-shadow: 0 0 80px #ffaa00, 0 0 150px #ff6600; } 100% { box-shadow: 0 0 60px #ff6600, 0 0 100px #ff3300; } }
.core-sun:hover { transform: scale(1.1) translateZ(60px); }
.universe { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
.planet { position: absolute; border-radius: 50%; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: center; align-items: center; text-align: center; color: #00ffcc; text-decoration: none; font-weight: bold; font-size: 14px; opacity: 0; transform: scale(0); transition: all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: inset 0 0 20px rgba(0,255,204,0.2), 0 0 20px rgba(0,255,204,0.1); z-index: 5; padding: 10px; }
.universe.open .planet { opacity: 1; transform: scale(1); }
.p-login { width: 120px; height: 120px; background: radial-gradient(circle at 30% 30%, #4a90e2, #003366); box-shadow: 0 0 30px #4a90e2; }
.universe.open .p-login { transform: translate(-180px, -100px) scale(1); }
.p-feedback { width: 100px; height: 100px; background: radial-gradient(circle at 30% 30%, #e94e77, #660022); box-shadow: 0 0 30px #e94e77; color: #fff; }
.universe.open .p-feedback { transform: translate(150px, -120px) scale(1); }
.p-time { width: 90px; height: 90px; background: radial-gradient(circle at 30% 30%, #a8e6cf, #1b5e20); box-shadow: 0 0 30px #a8e6cf; color: #000; }
.universe.open .p-time { transform: translate(-100px, 150px) scale(1); }
.p-portal { width: 110px; height: 110px; background: radial-gradient(circle at 30% 30%, #8e44ad, #2c003e); box-shadow: 0 0 30px #8e44ad; }
.universe.open .p-portal { transform: translate(120px, 130px) scale(1); }
.planet { animation: float 4s ease-in-out infinite; }
@keyframes float { 0% { margin-top: 0px; } 50% { margin-top: -15px; } 100% { margin-top: 0px; } }
</style></head><body>
<!-- صدای کهکشان -->
<audio autoplay loop style="display:none;"><source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3" type="audio/mpeg"></audio>
<div class='galaxy'><div class='universe'>
<div class='core-sun' onclick='toggleMenu()'></div>
<a href='/login' class='planet p-login'>ورود<br>کسب‌وکارها</a>
<a href='/feedback' class='planet p-feedback'>آینه<br>احساسی</a>
<a href='/time-capsule' class='planet p-time'>کپسول<br>زمان</a>
<a href='/memory-portal' class='planet p-portal'>پورتال<br>خاطرات</a>
</div></div>
<script>""" + JS + """</script></body></html>
"""

# آینه احساسی (با قابلیت آپلود عکس)
HTML_FEEDBACK = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>آینه احساسی</h1>
<p>امروز چه احساسی داری؟ (نصیحتی از ۲۰ سال بعدِ خودت دریافت کن)</p>
<form method='POST' enctype="multipart/form-data">
<textarea name='message' placeholder='امروز چه احساسی داری؟' required></textarea>
<p style="font-size:0.9rem; opacity:0.8; text-align:right;">(اختیاری) عکسی از خودت آپلود کن تا چهره‌ات را در آینده ببینی:</p>
<input type='file' name='user_image' accept='image/*' style="background:transparent; border:none; padding:0;">
<button type='submit'>ارتباط با آینده</button>
</form>
<a href='/'>BACK</a>
</div>
<script>""" + JS + """</script></body></html>
"""

# ورود و ثبت‌نام
HTML_LOGIN = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>AUTHENTICATION</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS</button></form><a href='/register'>REGISTER</a><a href='/'>BACK TO GALAXY</a></div><script>" + JS + "</script></body></html>"
HTML_REGISTER = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>NEW PROTOCOL</h1><form method='POST'><input type='text' name='name' placeholder='HOTEL/CAFE NAME' required><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INIT</button></form><a href='/login'>ALREADY REGISTERED?</a></div><script>" + JS + "</script></body></html>"

# داشبورد (پنل هتل‌دار)
HTML_DASHBOARD = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>
""" + CSS + """
.dashboard-box { width: 100%; max-width: 800px; text-align: right; }
.feedback-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; margin-bottom: 15px; box-shadow: inset 0 0 10px rgba(0,255,204,0.1); }
.emotion-tag { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; margin-right: 10px; background: #00ffcc; color: #000; font-weight: bold; }
.emotion-negative { background: #ff0080; color: #fff; }
.radar { width: 100px; height: 100px; border-radius: 50%; border: 2px solid #00ffcc; margin: 0 auto 20px auto; position: relative; overflow: hidden; box-shadow: 0 0 20px #00ffcc; }
.radar::after { content: ''; position: absolute; top: 50%; left: 50%; width: 50%; height: 2px; background: #00ffcc; transform-origin: left center; animation: spin 2s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style></head><body>
<div class='glass-container dashboard-box'>
<h1 style='text-align:center;'>پنل مدیریت کوانتومی</h1>
<div class='radar'></div>
<div style='display:flex; justify-content:space-between; margin-bottom: 20px;'>
<div>لِوِل شما: <b style='color:#00ffcc;'>{{ level }}</b></div>
<div>سکه‌های شما: <b style='color:#ffcc00;'>{{ points }}</b></div>
<div>کد یکتای شما: <b style='color:#fff;'>{{ code }}</b></div>
</div>
<h3>آخرین سیگنال‌های احساسی مشتریان شما:</h3>
<div style='max-height: 400px; overflow-y: auto; padding-left: 10px;'>
{% for f in feedbacks %}
<div class='feedback-card'>
<span class='emotion-tag {% if "ناراضی" in f.emotion %}emotion-negative{% endif %}'>{{ f.emotion }}</span>
<p style='margin-top:10px; color:#ddd;'>{{ f.message }}</p>
</div>
{% else %}
<p>هنوز هیچ سیگنالی از مشتریان دریافت نشده است.</p>
{% endfor %}
</div>
<div style='text-align:center; margin-top:20px;'>
<a href='/logout' style='color:#ff0080;'>خروج از سیستم</a>
<a href='/' style='color:#00ffcc;'>بازگشت به کهکشان</a>
</div>
</div>
<script>""" + JS + """</script></body></html>
"""

# کپسول زمان
HTML_CAPSULE = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>TIME CAPSULE</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><textarea name='message' placeholder='MESSAGE' required></textarea><input type='date' name='date' required><button type='submit'>LOCK</button></form>{% for c in capsules %}<div class='msg'>{{ c.name }}: {{ c.message }}</div>{% endfor %}<a href='/'>BACK</a></div><script>" + JS + "</script></body></html>"

# پورتال خاطرات
HTML_PORTAL = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "body { background: radial-gradient(circle at center, #2b1055, #7597de); }</style></head><body><audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' type='audio/mpeg'></audio><div class='glass-container'><h1>پورتال خاطرات</h1><p style='color:#fff; opacity:0.8;'>صدای محیط را حس کنید...</p>{% for c in chats %}<div class='msg'>YOU: {{ c.user }}<br>AI: {{ c.ai }}</div>{% endfor %}<form method='POST'><input type='text' name='message' placeholder='TALK...' required><button type='submit'>SEND</button></form><a href='/'>BACK</a></div><script>" + JS + "</script></body></html>"


# ----------------- مسیرهای Flask -----------------

@app.route('/')
def index(): return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_business = Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], unique_code=code)
        db.session.add(new_business)
        db.session.commit()
        return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body><div class='glass-container'><h1>YOUR CODE: {code}</h1><p>این کد یکتای پنل شماست. آن را حفظ کنید.</p><a href='/login'>رفتن به صفحه ورود</a></div></body></html>"
    return HTML_REGISTER

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Business.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        return "<html><body style='background:#000; color:red; text-align:center; padding:50px;'><h1>ACCESS DENIED.</h1><a href='/login' style='color:#fff;'>Try Again</a></body></html>"
    return HTML_LOGIN

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    if current_user.last_login != today:
        current_user.points += 20
        current_user.last_login = today
        db.session.commit()
    current_user.level = (current_user.points // 100) + 1
    db.session.commit()
    return render_template_string(HTML_DASHBOARD, code=current_user.unique_code, feedbacks=Feedback.query.order_by(Feedback.id.desc()).all(), points=current_user.points, level=current_user.level)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form['message']
        emotion = analyze_emotion(message)

        new_feedback = Feedback(message=message, emotion=emotion)
        db.session.add(new_feedback)
        if current_user.is_authenticated: current_user.points += 10
        db.session.commit()

        advice = ""
        video_url = ""
        theme_class = "angel-theme" if 'رضایت' in emotion else "zombie-theme" if 'ناراضی' in emotion else ""
        glitch_class = "glitch-active" if 'ناراضی' in emotion else ""
        cracked_class = "cracked" if 'ناراضی' in emotion else ""

        if 'رضایت' in emotion:
            video_url = "https://assets.mixkit.co/videos/preview/mixkit-happy-woman-dancing-in-a-field-of-flowers-1240-large.mp4"
            advice = "من ۲۰ سال بعدِ تو هستم. می‌بینم که امروز چقدر شادی. این لحظه را در قلبِ کوانتومی‌ات حفظ کن. این انرژی مثبت، سوختِ موشکِ مسیرِ من بود."
        elif 'ناراضی' in emotion:
            video_url = "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-on-a-window-1088-large.mp4"
            advice = "من ۲۰ سال بعدِ تو هستم. می‌دانم الان چقدر سخت است. اما به گذشته نگاه می‌کنم و می‌بینم این تاریکی فقط یک ابر زودگذر بود. نفس بکش. من از این سد عبور کردم، تو هم می‌توانی."
        else:
            video_url = "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4"
            advice = "من ۲۰ سال بعدِ تو هستم. مسیر تو در حال شکل‌گیری است. از این سکون استفاده کن تا ستاره بعدی‌ات را پیدا کنی."

# پردازش عکس کاربر (در صورت آپلود)
        image_html = ""
        if 'user_image' in request.files:
            file = request.files['user_image']
            if file and file.filename != '':
# تبدیل عکس به base64 برای نمایش بدون ذخیره در سرور
                img_data = base64.b64encode(file.read()).decode('utf-8')
                image_html = f"<img src='data:image/jpeg;base64,{img_data}' class='future-image' alt='نسخه آینده شما'>"

        return f"""
        <html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>
        {CSS}    
        .video-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -1; opacity: 0.3; }}
        </style></head>
        <body class='{theme_class} {glitch_class} {cracked_class}'>
            <video autoplay loop muted class='video-bg'><source src='{video_url}' type='video/mp4'></video>
            <div class='glass-container' style='max-width: 750px;'>
                <h1 style='color:#00ffcc; text-shadow: 0 0 10px #00ffcc;'>پیوند با آینده برقرار شد</h1>
                {image_html}
                <div class='msg' style='border-left-color: #00ffcc;'><b>شما:</b> {message}</div>
                <div class='msg' style='border-left-color: #ff0080;'><b>احساس شناسایی شده:</b> {emotion}</div>
                <div class='msg' style='border-left-color: #fff; background: rgba(0,255,204,0.1); line-height: 1.8;'>
                    <b style='color:#fff;'>نصیحت از نسخه ۲۰ سال بعدِ شما:</b><br><br>
                    <span class='typing-effect'>{advice}</span>
                </div>
                <a href='/'>بازگشت به کهکشان</a>
                <a href='/feedback' style='color:#ffcc00;'>ارسال سیگنال جدید</a>
            </div>
            <script>{JS}</script>
        </body></html>
        """
    return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        date_val = request.form['date']

        new_capsule = TimeCapsule(name=name, message=message, date=date_val)
        db.session.add(new_capsule)
        if current_user.is_authenticated: current_user.points += 10
        db.session.commit()

        future_prediction = f"""
        <div class='msg' style='border-color: #00ffcc;'>
            <h3>🌌 پیش‌بینی آینده برای پیام شما:</h3>
            <p>پیام شما در تاریخ <b>{date_val}</b> به یک اثر باستانی دیجیتال تبدیل شده است.</p>
            <p>شانس زنده ماندن در شبکه کوانتومی: <b style='color:#00ffcc;'>۹۹.۸٪</b></p>
        </div>
        """
        return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body><div class='glass-container'><h1>ثبت شد!</h1>{future_prediction}<a href='/'>بازگشت</a></div><script>{JS}</script></body></html>"

    capsules_list = TimeCapsule.query.all()
    return render_template_string(HTML_CAPSULE, capsules=capsules_list)

@app.route('/memory-portal', methods=['GET', 'POST'])
def memory_portal():
    if request.method == 'POST':
        if 'chats' not in session: session['chats'] = []
  session['chats'].append({'user': request.form['message'], 'ai': aura_brain(request.form['message'])})
        session.modified = True
        if current_user.is_authenticated:
            current_user.points += 5
            db.session.commit()
        return redirect(url_for('memory_portal'))
    return render_template_string(HTML_PORTAL, chats=session.get('chats', []))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
