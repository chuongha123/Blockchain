import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Get database connection parameters
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "FormosVN@123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "farmdb")

try:
    # Connect without specifying a database
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=int(DB_PORT)
    )
    
    with connection.cursor() as cursor:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' created or already exists")
        
        # Use the database
        cursor.execute(f"USE {DB_NAME}")
        
        # Create tables if needed
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            username VARCHAR(50) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        print("Users table created or already exists")
        
        # Check if role column exists, if not add it
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        role_exists = cursor.fetchone()
        if not role_exists:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'")
            print("Added 'role' column to users table")
        else:
            print("'role' column already exists in users table")
    
    connection.commit()
    connection.close()
    print("Database setup completed successfully")
    
except Exception as e:
    print(f"Error setting up database: {e}")
    
print("\nIf you're running locally, make sure MySQL is installed and running.")
print("If you're using Docker, run 'docker-compose up -d db' first.") 