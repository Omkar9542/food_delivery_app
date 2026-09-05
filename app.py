from flask import Flask
from models import db, User, Restaurant, MenuItem
from flask_login import LoginManager
from routes import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_delivery.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(main)

with app.app_context():
    db.create_all()
    if not Restaurant.query.first():
        r1 = Restaurant(name='Pizza Palace', cuisine='Italian')
        r2 = Restaurant(name='Burger Hub', cuisine='Fast Food')
        db.session.add_all([r1, r2])
        db.session.commit()
        
        m1 = MenuItem(name='Margherita Pizza', price=9.99, restaurant_id=r1.id)
        m2 = MenuItem(name='Cheese Burger', price=5.49, restaurant_id=r2.id)
        db.session.add_all([m1, m2])
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
