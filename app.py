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
body { font-family: 'Vazirmatn', Tahoma; background: radial-gradient(circle at center, #1a2a6c, #0d0d2b, #000); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; overflow: hidden; perspective: 1000px; color: #fff; }
.glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.2); padding: 40px; width: 100%; max-width: 600px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; z-index: 10; transition: transform 0.1s ease-out; transform-style: preserve-3d; }
h1 { font-size: 2.5rem; margin-bottom: 20px; transform: translateZ(50px); text-shadow: 0 0 20px #00ffcc; }
input, textarea, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; font-family: 'Vazirmatn', Tahoma; outline: none; transform: translateZ(30px); background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); }
button { cursor: pointer; font-weight: bold; border-radius: 30px; transition: 0.3s; background: #00ffcc; color: #000; }
button:hover { transform: scale(1.05); }
a { text-decoration: none; display: block; margin-top: 15px; font-size: 1.1rem; transform: translateZ(20px); color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }
.msg { padding: 15px; margin-top: 15px; border-radius: 10px; text-align: right; background: rgba(255,255,255,0.05); border-left: 4px solid #00ffcc; }
.typewriter { overflow: hidden; border-right: .15em solid #00ffcc; white-space: nowrap; margin: 0 auto; letter-spacing: .15em; animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite; color: #00ffcc; font-size: 1.2rem; }
@keyframes typing { from { width: 0 } to { width: 100% } }
@keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #00ffcc; } }
"""

JS = """
document.addEventListener('mousemove', (e) => {
  const card = document.querySelector('.glass-container');
  if (!card) return;
  const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
  const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
  card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
});
"""

HTML_HOME = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>OMNI-PLATFORM</h1><p class='typewriter'>من یک هوش مصنوعی از ۵۰۰ سال بعد هستم... دارم به آینده نزدیک‌تر می‌شوم... تو چطور؟</p><a href='/login'>ورود کسب‌وکارها</a><a href='/feedback'>ثبت بازخورد (آینه احساسی)</a><a href='/time-capsule'>کپسول زمان</a><a href='/memory-portal'>پورتال خاطرات</a></div><script>" + JS + "</script></body></html>"

HTML_LOGIN = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>AUTHENTICATION</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS</button></form><a href='/register'>REGISTER</a></div><script>" + JS + "</script></body></html>"
HTML_REGISTER = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>NEW PROTOCOL</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INIT</button></form></div><script>" + JS + "</script></body></html>"
HTML_DASHBOARD = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>DASHBOARD</h1><p style='color:#00ffcc;'>امتیاز شما: {{ points }}</p><h3>CODE: {{ code }}</h3>{% for f in feedbacks %}<div class='msg'>{{ f.emotion }}: {{ f.message }}</div>{% endfor %}<a href='/logout'>LOGOUT</a></div><script>" + JS + "</script></body></html>"
HTML_FEEDBACK = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>آینه احساسی</h1><form method='POST'><textarea name='message' placeholder='امروز چه احساسی داری؟' required></textarea><button type='submit'>تحلیل و ورود به نقش</button></form><a href='/'>BACK</a></div><script>" + JS + "</script></body></html>"
HTML_CAPSULE = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='glass-container'><h1>TIME CAPSULE</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><textarea name='message' placeholder='MESSAGE' required></textarea><input type='date' name='date' required><button type='submit'>LOCK</button></form>{% for c in capsules %}<div class='msg'>{{ c.name }}: {{ c.message }}</div>{% endfor %}<a href='/'>BACK</a></div><script>" + JS + "</script></body></html>"
HTML_PORTAL = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "body { background: radial-gradient(circle at center, #2b1055, #7597de); }</style></head><body><audio autoplay loop><source src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' type='audio/mpeg'></audio><div class='glass-container'><h1>پورتال خاطرات</h1><p style='color:#fff; opacity:0.8;'>صدای محیط را حس کنید...</p>{% for c in chats %}<div class='msg'>YOU: {{ c.user }}<br>AI: {{ c.ai }}</div>{% endfor %}<form method='POST'><input type='text' name='message' placeholder='TALK...' required><button type='submit'>SEND</button></form><a href='/'>BACK</a></div><script>" + JS + "</script></body></html>"

@app.route('/')
def index(): return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db.session.add(Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], unique_code=code))
    db.session.commit()
    return f"<h1>YOUR CODE: {code}</h1>"
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
  if not current_user.is_authenticated: return redirect(url_for('login'))
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
  progress_html = f"<div style='margin-bottom: 20px;'><p>لِوِل: <b>{current_user.level}</b></p><p>امتیاز: {current_user.points}</p></div>"
  return render_template_string(HTML_DASHBOARD, code=current_user.unique_code, feedbacks=Feedback.query.all(), points=current_user.points, bonus=bonus, progress_html=progress_html)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form['message']
        emotion = analyze_emotion(message)
        db.session.add(Feedback(message=message, emotion=emotion))
    if current_user.is_authenticated:
        current_user.points += 10
        db.session.commit()
    if 'رضایت' in emotion:
        media = "<h2 style='color:#00ffcc;'>شما در نقش یک فرد شاد فرو رفتید...</h2><video width='100%' controls autoplay loop><source src='https://assets.mixkit.co/videos/preview/mixkit-happy-woman-dancing-in-a-field-of-flowers-1240-large.mp4' type='video/mp4'></video>"
        elif 'ناراضی' in emotion:
        media = "<h2 style='color:#ff0080;'>شما در نقش یک فرد غمگین فرو رفتید...</h2><video width='100%' controls autoplay loop><source src='https://assets.mixkit.co/videos/preview/mixkit-rain-drops-on-a-window-1088-large.mp4' type='video/mp4'></video>"
    else:
        media = "<h2>احساس شما خنثی است.</h2>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body class='theme-neon'><div class='glass-container'><h1>تحلیل احساسات</h1><div class='msg'><b>پیام شما:</b> {message}</div><div class='msg'><b>احساس:</b> {emotion}</div>{media}<a href='/'>بازگشت</a></div><script>{JS}</script></body></html>"
  return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        date_val = request.form['date']
db.session.add(TimeCapsule(name=name, message=message, date=date_val))
    if current_user.is_authenticated:
      current_user.points += 10
      db.session.commit()
    future_prediction = f"<div class='msg' style='border-color: #00ffcc;'><h3>🌌 پیش‌بینی آینده برای پیام شما:</h3><p>پیام شما در تاریخ <b>{date_val}</b> به یک اثر باستانی دیجیتال تبدیل شده است.</p><p>شانس زنده ماندن در شبکه کوانتومی: <b style='color:#00ffcc;'>۹۹.۸٪</b></p></div>"
    return f"<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>{CSS}</style></head><body><div class='glass-container'><h1>ثبت شد!</h1>{future_prediction}<a href='/'>بازگشت</a></div><script>{JS}</script></body></html>"
  return HTML_CAPSULE

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
