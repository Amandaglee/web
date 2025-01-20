import os
import sys
import webbrowser
import threading
import time
from flask import Flask
from app import create_app
from flask_cors import CORS

def create_flask_app():
    app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/static')
    app = create_app(app)
    app.config['SECRET_KEY'] = 'your_secret_key'
    CORS(app)
    return app

def open_browser():
    time.sleep(1.5)  # 等待服务器启动
    webbrowser.open('http://localhost:51000')

def main():
    # 设置工作目录
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(application_path)
    
    # 创建 Flask 应用
    app = create_flask_app()
    
    # 启动浏览器线程
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=51000, debug=False)

if __name__ == '__main__':
    main() 