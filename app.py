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
body { font-family: 'Vazirmatn', Tahoma; background: #02040a; color: #00ffcc; text-align: center; padding: 50px; }
.hud-container { background: rgba(2,10,20,0.85); border: 1px solid #00ffcc; padding: 40px; max-width: 600px; margin: auto; }
input, textarea, button { width: 100%; padding: 15px; margin: 10px 0; background: #050505; border: 1px solid #00ffcc; color: #00ffcc; }
button { background: #00ffcc; color: #000; cursor: pointer; font-weight: bold; }
a { color: #ff0080; text-decoration: none; display: block; margin-top: 20px; }
"""

HTML_HOME = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>OMNI-PLATFORM</h1><a href='/login'>ورود کسب‌وکارها</a><a href='/feedback'>ثبت بازخورد</a><a href='/time-capsule'>کپسول زمان</a><a href='/memory-portal'>پورتال خاطرات</a></div></body></html>"
HTML_LOGIN = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>LOGIN</h1><form method='POST'><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>ACCESS</button></form><a href='/register'>REGISTER</a></div></body></html>"
HTML_REGISTER = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>REGISTER</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><input type='text' name='username' placeholder='USERNAME' required><input type='password' name='password' placeholder='PASSWORD' required><button type='submit'>INIT</button></form></div></body></html>"
HTML_DASHBOARD = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>DASHBOARD</h1><h3>CODE: {{ code }}</h3>{% for f in feedbacks %}<div>{{ f.emotion }}: {{ f.message }}</div>{% endfor %}<a href='/logout'>LOGOUT</a></div></body></html>"
HTML_FEEDBACK = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>FEEDBACK</h1><form method='POST'><textarea name='message' placeholder='MESSAGE' required></textarea><button type='submit'>SEND</button></form><a href='/'>BACK</a></div></body></html>"
HTML_CAPSULE = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>TIME CAPSULE</h1><form method='POST'><input type='text' name='name' placeholder='NAME' required><textarea name='message' placeholder='MESSAGE' required></textarea><input type='date' name='date' required><button type='submit'>LOCK</button></form>{% for c in capsules %}<div>{{ c.name }}: {{ c.message }}</div>{% endfor %}<a href='/'>BACK</a></div></body></html>"
HTML_PORTAL = "<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>" + CSS + "</style></head><body><div class='hud-container'><h1>PORTAL</h1>{% for c in chats %}<div>YOU: {{ c.user }}</div><div>AI: {{ c.ai }}</div>{% endfor %}<form method='POST'><input type='text' name='message' placeholder='TALK...' required><button type='submit'>SEND</button></form><a href='/'>BACK</a></div></body></html>"

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
return render_template_string(HTML_DASHBOARD, code=current_user.unique_code, feedbacks=Feedback.query.all())

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
if request.method == 'POST':
emotion = analyze_emotion(request.form['message'])
db.session.add(Feedback(message=request.form['message'], emotion=emotion))
db.session.commit()
return f"<h1>SAVED: {emotion}</h1>"
return HTML_FEEDBACK

@app.route('/time-capsule', methods=['GET', 'POST'])
def time_capsule():
if request.method == 'POST':
db.session.add(TimeCapsule(name=request.form['name'], message=request.form['message'], date=request.form['date']))
db.session.commit()
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

with app.app_context():
db.create_all()

if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
