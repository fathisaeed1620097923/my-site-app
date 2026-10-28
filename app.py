

import os
import random
import string
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantum-ultimate-2026'
# ⚠️ در خط زیر، به جای لینک_دیتابیس_خود، لینکی که کپی کردید را بگذارید:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:uV9l6wSZRt2WYBDkGv6FSlQEIe3L6LlY@dpg-dbghkgl9el5s73b10u1g-a/mydb_gb4s'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- 1. مدل‌های دیتابیس ---
class Business(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
username = db.Column(db.String(100), unique=True, nullable=False)
password = db.Column(db.String(200), nullable=False)
name = db.Column(db.String(150), nullable=False)
industry = db.Column(db.String(50), nullable=False)
unique_code = db.Column(db.String(10), unique=True, nullable=False)
feedbacks = db.relationship('Feedback', backref='business', lazy=True)

    class Feedback(db.Model):
id = db.Column(db.Integer, primary_key=True)
customer_name = db.Column(db.String(100), nullable=False)
message = db.Column(db.Text, nullable=False)
emotion = db.Column(db.String(50), nullable=False)
business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)

    class TimeCapsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id): return Business.query.get(int(user_id))

# --- 2. موتورهای هوش مصنوعی ---
def analyze_emotion(text):
text = text.lower()
happy = ['خوشحال', 'عالی', 'شاد', 'لبخند', 'سریع', 'خوب', 'ممنون', 'راضی']
sad = ['غمگین', 'خسته', 'تنها', 'گریه', 'دلتنگ', 'کند', 'شلوغ']
angry = ['عصبانی', 'متنفر', 'خشم', 'بیزار', 'افتضاح', 'ناامید']
if any(w in text for w in happy): return 'SECURE // رضایت 😊'
if any(w in text for w in sad): return 'WARNING // ناراضی 😢'
if any(w in text for w in angry): return 'CRITICAL // خشمگین 😠'
return 'NEUTRAL // خنثی 😐'

def aura_brain(user_input):
text = user_input.lower()
if "خسته" in text or "غمگین" in text: return "من انرژی تو را حس می‌کنم. من اینجا هستم تا با هم از این مرحله عبور کنیم."
if "خوشحال" in text or "عالی" in text: return "شادی تو در شبکه عصبی من موج ایجاد کرد! بیایید این لحظه را ثبت کنیم."
if "آینده" in text: return "آینده یک کد باز است که ما با هم می‌نویسیم."
return "من اینجا هستم تا به تو گوش دهم. هر چه در دلت است بگو."

