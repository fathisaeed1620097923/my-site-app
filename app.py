
import os
import random
import string
from datetime import date
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'future-500-years'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:5VAUU122WDEqj8UepCJypXIpdA8Vl8ip@dpg-dbi7boui0phs73d2ime0-a.oregon-postgres.render.com/mydb_ecw3'
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
    if any(w in text for w in ['خوشحال', 'عالی', 'شاد']): return 'رضایت 😊'
    if any(w in text for w in ['غمگین', 'خسته', 'بد']): return 'ناراضی 😢'
    return 'خنثی 😐'

def aura_brain(user_input):
    text = user_input.lower()
    if "خسته" in text: return "من اینجا هستم تا کمکت کنم."
    if "خوشحال" in text: return "شادی تو عالیه!"
    return "من به تو گوش می‌دهم."

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; overflow: hidden; position: relative; transition: background 0.5s; }
.glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.2); padding: 40px; width: 100%; max-width: 600px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; z-index: 10; }
h1 { font-size: 2.5rem; margin-bottom: 20px; }
input, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; font-family: 'Vazirmatn', Tahoma; outline: none; }
button { cursor: pointer; font-weight: bold; border-radius: 30px; transition: 0.3s; }
a { text-decoration: none; display: block; margin-top: 15px; font-size: 1.1rem; }
.msg { padding: 15px; margin-top: 15px; border-radius: 10px; text-align: right; }
.theme-btn { display: inline-block; padding: 8px 15px; margin: 5px; border-radius: 20px; cursor: pointer; font-size: 0.9rem; border: 1px solid; text-decoration: none; }
.theme-paradise { background: linear-gradient(135deg, #e0f7fa, #b2ebf2); color: #006064; }
.theme-paradise .glass-container { background: rgba(255,255,255,0.7); border-color: #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.theme-paradise a { color: #00838f; }
.theme-paradise input, .theme-paradise textarea { background: #fff; border: 1px solid #80deea; color: #006064; }
.theme-paradise button { background: #006064; color: #fff; }
.theme-paradise .msg { background: rgba(0,0,0,0.05); border-left: 4px solid #006064; }
.theme-zombie { background: #1a0000; color: #ff3333; animation: shake 0.5s infinite; }
.theme-zombie .glass-container { background: rgba(50, 0, 0, 0.8); border-color: #ff0000; box-shadow: 0 0 20px #ff0000; }
.theme-zombie a { color: #ff6666; }
.theme-zombie input, .theme-zombie textarea { background: #000; border: 1px solid #ff0000; color: #ff3333; }
.theme-zombie button { background: #ff0000; color: #000; }
.theme-zombie .msg { background: rgba(255,0,0,0.1); border-left: 4px solid #ff0000; }
@keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); } 10% { transform: translate(-1px, -2px) rotate(-1deg); } 20% { transform: translate(-3px, 0px) rotate(1deg); } 30% { transform: translate(3px, 2px) rotate(0deg); } 40% { transform: translate(1px, -1px) rotate(1deg); } 50% { transform: translate(-1px, 2px) rotate(-1deg); } 60% { transform: translate(-3px, 1px) rotate(0deg); } 70% { transform: translate(3px, 1px) rotate(-1deg); } 80% { transform: translate(-1px, -1px) rotate(1deg); } 90% { transform: translate(1px, 2px) rotate(0deg); } 100% { transform: translate(1px, -2px) rotate(-1deg); } }
.theme-neon { background: #0a0a0a; color: #00ffcc; }
.theme-neon .glass-container { border-color: #00ffcc; box-shadow: 0 0 30px rgba(0,255,204,0.2); }
.theme-neon a { color: #00ffcc; }
.theme-neon input, .theme-neon textarea { background: #111; border: 1px solid #00ffcc; color: #00ffcc; }
.theme-neon button { background: #00ffcc; color: #000; }
.theme-neon .msg { background: rgba(0,255,204,0.05); border-left: 4px solid #00ffcc; }
.theme-void { background: #000; color: #888; }
.theme-void .glass-container { background: #111; border-color: #333; }
.theme-void a { color: #fff; }
.theme-void input, .theme-void textarea { background: #222; border: 1px solid #444; color: #fff; }
.theme-void button { background: #fff; color: #000; }
.theme-void .msg { background: rgba(255,255,255,0.05); border-left: 4px solid #fff; }
"""

@app.route('/')
def index():
    theme = request.args.get('theme', session.get('theme', 'theme-neon'))
    session['theme'] = theme
    sound_html = ""
    if theme == 'theme-paradise': sound_html = "<audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3' type='audio/mpeg'></audio>"
    elif theme == 'theme-zombie': sound_html = "<audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3' type='audio/mpeg'></audio>"
    elif theme == 'theme-neon': sound_html = "<audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3' type='audio/mpeg'></audio>"
    elif theme == 'theme-void': sound_html = "<audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3' type='audio/mpeg'></audio>"
    theme_selector = "<div style='margin-bottom: 20px;'><span style='font-size: 0.9rem; opacity: 0.7;'>انتخاب دنیا:</span><br><a href='/?theme=theme-paradise' class='theme-btn' style='color:#006064; border-color:#006064;'>بهشتی</a><a href='/?theme=theme-zombie' class='theme-btn' style='color:#ff3333; border-color:#ff3333;'>مردگان</a><a href='/?theme=theme-neon' class='theme-btn' style='color:#00ffcc; border-color:#00ffcc;'>سایبرپانک</a><a href='/?theme=theme-void' class='theme-btn' style='color:#fff; border-color:#fff;'>سیاه‌چال</a></div>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='{theme}'>{sound_html}<div class='glass-container'><h1>OMNI-PLATFORM</h1>{theme_selector}<a href='/login'>ورود کسب‌وکارها</a><a href='/feedback'>ثبت بازخورد</a><a href='/time-capsule'>کپسول زمان</a><a href='/memory-portal'>پورتال خاطرات</a></div></body></html>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        db.session.add(Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], unique_code=code))
        db.session.commit()
        return f"<h1>YOUR CODE: {code}</h1>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>NEW PROTOCOL</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INIT</button></form></div></body></html>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Business.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user); return redirect(url_for('dashboard'))
        return "ACCESS DENIED."
return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>AUTHENTICATION</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS</button></form><a href='/register'>REGISTER</a></div></body></html>"

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    today = date.today()
    bonus = ""
    if current_user.last_login != today:
        current_user.points += 20
        current_user.last_login = today
        db.session.commit()
        bonus = "<div class='msg' style='border-color: #00ffcc; color: #00ffcc;'>🎉 پاداش ورود روزانه: +۲۰ امتیاز!</div>"
    current_user.level = (current_user.points // 100) + 1
    db.session.commit()
    progress = current_user.points % 100
    progress_html = f"<div style='margin-bottom: 20px;'><p>لِوِل: <b>{current_user.level}</b></p><p>امتیاز: {current_user.points}</p><div class='progress-bar'><div class='progress-fill' style='width: {progress}%;'></div></div></div>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>DASHBOARD</h1>{bonus}{progress_html}<h3>CODE: {current_user.unique_code}</h3>{''.join([f'<div class=msg>{f.emotion}: {f.message}</div>' for f in Feedback.query.all()])}<a href='/logout'>LOGOUT</a></div></body></html>"

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form['message']
        emotion = analyze_emotion(message)
        db.session.add(Feedback(message=message, emotion=emotion))
        if current_user.is_authenticated:
            current_user.points += 10
        db.session.commit()
        return f"<h1>SAVED: {emotion}</h1>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>آینه احساسی</h1><form method='POST'><textarea name='message' placeholder='امروز چه احساسی داری؟' required></textarea><button type='submit'>تحلیل و ورود به نقش</button></form><a href='/'>BACK</a></div></body></html>"

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
    if request.method == 'POST':
        db.session.add(TimeCapsule(name=request.form['name'], message=request.form['message'], date=request.form['date']))
        if current_user.is_authenticated:
            current_user.points += 10
        db.session.commit()
        return redirect(url_for('time_capsule'))
    capsules = TimeCapsule.query.all()
    cap_html = ''.join([f"<div class='msg'>{c.name}: {c.message}</div>" for c in capsules])
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>TIME CAPSULE</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><textarea name='message' placeholder='MESSAGE' required></textarea><input type='date' name='date' required><button type='submit'>LOCK</button></form>{cap_html}<a href='/'>BACK</a></div></body></html>"

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
    chats = session.get('chats', [])
    chat_html = ''.join([f"<div class='msg'>YOU: {c['user']}<br>AI: {c['ai']}</div>" for c in chats])
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-dark'><div class='glass-container'><h1>PORTAL</h1>{chat_html}<form method='POST'><input type='text' name='message' placeholder='TALK...' required><button type='submit'>SEND</button></form><a href='/'>BACK</a></div></body></html>"

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
