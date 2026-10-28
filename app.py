

import os
import random
import string
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantum-ultimate-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:uV9l6wSZRt2WYBDkGv6FSlQEIe3L6LlY@dpg-dbghkgl9el5s73b10u1g-a.frankfurt-postgres.render.com/mydb_gb4s'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Business(UserMixin, db.Model):
id = db.Column(db.Integer, primary_key=True)
username = db.Column(db.String(100), unique=True, nullable=False)
password = db.Column(db.String(200), nullable=False)
name = db.Column(db.String(150), nullable=False)
unique_code = db.Column(db.String(10), unique=True, nullable=False)

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
if any(w in text for w in ['خوشحال', 'عالی', 'شاد']): return 'رضایت 😊'
if any(w in text for w in ['غمگین', 'خسته', 'بد']): return 'ناراضی 😢'
return 'خنثی 😐'

def aura_brain(user_input):
text = user_input.lower()
if "خسته" in text: return "من اینجا هستم تا کمکت کنم."
if "خوشحال" in text: return "شادی تو عالیه!"
return "من به تو گوش می‌دهم."

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background-color: #02040a; background-image: linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px); background-size: 30px 30px; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #00ffcc; overflow: hidden; }
.hud-container { background: rgba(2, 10, 20, 0.85); border: 1px solid #00ffcc; padding: 40px; width: 100%; max-width: 600px; position: relative; box-shadow: 0 0 30px rgba(0, 255, 204, 0.15); clip-path: polygon(0 0, 100% 0, 100% calc(100% - 30px), calc(100% - 30px) 100%, 0 100%); }
.hud-container::before { content: 'SYSTEM ONLINE // SECURE CONNECTION'; position: absolute; top: -12px; left: 20px; background: #02040a; padding: 0 10px; font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00ffcc; letter-spacing: 1px; }
h1 { font-family: 'Share Tech Mono', monospace; font-size: 2.5rem; color: #00ffcc; text-shadow: 0 0 15px rgba(0, 255, 204, 0.6); margin-bottom: 20px; text-align: center; letter-spacing: 3px; }
input, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.3); color: #00ffcc; font-family: 'Share Tech Mono', monospace; outline: none; transition: 0.3s; }
button { background: #00ffcc; color: #000; cursor: pointer; font-weight: bold; clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px); }
a { color: #ff0080; text-decoration: none; display: block; margin-top: 15px; text-align: center; font-family: 'Share Tech Mono', monospace; font-size: 1.1rem; }
.msg { background: rgba(0, 255, 204, 0.05); border-left: 4px solid #00ffcc; padding: 15px; margin-top: 15px; }
.lang-btn { background: transparent; border: 1px solid #ff0080; color: #ff0080; margin-top: 20px; }
"""

# --- دیکشنری دو زبانه ---
LANG = {
'fa': {
'home': 'OMNI-PLATFORM', 'login': 'ورود کسب‌وکارها', 'feedback': 'ثبت بازخورد', 'capsule': 'کپسول زمان', 'portal': 'پورتال خاطرات',
'login_title': 'AUTHENTICATION', 'register': 'ثبت‌نام', 'username': 'نام کاربری', 'password': 'رمز عبور', 'access': 'ورود به سیستم',
'reg_title': 'NEW PROTOCOL', 'name': 'نام کسب‌وکار', 'init': 'ثبت‌نام', 'dash_title': 'داشبورد', 'code': 'کد اختصاصی',
'logout': 'خروج', 'fb_title': 'ثبت بازخورد', 'msg': 'پیام شما', 'send': 'ارسال', 'back': 'بازگشت',
'cap_title': 'کپسول زمان', 'cap_name': 'نام شما', 'cap_msg': 'پیام برای آینده', 'lock': 'قفل کردن',
'portal_title': 'پورتال خاطرات', 'talk': 'با گذشته صحبت کنید...', 'lang_btn': 'Change to English'
},
'en': {
'home': 'OMNI-PLATFORM', 'login': 'Business Login', 'feedback': 'Submit Feedback', 'capsule': 'Time Capsule', 'portal': 'Memory Portal',
'login_title': 'AUTHENTICATION', 'register': 'Register', 'username': 'Username', 'password': 'Password', 'access': 'Access System',
'reg_title': 'NEW PROTOCOL', 'name': 'Business Name', 'init': 'Initialize', 'dash_title': 'Dashboard', 'code': 'Unique Code',
'logout': 'Logout', 'fb_title': 'Submit Feedback', 'msg': 'Your Message', 'send': 'Send', 'back': 'Back',
'cap_title': 'Time Capsule', 'cap_name': 'Your Name', 'cap_msg': 'Message to Future', 'lock': 'Lock',
'portal_title': 'Memory Portal', 'talk': 'Talk to the past...', 'lang_btn': 'تغییر به فارسی'
}
}

def get_lang():
lang = request.args.get('lang', 'fa')
return lang, LANG[lang]

# --- قالب‌های HTML با پشتیبانی از دو زبان ---
HTML_HOME = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.home }}</h1><a href='/login?lang={{ lang }}'>{{ t.login }}</a><a href='/feedback?lang={{ lang }}'>{{ t.feedback }}</a><a href='/time-capsule?lang={{ lang }}'>{{ t.capsule }}</a><a href='/memory-portal?lang={{ lang }}'>{{ t.portal }}</a><a href='/?lang={{ 'en' if lang == 'fa' else 'fa' }}' class='lang-btn'>{{ t.lang_btn }}</a></div></body></html>"

HTML_LOGIN = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.login_title }}</h1><form method='POST'><input type='text' name='username' placeholder='{{ t.username }}' required><input type='password' name='password' placeholder='{{ t.password }}' required><button type='submit'>{{ t.access }}</button></form><a href='/register?lang={{ lang }}'>{{ t.register }}</a></div></body></html>"

HTML_REGISTER = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.reg_title }}</h1><form method='POST'><input type='text' name='name' placeholder='{{ t.name }}' required><input type='text' name='username' placeholder='{{ t.username }}' required><input type='password' name='password' placeholder='{{ t.password }}' required><button type='submit'>{{ t.init }}</button></form></div></body></html>"

HTML_DASHBOARD = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.dash_title }}</h1><h3>{{ t.code }}: {{ code }}</h3>{% for f in feedbacks %}<div class='msg'>{{ f.emotion }}: {{ f.message }}</div>{% endfor %}<a href='/logout?lang={{ lang }}'>{{ t.logout }}</a></div></body></html>"

HTML_FEEDBACK = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.fb_title }}</h1><form method='POST'><textarea name='message' placeholder='{{ t.msg }}' required></textarea><button type='submit'>{{ t.send }}</button></form><a href='/?lang={{ lang }}'>{{ t.back }}</a></div></body></html>"

HTML_CAPSULE = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.cap_title }}</h1><form method='POST'><input type='text' name='name' placeholder='{{ t.cap_name }}' required><textarea name='message' placeholder='{{ t.cap_msg }}' required></textarea><input type='date' name='date' required><button type='submit'>{{ t.lock }}</button></form>{% for c in capsules %}<div class='msg'>{{ c.name }}: {{ c.message }}</div>{% endfor %}<a href='/?lang={{ lang }}'>{{ t.back }}</a></div></body></html>"

HTML_PORTAL = "<!DOCTYPE html><html lang='{{ lang }}' dir='{{ 'rtl' if lang == 'fa' else 'ltr' }}'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>{{ t.portal_title }}</h1>{% for c in chats %}<div class='msg'>YOU: {{ c.user }}<br>AI: {{ c.ai }}</div>{% endfor %}<form method='POST'><input type='text' name='message' placeholder='{{ t.talk }}' required><button type='submit'>{{ t.send }}</button></form><a href='/?lang={{ lang }}'>{{ t.back }}</a></div></body></html>"

# --- مسیرها ---
@app.route('/')
def index():
lang, t = get_lang()
return render_template_string(HTML_HOME, lang=lang, t=t)

@app.route('/register', methods=['GET', 'POST'])
def register():
lang, t = get_lang()
if request.method == 'POST':
code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
db.session.add(Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], unique_code=code))
db.session.commit()
return f"<h1>YOUR CODE: {code}</h1>"
return render_template_string(HTML_REGISTER, lang=lang, t=t)

@app.route('/login', methods=['GET', 'POST'])
def login():
lang, t = get_lang()
if request.method == 'POST':
user = Business.query.filter_by(username=request.form['username']).first()
if user and check_password_hash(user.password, request.form['password']):
login_user(user); return redirect(url_for('dashboard', lang=lang))
return "ACCESS DENIED."
return render_template_string(HTML_LOGIN, lang=lang, t=t)

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
lang, t = get_lang()
return render_template_string(HTML_DASHBOARD, lang=lang, t=t, code=current_user.unique_code, feedbacks=Feedback.query.all())

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
lang, t = get_lang()
if request.method == 'POST':
emotion = analyze_emotion(request.form['message'])
db.session.add(Feedback(message=request.form['message'], emotion=emotion))
db.session.commit()
return f"<h1>SAVED: {emotion}</h1>"
return render_template_string(HTML_FEEDBACK, lang=lang, t=t)

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
lang, t = get_lang()
if request.method == 'POST':
db.session.add(TimeCapsule(name=request.form['name'], message=request.form['message'], date=request.form['date']))
db.session.commit()
return redirect(url_for('time_capsule', lang=lang))
return render_template_string(HTML_CAPSULE, lang=lang, t=t, capsules=TimeCapsule.query.all())

@app.route('/memory-portal', methods=['GET', 'POST'])
def memory_portal():
lang, t = get_lang()
if request.method == 'POST':
if 'chats' not in session: session['chats'] = []
session['chats'].append({'user': request.form['message'], 'ai': aura_brain(request.form['message'])})
session.modified = True
return redirect(url_for('memory_portal', lang=lang))
return render_template_string(HTML_PORTAL, lang=lang, t=t, chats=session.get('chats', []))

with app.app_context():
db.create_all()

if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
