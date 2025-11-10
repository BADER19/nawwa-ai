#!/usr/bin/env python
"""
Script to list all users in the database.
This will help identify your user ID and current status.
"""

import os
import sys

# For production on Railway, we need to use the DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Use local database if no production URL
    DATABASE_URL = "postgresql://user:mRQVnJuF44C0dtO-XjVW7yZVvU2OTdQAZ7rk4KJrN4g@localhost:15432/nawwa"
    print("[INFO] Using local database")
else:
    print("[INFO] Using production database")

# Parse the DATABASE_URL to handle both postgresql:// and postgresql+psycopg:// formats
if DATABASE_URL.startswith("postgresql+psycopg://"):
    # Convert to standard psycopg2 format
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

import psycopg2
from psycopg2 import sql

def list_all_users():
    """List all users in the database."""

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get all users
        cursor.execute("""
            SELECT id, email, username, is_admin, subscription_tier, created_at, usage_count
            FROM users
            ORDER BY id
        """)

        users = cursor.fetchall()

        if users:
            print("\n" + "="*80)
            print("ALL USERS IN DATABASE:")
            print("="*80)
            for user in users:
                user_id, email, username, is_admin, tier, created_at, usage_count = user
                admin_status = "ADMIN" if is_admin else "User"
                print(f"\nID: {user_id}")
                print(f"  Email: {email}")
                print(f"  Username: {username}")
                print(f"  Status: {admin_status}")
                print(f"  Tier: {tier}")
                print(f"  Created: {created_at}")
                print(f"  Usage Count: {usage_count}")
                print("-" * 40)
        else:
            print("\nNo users found in database")

        # Also show summary
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true")
        admins = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_tier = 'PRO'")
        pro_users = cursor.fetchone()[0]

        print(f"\nSUMMARY:")
        print(f"  Total Users: {total}")
        print(f"  Admins: {admins}")
        print(f"  PRO Users: {pro_users}")
        print("="*80)

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_all_users()