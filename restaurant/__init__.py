from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_admin import AdminIndexView
from flask_admin import expose, AdminIndexView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/restaurant'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Jeevansaimakam:Cube12345@Jeevansaimakam.mysql.pythonanywhere-services.com:3306/Jeevansaimakam$restaurant'
app.config['SECRET_KEY'] = '1b1bdc96eb8dba64b0fc5ae1'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page" #type: ignore

from restaurant import routes
from restaurant.models import *


class ItemAdminView(ModelView):
    column_exclude_list = ['orderer']

class UserAdminView(ModelView):
    column_exclude_list = ['password_hash']


class DashboardView(AdminIndexView):
    
    @expose('/')
    def index(self):
        data = db.session.execute(db.select(WorkerShifts)).scalars() #type: ignore
        return self.render(
            template='admin/index.html',
            data = list(data)
        )

admin = Admin(app, name='Restaurant Management', template_mode='bootstrap4', index_view=DashboardView())


admin.add_view(UserAdminView(User, db.session)) #type: ignore
admin.add_view(ModelView(Table, db.session)) #type: ignore
admin.add_view(ItemAdminView(Item, db.session)) #type: ignore
admin.add_view(ModelView(Order, db.session)) #type: ignore
admin.add_view(ModelView(WorkerShifts, db.session)) #type: ignore

with app.app_context():
    db.create_all() #type: ignore

babel = Babel(app)

@app.template_filter()
def return_order_name(value,dish):
    print(value)
    print(Order.query.filter_by(name = value, order_items=dish).all())
    for i in Order.query.filter_by(name = value).all():
        print(i.order_items)
        if dish in i.order_items:
            return i.name