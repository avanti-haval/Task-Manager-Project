import sqlite3

def create_database():
    conn = sqlite3.connect('tasks_projects.db')
    c = conn.cursor()

    # Create the table
    c.execute('''CREATE TABLE IF NOT EXISTS tbl_users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username VARCHAR(255) NOT NULL,
              email VARCHAR(255),
              join_date INTEGER,
              password VARCHAR(255) NOT NULL)''')

    # Create tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 category TEXT NOT NULL,
                 description TEXT NOT NULL,
                 start_date TEXT NOT NULL,
                 end_date TEXT NOT NULL,
                 completed INTEGER DEFAULT 0,
                 username VARCHAR(255) NOT NULL)''')

    # Create projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 task_name TEXT NOT NULL,
                 task_category TEXT NOT NULL,
                 task_description TEXT NOT NULL,
                 start_date TEXT NOT NULL,
                 end_date TEXT NOT NULL,
                 completed INTEGER DEFAULT 0,
                 username VARCHAR(255) NOT NULL)''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()

print("Database and table created successfully!")
