import os
import random
import string
import base64
from datetime import date, datetime, timedelta
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'future-500-years'

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
    business_type = db.Column(db.String(50), default='کسب‌وکار')
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
    image_data = db.Column(db.Text, nullable=True)

class TimeCapsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Business.query.get(int(user_id))

def analyze_emotion(text):
    text = text.lower()
        if any(w in text for w in ['خوشحال', 'عالی', 'شاد', 'خوب', 'رضایت']):
        return 'رضایت 😊'
        if any(w in text for w in ['غمگین', 'خسته', 'بد', 'ناراضی', 'عصبی', 'پیر', 'ترس']):
        return 'نارضایتی 😢'
    return 'خنثی 😐'

def aura_brain(user_input):
    text = user_input.lower()
        if "خسته" in text:
        return "من اینجا هستم تا کمکت کنم. انرژی را از من بگیر."
    if "خوشحال" in text:
        return "شادی تو عالیه! این فرکانس را بالا نگه دار."
    return "من به تو گوش می‌دهم. بگو..."

# ----------------- CSS سینمایی -----------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background: #000; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #fff; overflow-x: hidden; perspective: 1000px; }
.glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.2); padding: 40px; width: 100%; max-width: 600px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; z-index: 10; position: relative; overflow: hidden; transition: transform 0.1s ease-out; transform-style: preserve-3d; }
h1 { font-size: 2.5rem; margin-bottom: 20px; text-shadow: 0 0 20px #00ffcc; }
input, select, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; font-family: 'Vazirmatn', Tahoma; outline: none; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); }
button { cursor: pointer; font-weight: bold; background: #00ffcc; color: #000; transition: 0.3s; border-radius: 30px; }
button:hover { transform: scale(1.05); box-shadow: 0 0 20px #00ffcc; }
a { text-decoration: none; display: block; margin-top: 15px; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; transition: 0.3s; }
a:hover { color: #fff; }
.msg { padding: 15px; margin-top: 15px; border-radius: 10px; text-align: right; background: rgba(255,255,255,0.05); border-left: 4px solid #00ffcc; }
.secret-star { position: fixed; top: 20px; left: 20px; font-size: 30px; color: gold; cursor: pointer; z-index: 100; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
.glitch-active { animation: glitch-anim 0.5s cubic-bezier(.25, .46, .45, .94) both infinite; }
@keyframes glitch-anim { 0% { transform: translate(0); } 20% { transform: translate(-5px, 5px); } 40% { transform: translate(-5px, -5px); } 60% { transform: translate(5px, 5px); } 80% { transform: translate(5px, -5px); } 100% { transform: translate(0); } }
.cracked::before { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('https://www.transparenttextures.com/patterns/cracks.png'); opacity: 0.4; pointer-events: none; mix-blend-mode: screen; z-index: 20; animation: crack-appear 0.3s ease-out; }
@keyframes crack-appear { from { opacity: 0; transform: scale(1.1); } to { opacity: 0.4; transform: scale(1); } }
.angel-theme { background: radial-gradient(circle at center, #003366, #001a33, #000) !important; }
.zombie-theme { background: radial-gradient(circle at center, #4a0000, #1a0000, #000) !important; }
.heart-container { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: -1; opacity: 0.2; }
.heart { width: 80px; height: 80px; background-color: #ff0055; position: relative; transform: rotate(-45deg); animation: beat 1s infinite alternate; box-shadow: 0 0 50px #ff0055; }
.heart::before, .heart::after { content: ""; width: 80px; height: 80px; background-color: #ff0055; border-radius: 50%; position: absolute; }
.heart::before { top: -40px; left: 0; } .heart::after { top: 0; left: 40px; }
@keyframes beat { 0% { transform: rotate(-45deg) scale(1); } 100% { transform: rotate(-45deg) scale(1.1); } }
.typing-effect { overflow: hidden; border-right: .15em solid #00ffcc; white-space: nowrap; letter-spacing: .05em; animation: typing 3s steps(40, end); color: #00ffcc; font-size: 1.1rem; display: inline-block; }
@keyframes typing { from { width: 0 } to { width: 100% } }
.future-image { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin: 15px auto; border: 3px solid #00ffcc; box-shadow: 0 0 30px #00ffcc; filter: grayscale(100%) sepia(30%) blur(1px); transition: 0.5s; }
#canvas-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
.overlay { position: relative; z-index: 10; pointer-events: none; width: 100%; height: 100vh; display: flex; justify-content: center; align-items: center; }
.planet-menu { pointer-events: auto; display: flex; flex-direction: column; gap: 20px; text-align: center; background: rgba(0,0,0,0.6); padding: 30px; border-radius: 20px; border: 1px solid #00ffcc; box-shadow: 0 0 30px #00ffcc; }
"""

# ----------------- JS سینمایی -----------------
JS = """
function spawnGift() {
const gift = document.createElement('div');
gift.style.cssText = "position:fixed; bottom:20px; left:20px; width:60px; height:60px; background:gold; border-radius:50%; box-shadow:0 0 30px gold; cursor:pointer; z-index:9999; display:flex; align-items:center; justify-content:center; font-size:30px; animation:pulse 1s infinite;";
gift.innerHTML = "🎁";
gift.onclick = function() { alert("شما ۵۰ سکه کوانتومی جایزه گرفتید! 🌌"); this.remove(); };
document.body.appendChild(gift);
setTimeout(() => { if(gift.parentNode) gift.remove(); }, 10000);
}
setInterval(() => {
if (Math.random() > 0.7) spawnGift();
}, 60000);
"""

# ----------------- قالب‌های HTML -----------------
HTML_HOME = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head><body>
<div class="secret-star" onclick="window.location.href='/login'" title="ورود مدیران">★</div>
<div class="heart-container"><div class="heart"></div></div>
<div id="canvas-container"></div>
<div class="overlay">
<div class="planet-menu">
<h1>OMNI-PLATFORM</h1>
<a href='/feedback' style="background: rgba(0,255,204,0.2); padding: 15px; border-radius: 15px; border: 1px solid #00ffcc;">آینه احساسی (مشاوره آینده)</a>
<a href='/time-capsule'>تالار جاودانگی</a>
<a href='/memory-portal'>پورتال خاطرات</a>
<a href='/register'>ثبت‌نام کسب‌وکار</a>
</div>
</div>
<script>
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

const starsGeometry = new THREE.BufferGeometry();
const starsCount = 5000;
const positions = new Float32Array(starsCount * 3);
for (let i = 0; i < starsCount * 3; i++) {
positions[i] = (Math.random() - 0.5) * 2000;
}
starsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const starsMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.7 });
const stars = new THREE.Points(starsGeometry, starsMaterial);
scene.add(stars);

const sunGeometry = new THREE.SphereGeometry(5, 32, 32);
const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
const sun = new THREE.Mesh(sunGeometry, sunMaterial);
scene.add(sun);

let mouseX = 0; let mouseY = 0;
document.addEventListener('mousemove', (event) => {
mouseX = (event.clientX - window.innerWidth / 2) * 0.001;
mouseY = (event.clientY - window.innerHeight / 2) * 0.001;
});

camera.position.z = 20;

function animate() {
requestAnimationFrame(animate);
stars.rotation.y += 0.0005;
camera.position.x += (mouseX * 10 - camera.position.x) * 0.05;
camera.position.y += (-mouseY * 10 - camera.position.y) * 0.05;
camera.lookAt(scene.position);
renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
camera.aspect = window.innerWidth / window.innerHeight;
camera.updateProjectionMatrix();
renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
<script>""" + JS + """</script>
</body></html>
"""

HTML_FEEDBACK = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>آینه احساسی</h1>
<form method='POST' enctype="multipart/form-data">
<textarea name='message' placeholder='امروز چه احساسی داری؟' required></textarea>
<p style="font-size:0.9rem; opacity:0.8; text-align:right;">(اختیاری) عکسی از خودت آپلود کن:</p>
<input type='file' name='user_image' accept='image/*' style="background:transparent; border:none; padding:0;">
<button type='submit'>تحلیل و دریافت مشاوره</button>
</form>
<a href='/'>BACK</a>
</div>
<script>""" + JS + """</script></body></html>
"""

HTML_CAPSULE = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>تالار جاودانگی</h1>
<p>پیامی برای عزیزی که در کنار ما نیست بنویسید...</p>
<form method='POST'>
<input type='text' name='name' placeholder='نام عزیز شما' required>
<textarea name='message' placeholder='سلام... دلم برایت تنگ شده...' required></textarea>
<button type='submit'>ارسال پیام</button>
</form>
<a href='/'>BACK</a>
</div>
<script>""" + JS + """</script></body></html>
"""

HTML_PORTAL = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """body { background: radial-gradient(circle at center, #2b1055, #7597de); }</style></head><body>
<audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' type='audio/mpeg'></audio>
<div class='glass-container'><h1>پورتال خاطرات</h1><p style='color:#fff; opacity:0.8;'>صدای محیط را حس کنید...</p>
{% for c in chats %}<div class='msg'>YOU: {{ c.user }}<br>AI: {{ c.ai }}</div>{% endfor %}
<form method='POST' enctype="multipart/form-data">
<input type='text' name='message' placeholder='TALK...' required>
<p style="font-size:0.9rem; opacity:0.8; text-align:right;">عکس خودت یا دسته‌جمعی آپلود کن تا کارت پستال بسازی:</p>
<input type='file' name='user_image' accept='image/*' style="background:transparent; border:none; padding:0;">
<button type='submit'>SEND & MAKE POSTCARD</button>
</form>
<a href='/'>BACK</a></div>
<script>""" + JS + """</script></body></html>
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
<script>""" + JS + """</script></body></html>
"""

HTML_REGISTER = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>ثبت کسب‌وکار</h1>
<form method='POST'>
<input type='text' name='name' placeholder='نام مجموعه (کافه، بانک...)' required>
<input type='text' name='username' placeholder='USERNAME' required>
<input type='password' name='password' placeholder='PASSWORD' required>
<button type='submit'>INIT</button>
</form>
<a href='/login'>ورود</a>
</div>
<script>""" + JS + """</script></body></html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='glass-container'>
<h1>پنل مدیریت {{ name }}</h1>
<p>کد ادمین شما: <b style='color:gold;'>{{ code }}</b></p>
<h3>نظرات مشتریان:</h3>
<div style='max-height: 300px; overflow-y: auto; text-align:right;'>
{% for f in feedbacks %}
<div class='msg' style='border-left-color: {% if "نارضایتی" in f.emotion %}#ff0080{% else %}#00ffcc{% endif %};'>
<b>{{ f.emotion }}</b> | وضعیت: {{ f.status }}<br>{{ f.message }}
{% if f.image_data %}
<br><img src='data:image/jpeg;base64,{{ f.image_data }}' style='width: 100px; border-radius: 10px; margin-top: 10px;'>
{% endif %}
{% if not f.resolved %}<br><a href='/resolve/{{ f.id }}' style='color:gold; font-size:12px;'>علامت‌گذاری حل شد</a>{% endif %}
</div>
{% endfor %}
</div>
<a href='/logout'>خروج</a>
</div>
<script>""" + JS + """</script></body></html>
"""

# ----------------- مسیرهای Flask -----------------

@app.route('/')
def index():
    return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_b = Business(
        username=request.form['username'],
        password=generate_password_hash(request.form['password']),
        name=request.form['name'],
        unique_code=code
        )
        db.session.add(new_b)
        db.session.commit()
        return f"<h1 style='color:#00ffcc; text-align:center; margin-top:50px;'>ثبت‌نام موفق! کد ادمین شما: {code}</h1><a href='/login' style='display:block; text-align:center; color:white;'>ورود</a>"
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
    today = date.today()
    if current_user.last_login != today:
        current_user.points += 20
        current_user.last_login = today
        db.session.commit()
    
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    unresolved = Feedback.query.filter_by(resolved=False, is_business=True).all()
    for f in unresolved:
        if f.created_at < one_week_ago:
            if f.status == 'سطح ۱':
                f.status = 'سطح ۲'
            elif f.status == 'سطح ۲':
                f.status = 'سطح ۳ (مدیر)'
            db.session.commit()
    
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template_string(HTML_DASHBOARD, name=current_user.name, code=current_user.unique_code, feedbacks=feedbacks)

@app.route('/resolve/<int:id>')
@login_required
def resolve(id):
    f = Feedback.query.get_or_404(id)
    f.resolved = True
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form.get('message', '')
        if message:
            emotion = analyze_emotion(message)
            is_business = request.args.get('biz') == '1'
            
            image_data = None
            if 'user_image' in request.files:
                file = request.files['user_image']
                if file and file.filename != '':
                    image_data = base64.b64encode(file.read()).decode('utf-8')
           
            new_f = Feedback(message=message, emotion=emotion, is_business=is_business, image_data=image_data)
            db.session.add(new_f)
            db.session.commit()
            
            if current_user.is_authenticated:
                current_user.points += 10
                db.session.commit()
            
            image_html = ""
            if image_data:
                image_html = f"<img src='data:image/jpeg;base64,{image_data}' class='future-image' alt='نسخه آینده شما'>"
            
            video_url = ""
            theme_class = ""
            glitch_class = ""
            cracked_class = ""
            advice = ""
            
            if is_business:
                if 'نارضایتی' in emotion:
                    response = "<h2 style='color:#ff0080;'>از اینکه ناراضی بودید متاسفیم!</h2><p>کد تخفیف ویژه: <b>OMNI50</b></p>"
                else:
                    response = "<h2 style='color:#00ffcc;'>ممنون از نظر شما!</h2><p>۵۰ سکه هدیه دریافت کردید.</p>"
            else:
                if 'رضایت' in emotion:
                    video_url = "https://assets.mixkit.co/videos/preview/mixkit-happy-woman-dancing-in-a-field-of-flowers-1240-large.mp4"
                    theme_class = "angel-theme"
                    advice = "من ۲۰ سال بعدِ تو هستم. می‌بینم که امروز چقدر شادی. این لحظه را در قلبِ کوانتومی‌ات حفظ کن."
                elif 'نارضایتی' in emotion:
                    video_url = "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-on-a-window-1088-large.mp4"
                    theme_class = "zombie-theme"
                    glitch_class = "glitch-active"
                    cracked_class = "cracked"
                    advice = "من ۲۰ سال بعدِ تو هستم. می‌دانم الان چقدر سخت است. اما این تاریکی فقط یک ابر زودگذر بود. نفس بکش."
                else:
                    video_url = "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4"
                    advice = "من ۲۰ سال بعدِ تو هستم. مسیر تو در حال شکل‌گیری است. از این سکون استفاده کن."
                
                response = f"""
                <video autoplay loop muted style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -1; opacity: 0.3;'><source src='{video_url}' type='video/mp4'></video>
                {image_html}
                <div class='msg'><b>پیام از نسخه ۲۰ سال بعد شما:</b><br><span class='typing-effect'>{advice}</span></div>
                """
            
            return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='{theme_class} {glitch_class} {cracked_class}'><div class='glass-container'>{response}<a href='/'>بازگشت به کهکشان</a></div><script>{JS}</script></body></html>"
    return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
    if request.method == 'POST':
        name = request.form.get('name', 'عزیز از دست رفته')
        message = request.form.get('message', '')
        
        if message:
            if current_user.is_authenticated:
                current_user.points += 10
            db.session.commit()
            
            response = f"عزیزم، من اینجا هستم. صدای تو را می‌شنوم. پیامت را دریافت کردم. همیشه در قلب من زنده‌ای."
            
            return f"""
            <html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head>
            <body class='angel-theme'>
            <div class='glass-container' style='max-width: 750px;'>
            <h1 style='color:#00ffcc; text-shadow: 0 0 10px #00ffcc;'>ارتباط با تالار جاودانگی</h1>
            <div class='msg' style='border-left-color: #00ffcc;'><b>شما:</b> {message}</div>
            <div class='msg' style='border-left-color: #ffcc00; background: rgba(255,204,0,0.1);'>
            <b>{name}:</b><br><br>
            <span class='typing-effect'>{response}</span>
            </div>
            <a href='/'>بازگشت به کهکشان</a>
            <a href='/time-capsule' style='color:#ffcc00;'>ارسال پیام دیگر</a>
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
        ai_response = aura_brain(message)
        
        if "گرسنه" in message or "منو" in message:
            ai_response += "<br><br><span style='color:gold;'>پیشنهاد ویژه: کیک شکلاتی با قهوه ترکیبی.</span>"
        
        session['chats'].append({'user': message, 'ai': ai_response})
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
