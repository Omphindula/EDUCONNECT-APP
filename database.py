import os
from dotenv import load_dotenv

load_dotenv()

# Try to use MySQL when DB_ENGINE=mysql; otherwise use SQLite fallback
DB_ENGINE = os.getenv('DB_ENGINE', '').lower()

def get_db_connection():
    """Return a DB connection object. For MySQL returns mysql.connector connection; for SQLite returns sqlite3 connection."""
    if DB_ENGINE == 'mysql':
        import mysql.connector
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', ''),
            user=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', '')
        )
        return connection
    else:
        import sqlite3
        db_path = os.path.join(os.getcwd(), os.getenv('SQLITE_DB', 'educonnect.db'))
        connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        # Return row factory for dict-like access similar to mysql.connector.cursor(dictionary=True)
        connection.row_factory = sqlite3.Row
        return connection


def init_database():
    if DB_ENGINE == 'mysql':
        import mysql.connector
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', ''),
            user=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'educonnect')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        # MySQL table creation (original)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'teacher') DEFAULT 'student',
                date_joined DATETIME NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                teacher_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lesson_id INT NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                uploaded_by INT NOT NULL,
                uploaded_at DATETIME NOT NULL,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                user_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                lesson_id INT NOT NULL,
                status ENUM('in-progress', 'completed') DEFAULT 'in-progress',
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                UNIQUE KEY unique_student_lesson (student_id, lesson_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                discussion_id INT NOT NULL,
                user_id INT NOT NULL,
                parent_id INT DEFAULT NULL,
                message TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (discussion_id) REFERENCES discussions(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("MySQL database initialized successfully!")
    """Initialize the database with required tables for the selected engine (MySQL or SQLite)."""
    if DB_ENGINE == 'mysql':
        import mysql.connector
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', ''),
            user=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'educonnect')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        # MySQL table creation (original)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'teacher') DEFAULT 'student',
                date_joined DATETIME NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                teacher_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lesson_id INT NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                uploaded_by INT NOT NULL,
                uploaded_at DATETIME NOT NULL,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                user_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                lesson_id INT NOT NULL,
                status ENUM('in-progress', 'completed') DEFAULT 'in-progress',
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                UNIQUE KEY unique_student_lesson (student_id, lesson_id)
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("MySQL database initialized successfully!")

    else:
        import sqlite3
        db_path = os.path.join(os.getcwd(), os.getenv('SQLITE_DB', 'educonnect.db'))
        connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()

        # SQLite doesn't support ENUM, AUTO_INCREMENT, or foreign key behaviours in the same way.
        # Create tables with compatible types and enable foreign keys.
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                date_joined DATETIME NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_by INTEGER NOT NULL,
                uploaded_at DATETIME NOT NULL,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                message TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                status TEXT DEFAULT 'in-progress',
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                UNIQUE (student_id, lesson_id)
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print(f"SQLite database initialized at {db_path}")


if __name__ == '__main__':
    init_database()
