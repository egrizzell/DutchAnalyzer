import psycopg
from psycopg import sql
from dutchanalyzer.config import *
from dutchanalyzer.utilities.util_vars import LANG_CODES_TO_NAMES
import os
from pathlib import Path
from dotenv import load_dotenv


def get_all_items_from_table(table, db='cleaning_db'):
    load_dotenv()
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_db')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    items = cur.execute(t"SELECT * FROM  {table:i}")
                    return items.fetchall()

def get_table_col_schemas_in_db(db='cleaning_db'):
   if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    db_schema = {}

                    rows = cur.execute("""
                        SELECT 
                            table_schema,
                            table_name,
                            column_name,
                            data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        ORDER BY table_schema, table_name, ordinal_position;
                        """)
                    # Print results nicely
                    for schema, table, column, dtype in rows:
                        if table not in db_schema:
                            db_schema[table] = {column:dtype}
                        else:
                            db_schema[table][column] = dtype
        
                    return db_schema
    
def table_exists(table):
    with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                   
                    query = """ SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_name = '{}'
                        ) AS table_existence; """.format(table)
                    try:
                        result = cur.execute(query).fetchall()[0][0]  
                        return result
                    except:
                         return False
                    
                
def create_languages_table(db='cleaning_db'):
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS languages (
                            lang_code TEXT PRIMARY KEY,
                            lang text,
                            dutch_name text,        
                            english_name text
                            )
                        """)
                    
                    for lang_code, vals in LANG_CODES_TO_NAMES.items():
                        lang = vals['standard']
                        dutch_name = vals['nl_name']
                        english_name = vals['en_name']
                        cur.execute(t"INSERT INTO languages (lang_code, lang, dutch_name, english_name) VALUES ({lang_code}, {lang}, {dutch_name}, {english_name})")