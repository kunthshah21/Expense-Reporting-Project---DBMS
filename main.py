from app.db import initialize_db
from app.cli import main_cli

if __name__ == "__main__":
    initialize_db()
    print("Database initialized")
    main_cli()