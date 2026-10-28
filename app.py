

import os
import random
import string
from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantum-ultimate-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:uV9l6wSZRt2WYBDkGv6FSlQEIe3L6LlY@dpg-dbghkgl9el5s73b10u1g-a/mydb_gb4s'
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
industry = db.Column(db.String(50), nullable=False)
unique_code = db.Column(db.String(10), unique=True, nullable=False)

class Feedback(db.Model):
id = db.Column(db.Integer, primary_key=True)
customer_name = db.Column(db.String(100), nullable=False)
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
if any(w in text for w in ['خوشحال', 'عالی', 'شاد', 'خوب']): return 'رضایت 😊'
if any(w in text for w in ['غمگین', 'خسته', 'بد', 'افتضاح']): return 'ناراضی 😢'
return 'خنثی 😐'

def aura_brain(user_input):
text = user_input.lower()
if "خسته" in text or "غمگین" in text: return "من انرژی تو را حس می‌کنم. من اینجا هستم."
if "خوشحال" in text or "عالی" in text: return "شادی تو در شبکه عصبی من موج ایجاد کرد!"
return "من اینجا هستم تا به تو گوش دهم."

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma; background-color: #02040a; background-image: linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px); background-size: 30px 30px; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #00ffcc; overflow: hidden; }
.hud-container { background: rgba(2, 10, 20, 0.85); border: 1px solid #00ffcc; padding: 40px; width: 100%; max-width: 800px; position: relative; box-shadow: 0 0 30px rgba(0, 255, 204, 0.15); clip-path: polygon(0 0, 100% 0, 100% calc(100% - 30px), calc(100% - 30px) 100%, 0 100%); }
h1 { font-family: 'Share Tech Mono', monospace; font-size: 2.8rem; color: #00ffcc; text-shadow: 0 0 15px rgba(0, 255, 204, 0.6); margin-bottom: 10px; text-align: center; letter-spacing: 3px; }
input, textarea, select, button { width: 100%; padding: 15px; margin-bottom: 15px; background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.3); color: #00ffcc; font-family: 'Share Tech Mono', monospace; outline: none; }
button { background: #00ffcc; color: #000; cursor: pointer; }
.msg { background: rgba(0, 255, 204, 0.05); border-left: 4px solid #00ffcc; padding: 15px; margin-top: 15px; }
.chat-box { background: rgba(0,0,0,0.5); border: 1px solid #00ffcc; height: 300px; overflow-y: auto; padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }
.chat-msg { padding: 10px; border-radius: 5px; max-width: 80%; }
.chat-user { background: rgba(0, 255, 204, 0.2); align-self: flex-end; }
.chat-ai { background: rgba(136, 204, 255, 0.1); align-self: flex-start; }
a { color: #00ffcc; text-decoration: none; display: block; margin-top: 15px; text-align: center; }
"""

HTML_HOME = """
<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>""" + CSS + """</style></head><body>
<div class='hud-container'>
<h1>OMNI-PLATFORM</h1>
<p style='text-align:center;color:#88ccff;'>QUANTUM BUSINESS & TIME CAPSULE</p>
<a href='/login'><button>ورود کسب‌وکارها</button></a>
<a href='/feedback'><button style='background:transparent;border:1px solid #00ffcc'>ثبت بازخورد (مشتری)</button></a>
<a href='/time-capsule'><button style='background:transparent;border:1px solid #ff0080;color:#ff0080'>کپسول زمان</button></a>
<a href='/memory-portal'><button style='background:transparent;border:1px dashed #ff0080;color:#ff0080'>پورتال خاطرات (چت با گذشته)</button></a>
</div>
</body></html>
"""

HTML_LOGIN = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>AUTHENTICATION</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS SYSTEM</button></form><a href='/register'>NEW USER REGISTRATION</a></div></body></html>"

HTML_REGISTER = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>NEW PROTOCOL</h1><form method='POST'><input type='text' name='name' placeholder='MISSION NAME (نام کسب‌وکار)' required><input type='text' name='industry' placeholder='INDUSTRY (صنف)' required><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INITIALIZE</button></form></div></body></html>"

HTML_DASHBOARD = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>MISSION LOG</h1><h3 style='color:#88ccff;'>CODE: {{ code }}</h3>{% for f in feedbacks %}<div class='msg'><span style='color:#00ffcc;'>[{{ f.emotion }}]</span> {{ f.customer_name }}: {{ f.message }}</div>{% endfor %}<a href='/logout'>DISCONNECT SYSTEM</a></div></body></html>"

HTML_FEEDBACK = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>SEND SIGNAL</h1><form method='POST'><input type='text' name='code' placeholder='TARGET CODE' required><input type='text' name='customer_name' placeholder='AGENT NAME' required><textarea name='message' placeholder='TRANSMISSION TEXT...' required></textarea><button type='submit'>TRANSMIT</button></form></div></body></html>"

HTML_CAPSULE = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1 style='color:#ff0080;'>TIME CAPSULE</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><textarea name='message' placeholder='MESSAGE FOR FUTURE...' required></textarea><input type='date' name='date' required><button type='submit' style='background:#ff0080;color:#fff;'>LOCK</button></form>{% for c in capsules %}<div class='msg' style='border-left-color:#ff0080;'><b>{{ c.name }}</b> ({{ c.date }}):<br>{{ c.message }}</div>{% endfor %}<a href='/'>BACK</a></div></body></html>"

HTML_PORTAL = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1 style='color:#ff0080;'>MEMORY PORTAL</h1><div class='chat-box'>{% for c in chats %}<div class='chat-msg chat-user'>{{ c.user }}</div><div class='chat-msg chat-ai'>{{ c.ai }}</div>{% endfor %}</div><form method='POST'><input type='text' name='message' placeholder='TALK TO PAST...' required><button type='submit' style='background:#ff0080;color:#fff;'>SEND</button></form><a href='/'>BACK</a></div></body></html>"

@app.route('/')
def index(): return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
if request.method == 'POST':
code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
new_biz = Business(username=request.form['username'], password=generate_password_hash(request.form['password']), name=request.form['name'], industry=request.form['industry'], unique_code=code)
db.session.add(new_biz); db.session.commit()
return f"<h1 style='color:#00ffcc;text-align:center;'>YOUR CODE: {code}</h1>"
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
feedbacks = Feedback.query.all()
return render_template_string(HTML_DASHBOARD, code=current_user.unique_code, feedbacks=feedbacks)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
if request.method == 'POST':
emotion = analyze_emotion(request.form['message'])
db.session.add(Feedback(customer_name=request.form['customer_name'], message=request.form['message'], emotion=emotion)); db.session.commit()
return f"<h1 style='color:#00ffcc;text-align:center;'>SAVED: {emotion}</h1>"
return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
if request.method == 'POST':
db.session.add(TimeCapsule(name=request.form['name'], message=request.form['message'], date=request.form['date'])); db.session.commit()
return redirect(url_for('time_capsule'))
return render_template_string(HTML_CAPSULE, capsules=TimeCapsule.query.all())

@app.route('/memory-portal', methods=['GET', 'POST'])
def memory_portal():
if request.method == 'POST':
if 'chats' not in session: session['chats'] = []
session['chats'].append({'user': request.form['message'], 'ai': aura_brain(request.form['message'])})
session.modified = True
return redirect(url_for('memory_portal'))
return render_template_string(HTML_PORTAL, chats=session.get('chats', []))

with app.app_context(): db.create_all()

if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
