"""
Database initialization script.

Run this script to initialize the database schema:
    python -m src.core.init_db
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import init_db, drop_db
from src.domain.models import Base


def main():
    print("=" * 50)
    print("[Database Initialization]")
    print("=" * 50)

    # Initialize database
    print("\n>>> Creating tables...")
    init_db()
    print("✓ Database initialized successfully!")

    print("\nAvailable tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    print("\n>>> Database is ready for use.")


if __name__ == "__main__":
    main()
