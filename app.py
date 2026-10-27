from flask import Flask
app = Flask(__name__)
html_code = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>آینده</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Vazirmatn', Tahoma, sans-serif; background: #050505; height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; color: white; }
.orb { position: absolute; width: 400px; height: 400px; background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; animation: float 6s ease-in-out infinite; }
.orb-2 { position: absolute; width: 500px; height: 500px; background: radial-gradient(circle, rgba(255,0,128,0.15) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; animation: float 8s ease-in-out infinite reverse; top: -100px; left: -100px; }
.card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); padding: 60px 40px; border-radius: 30px; text-align: center; z-index: 10; box-shadow: 0 20px 50px rgba(0,0,0,0.5); animation: fadeIn 1.5s ease-out; }
h1 { font-size: 3rem; font-weight: 700; background: linear-gradient(90deg, #00f2fe, #4facfe, #ff0080); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; animation: shine 3s infinite linear; background-size: 200% auto; }
p { font-size: 1.2rem; color: #a0a0a0; line-height: 2; font-weight: 300; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-30px); } }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
@keyframes shine { to { background-position: 200% center; } }
</style>
</head>
<body>
<div class="orb"></div>
<div class="orb-2"></div>
<div class="card">
<h1>آینده از اینجا شروع می‌شود</h1>
<p>من این وب‌سایت را در سال ۲۰۲۶ ساختم.<br>این طراحی با فناوری <b>Glassmorphism</b> و افکت‌های نوری، تا ده سال آینده هم نوآورانه و خاص باقی خواهد ماند.</p>
</div>
</body>
</html>
"""
@app.route('/')
def home(): return html_code
if __name__ == '__main__': app.run(debug=True)