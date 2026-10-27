
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# این یک دیتابیس موقت است. در نسخه واقعی از یک دیتابیس ابری استفاده می‌کنید.
messages = []

# قالب HTML به همراه استایل‌های بسیار مدرن
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>کپسول زمان دیجیتال</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma, sans-serif; background: #050505; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: white; }
.orb { position: absolute; width: 400px; height: 400px; background: radial-gradient(circle, rgba(0,242,254,0.15) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; animation: float 6s ease-in-out infinite; z-index: -1; }
.orb-2 { position: absolute; width: 500px; height: 500px; background: radial-gradient(circle, rgba(255,0,128,0.1) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; animation: float 8s ease-in-out infinite reverse; top: -100px; left: -100px; z-index: -1; }
.card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 24px; text-align: center; width: 100%; max-width: 500px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
h1 { font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #00f2fe, #4facfe, #ff0080); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
p.sub { color: #a0a0a0; margin-bottom: 30px; font-size: 0.9rem; }
textarea, input { width: 100%; padding: 15px; margin-bottom: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: white; font-family: inherit; outline: none; transition: 0.3s; }
textarea:focus, input:focus { border-color: #4facfe; background: rgba(255,255,255,0.1); }
button { width: 100%; padding: 15px; background: linear-gradient(90deg, #00f2fe, #4facfe); border: none; border-radius: 12px; color: #000; font-weight: bold; font-size: 1rem; cursor: pointer; transition: 0.3s; }
button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3); }
.msg-box { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin-top: 20px; text-align: right; border-right: 4px solid #4facfe; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-30px); } }
</style>
</head>
<body>
<div class="orb"></div>
<div class="orb-2"></div>
<div class="card">
<h1>کپسول زمان</h1>
<p class="sub">پیام خود را برای آینده قفل کنید.</p>

<form method="POST" action="/add">
<input type="text" name="name" placeholder="نام شما" required>
<textarea name="message" rows="4" placeholder="پیام شما برای آینده..." required></textarea>
<input type="date" name="date" required>
<button type="submit">🔒 قفل کردن در زمان</button>
</form>

{% if messages %}
<div style="margin-top: 30px;">
<h3 style="margin-bottom: 15px;">پیام‌های قفل شده:</h3>
{% for msg in messages %}
<div class="msg-box">
<strong>{{ msg.name }}</strong> در تاریخ <strong>{{ msg.date }}</strong> نوشت:<br>
<span style="color:#ddd;">"{{ msg.message }}"</span>
</div>
{% endfor %}
</div>
{% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def home():
return render_template_string(HTML_TEMPLATE, messages=messages)

@app.route('/add', methods=['POST'])
def add_message():
name = request.form.get('name')
message = request.form['message']
date = request.form['date']
if name and message and date:
messages.append({'name': name, 'message': message, 'date': date})
return redirect(url_for('home'))

if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
