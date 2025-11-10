#!/usr/bin/env python
"""
Script to make a user admin and upgrade to PRO tier.
Run this locally or on Railway to update user privileges.
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:mRQVnJuF44C0dtO-XjVW7yZVvU2OTdQAZ7rk4KJrN4g@localhost:15432/nawwa"
)

def make_user_admin_and_pro(email=None, user_id=None):
    """Make a user admin and upgrade to PRO tier."""

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Build the query based on what's provided
        if email:
            print(f"Looking for user with email: {email}")
            query = sql.SQL("""
                UPDATE users
                SET is_admin = true, subscription_tier = 'PRO'
                WHERE email = %s
                RETURNING id, email, username, is_admin, subscription_tier
            """)
            cursor.execute(query, (email,))
        elif user_id:
            print(f"Looking for user with ID: {user_id}")
            query = sql.SQL("""
                UPDATE users
                SET is_admin = true, subscription_tier = 'PRO'
                WHERE id = %s
                RETURNING id, email, username, is_admin, subscription_tier
            """)
            cursor.execute(query, (user_id,))
        else:
            # If neither provided, update the first user (ID=1)
            print("No email or ID provided, updating first user (ID=1)")
            query = sql.SQL("""
                UPDATE users
                SET is_admin = true, subscription_tier = 'PRO'
                WHERE id = 1
                RETURNING id, email, username, is_admin, subscription_tier
            """)
            cursor.execute(query)

        # Get the result
        result = cursor.fetchone()

        if result:
            conn.commit()
            user_id, email, username, is_admin, tier = result
            print(f"\n[SUCCESS] Successfully updated user!")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            print(f"   Admin: {is_admin}")
            print(f"   Tier: {tier}")
        else:
            print("[ERROR] No user found with the provided criteria")

            # Show existing users
            cursor.execute("SELECT id, email, username, is_admin, subscription_tier FROM users LIMIT 5")
            users = cursor.fetchall()
            if users:
                print("\nExisting users:")
                for u in users:
                    print(f"  ID: {u[0]}, Email: {u[1]}, Username: {u[2]}, Admin: {u[3]}, Tier: {u[4]}")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        # If argument looks like an email
        if "@" in sys.argv[1]:
            make_user_admin_and_pro(email=sys.argv[1])
        # If argument is a number (user ID)
        elif sys.argv[1].isdigit():
            make_user_admin_and_pro(user_id=int(sys.argv[1]))
        else:
            print("Usage: python make_admin.py [email or user_id]")
            print("  Example: python make_admin.py user@example.com")
            print("  Example: python make_admin.py 1")
            sys.exit(1)
    else:
        # No arguments - update user ID 1
        make_user_admin_and_pro()