import csv
import uuid

from app import app
from models import db, User, Trade

CSV_FILE = "data/trades.csv"
USER_EMAIL = "samuelmutisya2001@gmail.com"


def migrate_trades():

    with app.app_context():

        user = db.session.execute(
            db.select(User).filter_by(email=USER_EMAIL)
        ).scalar_one_or_none()

        if user is None:
            raise ValueError("Target account was not found.")

        existing_count = Trade.query.filter_by(user_id=user.id).count()

        if existing_count:
            raise ValueError("This account already has trades. Migration stopped.")

        with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames or "Trade ID" not in reader.fieldnames:
                raise ValueError("Invalid CSV headers.")

            rows = list(reader)

        if not rows:
            print("No trades found in the CSV.")
            return

        imported_ids = set()
        new_records = []

        for row in rows:

            trade_id = row.get("Trade ID", "").strip()

            if not trade_id:
                trade_id = uuid.uuid4().hex

            if trade_id in imported_ids:
                raise ValueError(f"Duplicate Trade ID in CSV: {trade_id}")

            if db.session.get(Trade, trade_id) is not None:
                raise ValueError(f"Trade ID already exists: {trade_id}")

            imported_ids.add(trade_id)

            trade_data = row.copy()
            trade_data.pop("Trade ID", None)

            new_records.append(
                Trade(
                    id=trade_id,
                    user_id=user.id,
                    trade_data=trade_data,
                )
            )

        try:
            db.session.add_all(new_records)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        print("Migration completed successfully!")
        print("Account:", user.email)
        print("Imported trades:", len(new_records))


if __name__ == "__main__":
    migrate_trades()
