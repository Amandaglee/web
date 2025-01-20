from flask import Flask
from app import create_app
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/static')
app = create_app(app)
app.config['SECRET_KEY'] = 'your_secret_key'
CORS(app)

# Vercel 需要这个
if __name__ == "__main__":
    app.run()