from contextlib import contextmanager
from pathlib import Path
import sqlite3

# =================================================================================================
# Get a database session
# =================================================================================================
@contextmanager
def get_session():

    # Path to the SQLite3 database file
    database = Path(__file__).resolve().parent / "Bada Bing.db"

    # Get a database connection
    connection = sqlite3.connect(database)

    # Return SQL results as dicts
    connection.row_factory = sqlite3.Row

    # Enforce foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON;")

    # Get a database cursor
    cursor = connection.cursor()

    try:

        # Yield the database cursor
        yield cursor

        # Always commit after the session is completed
        connection.commit()

    # If an unhandled exception occurs
    except Exception:

        # Rollback database changes
        connection.rollback()

    # Always
    finally:

        # Close the database connection
        connection.close()

# =================================================================================================
# Initialize the database
# =================================================================================================
def initialize_database() -> None:

    # Get a database session
    with get_session() as session:

        # Create the status table
        session.execute("""
            CREATE TABLE IF NOT EXISTS status (
                id INTEGER NOT NULL PRIMARY KEY,
                last_start_date_value TEXT NOT NULL,
                last_update_date TEXT NOT NULL
            );
        """)

        # Insert initial status data
        session.execute("""
            INSERT OR IGNORE INTO status (
                id,
                last_start_date_value,
                last_update_date
            )
            VALUES (
                1,
                "0",
                "2000-01-01T00:00:00.000000+00:00"
            );
        """)