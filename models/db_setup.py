import psycopg2
import os

def get_connection():
    try:
        return psycopg2.connect(
            database=os.getenv('cleaning_database'),
            user=os.getenv('database_username'),
            password=os.getenv('database_password'),
            host=os.getenv('database_host'),
            port=os.getenv('database_port'),
        )
    except:
        return False
    
def make_tables():
    pass


if __name__ == '__main__':
    conn = get_connection()
    if conn:
        print("Connection to the PostgreSQL established successfully.")
    else:
        print("Connection to the PostgreSQL encountered and error.")

    cursor = conn.cursor()

    conn.commit()
    cursor.close()
    conn.close()