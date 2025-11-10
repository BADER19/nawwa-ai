#!/usr/bin/env python
"""
Quick dashboard to check database stats.
Run this anytime to see your users and growth metrics.
"""

import os
import sys
from datetime import datetime, timedelta

# For production on Railway, we need to use the DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Use local database if no production URL
    DATABASE_URL = "postgresql://user:mRQVnJuF44C0dtO-XjVW7yZVvU2OTdQAZ7rk4KJrN4g@localhost:15432/nawwa"
    print("[INFO] Using LOCAL database")
    print("-" * 50)
else:
    print("[INFO] Using PRODUCTION database")
    print("-" * 50)

# Parse the DATABASE_URL to handle both postgresql:// and postgresql+psycopg:// formats
if DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

import psycopg2
from psycopg2 import sql

def show_dashboard():
    """Show dashboard with user statistics."""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # Get users by tier
        cursor.execute("""
            SELECT subscription_tier, COUNT(*)
            FROM users
            GROUP BY subscription_tier
            ORDER BY subscription_tier
        """)
        tier_counts = cursor.fetchall()

        # Get recent signups (last 7 days)
        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE created_at > NOW() - INTERVAL '7 days'
        """)
        recent_signups = cursor.fetchone()[0]

        # Get today's signups
        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE created_at > NOW() - INTERVAL '1 day'
        """)
        today_signups = cursor.fetchone()[0]

        # Get admin count
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true")
        admin_count = cursor.fetchone()[0]

        # Get total usage
        cursor.execute("SELECT SUM(usage_count) FROM users")
        total_usage = cursor.fetchone()[0] or 0

        print("\n" + "="*60)
        print("🚀 NAWWA.AI DASHBOARD")
        print("="*60)

        print(f"\n📊 USER STATISTICS:")
        print(f"   Total Users: {total_users}")
        print(f"   New Today: {today_signups}")
        print(f"   Last 7 Days: {recent_signups}")
        print(f"   Admins: {admin_count}")

        print(f"\n💎 TIER BREAKDOWN:")
        for tier, count in tier_counts:
            percent = (count / total_users * 100) if total_users > 0 else 0
            print(f"   {tier}: {count} users ({percent:.1f}%)")

        print(f"\n📈 USAGE METRICS:")
        print(f"   Total API Calls: {total_usage}")
        avg_usage = total_usage / total_users if total_users > 0 else 0
        print(f"   Average per User: {avg_usage:.1f}")

        # Get most recent users
        cursor.execute("""
            SELECT email, username, subscription_tier, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_users = cursor.fetchall()

        print(f"\n👥 RECENT SIGNUPS:")
        for email, username, tier, created_at in recent_users:
            time_ago = datetime.now() - created_at.replace(tzinfo=None)
            if time_ago.days > 0:
                ago_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                ago_str = f"{time_ago.seconds // 3600}h ago"
            else:
                ago_str = f"{time_ago.seconds // 60}m ago"

            print(f"   • {username or 'No name'} ({email[:20]}...) - {tier} - {ago_str}")

        # Get most active users
        cursor.execute("""
            SELECT email, username, usage_count, subscription_tier
            FROM users
            WHERE usage_count > 0
            ORDER BY usage_count DESC
            LIMIT 5
        """)
        active_users = cursor.fetchall()

        if active_users:
            print(f"\n🔥 MOST ACTIVE USERS:")
            for email, username, usage, tier in active_users:
                print(f"   • {username or email[:15]} - {usage} calls ({tier})")

        print("\n" + "="*60)

        # Show growth rate
        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE created_at > NOW() - INTERVAL '14 days'
            AND created_at <= NOW() - INTERVAL '7 days'
        """)
        last_week = cursor.fetchone()[0]

        if last_week > 0:
            growth_rate = ((recent_signups - last_week) / last_week) * 100
            if growth_rate > 0:
                print(f"📈 Week-over-week growth: +{growth_rate:.1f}%")
            else:
                print(f"📉 Week-over-week growth: {growth_rate:.1f}%")

        print("="*60)

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    show_dashboard()