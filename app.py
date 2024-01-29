from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_simple_captcha import CAPTCHA

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"  # Change this to a secret key for session security

SIMPLE_CAPTCHA = CAPTCHA(config={})
app = SIMPLE_CAPTCHA.init_app(app)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Create the database and tables within the application context
with app.app_context():
    db.create_all()

    # Check if the default user exists
    default_user = User.query.filter_by(username="user").first()

    # If the default user doesn't exist, add it
    if not default_user:
        default_password = generate_password_hash("password", method="pbkdf2:sha256")
        new_user = User(username="user", password=default_password)
        db.session.add(new_user)
        db.session.commit()


@app.route("/")
def index():
    new_captcha_dict = SIMPLE_CAPTCHA.create()
    return render_template("login.html", captcha=new_captcha_dict)


@app.route("/login", methods=["POST"])
def login():
    c_hash = request.form.get("captcha-hash")
    c_text = request.form.get("captcha-text")
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        flash("Invalid captcha", "error")
        return redirect(url_for("index"))

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        flash("Login successful", "success")
        return redirect(url_for("index"))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
