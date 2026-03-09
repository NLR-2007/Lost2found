import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "lost2found")

def init_db():
    print(f"Connecting to MySQL at {DB_HOST} as {DB_USER}...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create database
        print(f"Creating database {DB_NAME}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # Create users table
        print("Creating users table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create lost_items table
        print("Creating lost_items table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255) NOT NULL,
            image VARCHAR(255),
            mobile VARCHAR(15),
            college_id VARCHAR(50),
            status ENUM('open', 'matched', 'recovered') DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recovered_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # Create found_items table
        print("Creating found_items table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255) NOT NULL,
            image VARCHAR(255),
            mobile VARCHAR(15),
            college_id VARCHAR(50),
            status ENUM('open', 'matched', 'recovered') DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recovered_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # Create matches table
        print("Creating matches table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lost_id INT NOT NULL,
            found_id INT NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lost_id) REFERENCES lost_items(id) ON DELETE CASCADE,
            FOREIGN KEY (found_id) REFERENCES found_items(id) ON DELETE CASCADE
        )
        """)

        # Seed admin user (Admin 1)
        print("Seeding admin user (Admin1)...")
        admin_email = "Admin@l2f.com"
        admin_pass = "boss@123"
        hashed_pass = generate_password_hash(admin_pass)

        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s)", (admin_email,))
        admin_exists = cursor.fetchone()

        if not admin_exists:
            cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """, ("Admin", admin_email, hashed_pass, "admin"))
            print("Admin1 user seeded successfully.")
        else:
            print("Admin1 user already exists.")

        # Seed admin user (Admin 2)
        print("Seeding admin user (Admin2)...")
        admin2_email = "Admin2@l2f.com"
        admin2_pass = "krsna@1234"
        hashed_pass2 = generate_password_hash(admin2_pass)

        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s)", (admin2_email,))
        admin2_exists = cursor.fetchone()

        if not admin2_exists:
            cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """, ("Admin2", admin2_email, hashed_pass2, "admin"))
            print("Admin2 user seeded successfully.")
        else:
            print("Admin2 user already exists.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialization successful!")
    
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
