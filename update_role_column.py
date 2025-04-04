import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Get database connection parameters
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "farmdb")

try:
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=int(DB_PORT),
        database=DB_NAME
    )
    
    with connection.cursor() as cursor:
        # Check if role column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        role_column = cursor.fetchone()
        
        if not role_column:
            print("Adding 'role' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'")
            print("✅ Column 'role' added successfully")
        else:
            print("✅ Column 'role' already exists in users table")
        
        # Set first user as admin if there are users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            # Update the first user to be admin
            cursor.execute("UPDATE users SET role = 'admin' WHERE id = 1")
            print("✅ Updated user with ID 1 to have admin role")
        
        # Print users table structure for verification
        cursor.execute("DESCRIBE users")
        table_structure = cursor.fetchall()
        print("\n--- Users Table Structure ---")
        for column in table_structure:
            print(f"- {column[0]}: {column[1]} (Default: {column[4]})")
    
    connection.commit()
    connection.close()
    print("\n✅ Database update completed successfully")
    
except Exception as e:
    print(f"❌ Error updating database: {e}") 