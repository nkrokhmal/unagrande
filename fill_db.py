import os
import inspect
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_script import Manager
from flask_admin.contrib.sqla import ModelView

os.environ['environment'] = 'flask_app'

from app import create_app
import app.models as umalat_models

app, db = create_app()
manager = Manager(app)
migrate = Migrate(app, db, render_as_batch=True)
manager.add_command('db', MigrateCommand)

admin = Admin(app, name='Umalat admin', template_mode='bootstrap3')
for name, obj in inspect.getmembers(umalat_models):
    if inspect.isclass(obj):
        admin.add_view(ModelView(obj, db.session))

if __name__ == '__main__':
    # from app.fill_db import fill_db
    # with app.app_context():
    #     fill_db()
    from app.models.fill_db.default_data import generate_all
    from app.models.fill_db.fill_mozzarella import fill_db as mozzarella_fill_db
    from app.models.fill_db.fill_ricotta import fill_db as ricotta_fill_db
    with app.app_context():
        generate_all()
        mozzarella_fill_db()
        ricotta_fill_db()