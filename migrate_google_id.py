from sqlalchemy import inspect, text
from app import app, db

with app.app_context():

    inspector = inspect(db.engine)

    columns = [column["name"] for column in inspector.get_columns("users")]

    if "google_id" not in columns:

        db.session.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255)"))

        print("Google ID column added successfully.")

    else:
        print("Google ID column already exists.")

    db.session.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id
            ON users (google_id)
        """))

    db.session.commit()

    print("Google ID migration completed successfully.")
