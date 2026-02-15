from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# إعداد Z.ai (ضع مفتاحك هنا)
ZAI_API_KEY = "996605e61ee449a1adc5f4521d2282fe.HPJ8VTiq1xbRxXdP"
client = openai.OpenAI(api_key=ZAI_API_KEY, base_url="https://open.bigmodel.cn/api/paas/v4/")

# جداول قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

with app.app_context():
    db.create_all()

# --- المسارات (Routes) ---

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = generate_password_hash(request.form.get('password'))
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.form.get('email')).first()
    if user and check_password_hash(user.password, request.form.get('password')):
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return "خطأ في البيانات"

@app.route('/ai_process', methods=['POST'])
def ai_process():
    prompt = request.json.get('prompt')
    user_id = session.get('user_id')
    
    # التعليمات البرمجية لجعل الذكاء الاصطناعي "قوي جداً"
    instruction = "أنت مهندس برمجيات ومصمم برزنتيشن محترف. إذا طلب المستخدم موقعاً، أعطه كود HTML/CSS كامل داخل وسوم الكود. إذا طلب برزنتيشن، أعطه شرائح مفصلة."
    
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
    )
    
    ai_result = response.choices[0].message.content
    
    # حفظ المنشأة في قاعدة البيانات
    new_project = Project(title=prompt[:30], content=ai_result, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({"result": ai_result})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  
