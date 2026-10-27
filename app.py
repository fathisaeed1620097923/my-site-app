import os
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "<html lang='fa' dir='rtl'><head><meta charset='UTF-8'><style>@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');body{font-family:'Vazirmatn',Tahoma;background:linear-gradient(135deg, #0f0c29, #302b63, #24243e);color:white;text-align:center;padding-top:15%;margin:0;height:100vh;overflow:hidden}.card{background:rgba(255,255,255,0.05);backdrop-filter:blur(15px);padding:50px 40px;border-radius:24px;border:1px solid rgba(255,255,255,0.1);display:inline-block;box-shadow:0 8px 32px 0 rgba(0,0,0,0.37)}h1{font-size:2.5rem;background:linear-gradient(to right, #00f2fe, #4facfe);-webkit-background-clip:text;-webkit-text-fill-color:transparent}p{color:#d1d1d1;font-size:1.1rem;line-height:1.8}</style></head><body><div class='card'><h1>آینده از اینجا شروع می‌شود</h1><p>سلام! این سایت من است.<br>این طراحی با فناوری <b>Glassmorphism</b> تا ده سال آینده هم مدرن است.</p></div></body></html>"
if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
