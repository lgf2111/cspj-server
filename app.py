from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_simple_captcha import CAPTCHA
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"  # Change this to a secret key for session security

SIMPLE_CAPTCHA = CAPTCHA(config={})
app = SIMPLE_CAPTCHA.init_app(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


with app.app_context():
    db.create_all()

    default_user = User.query.filter_by(username="admin").first()

    if not default_user:
        default_password = generate_password_hash("admin", method="pbkdf2:sha256")
        new_user = User(username="admin", password=default_password)
        db.session.add(new_user)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    new_captcha_dict = SIMPLE_CAPTCHA.create()
    return render_template("login.html", captcha=new_captcha_dict)


@app.route("/login", methods=["POST"])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    c_hash = request.form.get("captcha-hash")
    c_text = request.form.get("captcha-text")

    # Comment this do demonstrate the test case
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        flash("Invalid captcha", "error")
        return redirect(url_for("login"))

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("index"))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=8080)
