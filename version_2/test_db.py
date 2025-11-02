# test_insert_user.py
from ijara_kitoblar.database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()

    result = db.add_user(
        library_id="ID0002",
        full_name="Abdulaziz Abdukarimov",
        phone_number="+998900000002",
        telegram_id=987654321
    )

    print("Natija:", result)

if __name__ == "__main__":
    main()
