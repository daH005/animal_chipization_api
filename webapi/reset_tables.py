from webapi.__init__ import db, app, configure_app_and_db

configure_app_and_db()
db.drop_all()
db.create_all()
