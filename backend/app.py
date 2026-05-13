from flask import Flask
from config import Config
from database.db import db
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

from routes.productos import productos_bp

app.register_blueprint(productos_bp, url_prefix='/productos')

@app.route('/')
def home():
    return "API de dulceria funcionando"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)