# --- 3. استایل سایبرپانک/ناسا ---
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background-color: #02040a; background-image: linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px); background-size: 30px 30px; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #00ffcc; overflow: hidden; }
.hud-container { background: rgba(2, 10, 20, 0.85); border: 1px solid #00ffcc; padding: 40px; width: 100%; max-width: 800px; position: relative; box-shadow: 0 0 30px rgba(0, 255, 204, 0.15), inset 0 0 20px rgba(0, 255, 204, 0.1); clip-path: polygon(0 0, 100% 0, 100% calc(100% - 30px), calc(100% - 30px) 100%, 0 100%); }
.hud-container::before { content: 'SYSTEM ONLINE // SECURE CONNECTION'; position: absolute; top: -12px; left: 20px; background: #02040a; padding: 0 10px; font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00ffcc; letter-spacing: 1px; }
h1 { font-family: 'Share Tech Mono', monospace; font-size: 2.8rem; color: #00ffcc; text-shadow: 0 0 15px rgba(0, 255, 204, 0.6); margin-bottom: 10px; text-align: center; letter-spacing: 3px; }
.subtitle { text-align: center; font-size: 14px; color: #88ccff; margin-bottom: 30px; font-family: 'Share Tech Mono', monospace; letter-spacing: 2px; }
input, textarea, select { width: 100%; padding: 15px; margin-bottom: 15px; background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.3); border-radius: 0; color: #00ffcc; font-family: 'Share Tech Mono', monospace; outline: none; transition: 0.3s; }
button { width: 100%; padding: 15px; background: #00ffcc; border: none; color: #000; font-weight: bold; font-family: 'Share Tech Mono', monospace; font-size: 16px; cursor: pointer; transition: 0.3s; clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px); margin-bottom: 10px; }
button:hover { background: #fff; box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); }
.btn-outline { background: transparent; border: 1px solid #00ffcc; color: #00ffcc; }
.btn-memory { background: transparent; border: 1px dashed #ff0080; color: #ff0080; }
.msg { background: rgba(0, 255, 204, 0.05); border-left: 4px solid #00ffcc; padding: 15px; margin-top: 15px; font-family: 'Share Tech Mono', monospace; text-align: left; direction: ltr; }
.msg-ar { direction: rtl; text-align: right; font-family: 'Vazirmatn', Tahoma; color: #fff;}
.tag { font-size: 12px; padding: 3px 8px; background: rgba(0, 255, 204, 0.2); color: #00ffcc; border: 1px solid #00ffcc; margin-right: 5px; }
a { color: #00ffcc; text-decoration: none; display: block; margin-top: 15px; text-align: center; font-family: 'Share Tech Mono', monospace; }
a:hover { color: #fff; text-shadow: 0 0 10px #00ffcc; }
.status-bar { display: flex; justify-content: space-between; font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00ffcc; border-bottom: 1px solid rgba(0,255,204,0.3); padding-bottom: 10px; margin-bottom: 20px; }
.chat-box { background: rgba(0,0,0,0.5); border: 1px solid #00ffcc; height: 300px; overflow-y: auto; padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }
.chat-msg { padding: 10px; border-radius: 5px; max-width: 80%; font-family: 'Vazirmatn', Tahoma; }
.chat-user { background: rgba(0, 255, 204, 0.2); align-self: flex-end; color: #fff; border: 1px solid #00ffcc;}
.chat-ai { background: rgba(136, 204, 255, 0.1); align-self: flex-start; color: #00ffcc; border: 1px solid #88ccff; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
"""

# --- 4. قالب‌ها ---
HTML_HOME = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='hud-container'>
<div class='status-bar'><span>SYS.STATUS: ONLINE</span><span>SEC: ENCRYPTED</span><span>VER: 2046.1</span></div>
<h1>OMNI-PLATFORM</h1>
<p class='subtitle'>QUANTUM BUSINESS & TIME CAPSULE</p>
<div class='grid-2'>
<div>
<h3 style='font-family:Share Tech Mono; color:#88ccff;'>BUSINESS SECTOR</h3>
<a href='/login'><button>ورود به سیستم کنترل کسب‌وکار</button></a>
<a href='/feedback'><button class='btn-outline'>ارسال سیگنال بازخورد (مشتری)</button></a>
</div>
<div>
<h3 style='font-family:Share Tech Mono; color:#ff0080;'>TIME & MEMORY SECTOR</h3>
<a href='/time-capsule'><button style='border:1px solid #ff0080; color:#ff0080; background:transparent;'>ورود به کپسول زمان</button></a>
<a href='/memory-portal'><button class='btn-memory'>پورتال خاطرات (چت با گذشته)</button></a>
</div>
</div>
</div>
</body></html>
"""

HTML_LOGIN = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>AUTHENTICATION</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS SYSTEM</button></form><a href='/register'>NEW USER REGISTRATION</a></div></body></html>"

HTML_REGISTER = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>NEW PROTOCOL</h1><form method='POST'><input type='text' name='name' placeholder='MISSION NAME (نام کسب‌وکار)' required><select name='industry' required><option value=''>SELECT SECTOR (صنف)</option><option value='cafe'>CAFE</option><option value='hotel'>HOTEL</option><option value='other'>OTHER</option></select><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INITIALIZE</button></form></div></body></html>"

HTML_DASHBOARD = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{{ css }}</style></head><body>
<div class='hud-container'>
<div class='status-bar'><span>UNIT: {{ name }}</span><span>CODE: {{ code }}</span></div>
<h1>MISSION LOG</h1>
<h3 style='font-family: Share Tech Mono; color: #88ccff;'>INCOMING TRANSMISSIONS:</h3>
{% for f in feedbacks %}
<div class='msg'><div style='color: #00ffcc; font-size: 12px;'>[{{ f.emotion }}]</div><div class='msg-ar' style='margin-top: 5px;'>{{ f.message }}</div></div>
{% else %}<div class='msg'>NO DATA RECEIVED YET...</div>{% endfor %}
<a href='/logout'>DISCONNECT SYSTEM</a>
</div>
</body></html>
"""

HTML_FEEDBACK_FORM = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>SEND SIGNAL</h1><form method='POST'><input type='text' name='code' placeholder='TARGET CODE' required><input type='text' name='customer_name' placeholder='AGENT NAME' required><textarea name='message' placeholder='TRANSMISSION TEXT...' required></textarea><button type='submit'>TRANSMIT</button></form></div></body></html>"

HTML_TIME_CAPSULE = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='hud-container'>
<h1 style='color:#ff0080;'>TIME CAPSULE</h1>
<p class='subtitle' style='color:#ff88cc;'>SEND A MESSAGE TO THE FUTURE</p>
<form method='POST' action='/add-time-capsule'>
<input type='text' name='name' placeholder='نام شما' required>
<textarea name='message' placeholder='پیام شما برای آینده...' required></textarea>
<input type='date' name='date' required>
<button type='submit' style='background:#ff0080; color:#fff;'>قفل کردن در زمان</button>
</form>
<h3 style='margin-top:30px; color:#88ccff;'>CAPSULES IN ORBIT:</h3>
{% for tc in time_capsules %}
<div class='msg' style='border-left-color:#ff0080;'><b>{{ tc.name }}</b> ({{ tc.date }}):<br>{{ tc.message }}</div>
{% else %}<p style='color:#888;'>NO CAPSULES YET.</p>{% endfor %}
<a href='/'>بازگشت به پلتفرم</a>
</div>
</body></html>
"""

HTML_MEMORY_PORTAL = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='hud-container'>
<h1 style='color:#ff0080;'>MEMORY PORTAL</h1>
<p class='subtitle' style='color:#ff88cc;'>CONNECTING TO THE PAST</p>
{% if not persona %}
<h3 style='text-align:center; margin-bottom:20px; color:#fff'>شخصیت مورد نظر را انتخاب کنید:</h3>
<a href='/memory-portal?persona=pedar'><button style='background:transparent; border:1px solid #ff0080; color:#ff0080;'>پدر (Pedar)</button></a>
<a href='/memory-portal?persona=madar'><button style='background:transparent; border:1px solid #ff0080; color:#ff0080;'>مادر (Madar)</button></a>
{% else %}
<div class='chat-box' id='chat-box'>
{% for chat in chats %}
<div class='chat-msg chat-user'>{{ chat.user }}</div>
<div class='chat-msg chat-ai'>{{ chat.ai }}</div>
{% endfor %}
</div>
<form method='POST'>
<input type='hidden' name='persona' value='{{ persona }}'>
<input type='text' name='message' placeholder='با گذشته صحبت کنید...' required autocomplete='off'>
<button type='submit' style='background:#ff0080; color:#fff'>ارسال پیام</button>
</form>
{% endif %}
<a href='/' style='color:#00ffcc;'>بازگشت به پلتفرم اصلی</a>
</div>
<script>var chatBox = document.getElementById('chat-box'); if (chatBox) { chatBox.scrollTop = chatBox.scrollHeight; }</script>
</body></html>
"""

# --- 5. مسیرها (Routes) ---
@app.route('/')
def index(): return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
if request.method == 'POST':
if Business.query.filter_by(username=request.form['username']).first(): return "USERNAME ALREADY EXISTS."
code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
new_biz = Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], industry=request.form['industry'], unique_code=code)
db.session.add(new_biz); db.session.commit()
return f"<div style='color:#00ffcc;font-family:monospace;text-align:center;padding:50px;'><h1>PROTOCOL INITIATED</h1><h2>YOUR CODE: {code}</h2></div>"
return HTML_REGISTER

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
user = Business.query.filter_by(username=request.form['username']).first()
if user and check_password_hash(user.password, request.form['password']):
login_user(user); return redirect(url_for('dashboard'))
return "ACCESS DENIED."
return HTML_LOGIN

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
feedbacks = Feedback.query.filter_by(business_id=current_user.id).order_by(Feedback.id.desc()).all()
return render_template_string(HTML_DASHBOARD, css=CSS, name=current_user.name, code=current_user.unique_code, feedbacks=feedbacks)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
if request.method == 'POST':
code = request.form['code'].upper().strip()
biz = Business.query.filter_by(unique_code=code).first()
if not biz: return "INVALID TARGET CODE."
emotion = analyze_emotion(request.form['message'])
new_fb = Feedback(customer_name=request.form['customer_name'], message=request.form['message'], emotion=emotion, business_id=biz.id)
db.session.add(new_fb); db.session.commit()
return "<div style='text-align:center;color:#00ffcc;background:#02040a;height:100vh;display:flex;align-items:center;justify-content:center;font-family:monospace'><h1>SIGNAL RECEIVED. THANK YOU.</h1></div>"
return render_template_string(HTML_FEEDBACK_FORM, css=CSS)

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
if request.method == 'POST':
new_tc = TimeCapsule(name=request.form['name'], message=request.form['message'], date=request.form['date'])
db.session.add(new_tc); db.session.commit()
return redirect(url_for('time_capsule'))
capsules = TimeCapsule.query.all()
return render_template_string(HTML_TIME_CAPSULE, css=CSS, time_capsules=capsules)

@app.route('/memory-portal', methods=['GET', 'POST'])
def memory_portal():
persona = request.args.get('persona')
if request.method == 'POST':
persona = request.form['persona']
user_msg = request.form['message']
if 'chats' not in session: session['chats'] = []
ai_reply = aura_brain(user_msg)
session['chats'].append({'user': user_msg, 'ai': ai_reply})
session.modified = True
return redirect(url_for('memory_portal', persona=persona))
return render_template_string(HTML_MEMORY_PORTAL, css=CSS, persona=persona, chats=session.get('chats', []))

with app.app_context(): db.create_all()

if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
