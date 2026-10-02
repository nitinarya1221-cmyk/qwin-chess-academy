from app import app, db, User

with app.app_context():

    users = User.query.all()

    for user in users:
        print("ID:", user.id)
        print("Name:", user.name)
        print("Email:", user.email)
        print("Phone:", user.phone)
        print("Password Hash:", user.password_hash)
        print("-------------------------")