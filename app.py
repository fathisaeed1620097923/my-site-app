import os
from flask import Flask, request, redirect, url_for
app = Flask(__name__)
messages = []
HTML = """<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><style>@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');body{font-family:'Vazirmatn',Tahoma;background:#050505;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;color:white;margin:0}.card{background:rgba(255,255,255,0.03);backdrop-filter:blur(20px);padding:40px;border-radius:24px;width:100%;max-width:500px;box-shadow:0 20px 50px rgba(0,0,0,0.5)}h1{font-size:2rem;background:linear-gradient(90deg,#00f2fe,#4facfe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center}input,textarea{width:100%;padding:15px;margin-bottom:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;color:white;box-sizing:border-box}button{width:100%;padding:15px;background:linear-gradient(90deg,#00f2fe,#4facfe);border:none;border-radius:12px;font-weight:bold;cursor:pointer}.msg{background:rgba(255,255,255,0.05);padding:15px;border-radius:12px;margin-top:10px;border-right:4px solid #4facfe}</style></head><body><div class="card"><h1>کپسول زمان</h1><form method="POST" action="/add"><input type="text" name="name" placeholder="نام شما" required><textarea name="message" placeholder="پیام شما..." required></textarea><input type="date" name="date" required><button type="submit">🔒 قفل کردن</button></form>"""
HTML_END = """</div></body></html>"""
@app.route('/')
def home(): return HTML + "".join([f'<div class="msg"><b>{m["name"]}</b> ({m["date"]}):<br>{m["message"]}</div>' for m in messages]) + HTML_END
@app.route('/add', methods=['POST'])
def add(): messages.append({'name': request.form['name'], 'message': request.form['message'], 'date': request.form['date']}); return redirect(url_for('home'))
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
