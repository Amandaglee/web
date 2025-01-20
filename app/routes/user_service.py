from flask import Blueprint, request, jsonify
from flask import render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from ..DataBase import User, db
from dotenv import load_dotenv
import os
from cozepy import COZE_CN_BASE_URL, Coze, TokenAuth, Message, ChatEventType
import urllib3
import ssl
import socket

# 禁用SSL验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建不验证SSL的HTTPS连接池
http = urllib3.PoolManager(
    cert_reqs='CERT_NONE',
    ssl_version=ssl.PROTOCOL_TLSv1_2,
    retries=urllib3.Retry(3)
)

load_dotenv()  # 加载.env文件

bp = Blueprint('user', __name__, url_prefix='/')

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length
        (min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length
        (min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
            
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length
        (min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length
        (min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')       


@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/function')
def function():
    items = [
    {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
    {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
    {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
]
    return render_template('function.html', items = items)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            bcrypt = Bcrypt()
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user.dashboard'))
    return render_template('login.html', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user.login'))
    
    return render_template('register.html', form=form)

# 设置API的基本URL和Token
coze_api_token = 'pat_hCF457KOPipznDMs4QPf3RmsAGNl6ue43VWSiLpPDjNmR2q5folhXHiuXqPWV1ni'
coze_api_base = 'https://api.coze.cn'  # 直接使用IP地址

# 设置环境变量
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['no_proxy'] = '*'

# 全局禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

# 设置DNS
socket.setdefaulttimeout(30)  # 设置超时时间

# 初始化Coze对象
coze = Coze(
    auth=TokenAuth(token=coze_api_token),
    base_url=coze_api_base
)

# 机器人ID
BOT_ID = '7460833738155474978'

@bp.route('/api/fortune', methods=['POST'])
@login_required
def get_fortune():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '没有收到有效的请求数据'
            }), 400
            
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': '请输入问题'
            }), 400

        try:
            # 生成回复
            response_parts = []
            for event in coze.chat.stream(
                bot_id=BOT_ID,
                user_id=str(request.remote_addr),
                additional_messages=[
                    Message.build_user_question_text(user_message),
                ],
            ):
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    response_parts.append(event.message.content)

                if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                    print("回复生成完成")
                    break

            full_response = "".join(response_parts)
            
            if full_response:
                return jsonify({
                    'status': 'success',
                    'response': full_response
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'AI没有生成回复'
                }), 500

        except Exception as api_error:
            print(f"API调用错误: {str(api_error)}")
            return jsonify({
                'status': 'error',
                'message': f'API调用错误: {str(api_error)}'
            }), 500

    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500