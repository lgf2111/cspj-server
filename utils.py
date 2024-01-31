import socket
from werkzeug.security import generate_password_hash


def find_free_port(start_port, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
            return port
        except OSError:
            pass
    raise RuntimeError("Unable to find a free port.")


def initialize_database(app, db, User):
    with app.app_context():
        db.create_all()

        default_user = User.query.filter_by(username="admin").first()

        if not default_user:
            default_password = generate_password_hash("admin", method="pbkdf2:sha256")
            new_user = User(username="admin", password=default_password)
            db.session.add(new_user)
            db.session.commit()
