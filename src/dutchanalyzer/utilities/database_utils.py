import psycopg
from psycopg import sql
from psycopg.types.json import Json
from dutchanalyzer.config import *
from dutchanalyzer.utilities.util_vars import LANG_CODES_TO_NAMES, POS_INFO
from dutchanalyzer.utilities.json_utils import get_eid_word_pos, count_lines_with_progress
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date, datetime



    

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
                    
def is_public_table(table_name: str, db='cleaning_db') -> bool:
     if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    query = """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = %s
                        );
                    """
                    cur.execute(query, (table_name,))
                    return cur.fetchone()[0]
                                

def get_all_items_from_table(table, db='cleaning_db'):
    load_dotenv()
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_db')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    if is_public_table(table):
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
                
def get_connection():
    try:
        return psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}"
        )
    except:
        return False
    
# Make Database Tables                                
def create_languages_table(db='cleaning_db'):
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS languages (
                            lang_code TEXT PRIMARY KEY,
                            lang text,
                            en_name text,
                            nl_name text        
                            )
                        """)
                    
                    for lang_code, vals in LANG_CODES_TO_NAMES.items():
                        lang = vals['standard']
                        nl_name = vals['nl_name']
                        en_name = vals['en_name']
                        cur.execute(t"INSERT INTO languages (lang_code, lang, en_name, nl_name) VALUES ({lang_code}, {lang}, {en_name}, {nl_name})")

def create_primary_parts_of_speech_table(db='cleaning_db'):
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    cur.execute(""" 
                                CREATE TABLE IF NOT EXISTS primary_parts_of_speech (
                                    pos_code TEXT PRIMARY KEY,
                                    en_name TEXT,
                                    nl_name TEXT,   
                                    nl_abbr TEXT           
                                    )
                                """)
                    for pos_code, vals in POS_INFO.items():
                        nl_name = vals['nl_name']
                        nl_abbr = vals["nl_abbr"]
                        en_name = vals['en_name']
                        cur.execute(t"INSERT INTO primary_parts_of_speech (pos_code, en_name, nl_name, nl_abbr) VALUES ({pos_code}, {en_name}, {nl_name}, {nl_abbr})")

def insert_raw_entry(cur, obj: dict):
    query = """
        INSERT INTO wiktionary_entries (
            word,
            pos,
            lang_code,
            def_lang_code,
            f_code,
            processing_complete,
            original_json,
            dump_date,
            added_on,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    dump_date = date(2025, 1, 10)  
    f_code, word, pos = get_eid_word_pos(obj)
    lang_code = obj.get('lang_code')
    
    if f_code.startswith('E'):
        def_lang_code = 'en'
    else:
        def_lang_code = 'nl'
    
    cur.execute(
        query,
        (
            word,
            pos,
            lang_code,
            def_lang_code,
            f_code,
            bool(obj.get("processing_complete", False)),  
            Json(obj),                                    
            dump_date,
            datetime.now(),
            datetime.now()
        )
    )

def fill_wiktionary_entries_table(file: Path, db='cleaning_db', start_index=0):
    error_lines = []
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    with open(file, 'r', encoding='utf-8') as f:
                        for i, line in tqdm(enumerate(f), desc= f'adding entries from {file.stem}', total=count_lines_with_progress(file, quiet=True)):
                            if i >= start_index:
                                if line:
                                    try:
                                        obj = json.loads(line)
                                        if obj:
                                            insert_raw_entry(cur, obj)
                                    except Exception as e:
                                        error_lines.append((i, e, obj))
    return error_lines

def create_wiktionary_entries_table(db='cleaning_db'):
    if db == 'cleaning_db':
        with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
            with conn.cursor() as cur:
                if cur:
                    cur.execute(""" CREATE TABLE IF NOT EXISTS wiktionary_entries ( 
                                 id bigserial PRIMARY KEY, 
                                word TEXT, 
                                pos TEXT REFERENCES primary_parts_of_speech(pos_code), 
                                lang_code TEXT REFERENCES languages(lang_code), 
                                def_lang_code TEXT REFERENCES languages(lang_code), 
                                f_code TEXT, 
                                processing_complete BOOL DEFAULT False, 
                                original_json JSONB, 
                                dump_date DATE, 
                                added_on TIMESTAMPTZ, 
                                updated_at TIMESTAMPTZ 
                                    )
                                """)      
                    f_files = [ENF_FILE, EEF_FILE, NEF_FILE, NNF_FILE, NOF_FILE, EOF_FILE]
                    for file in f_files:
                        error_lines = fill_wiktionary_entries_table(file)
                        if error_lines: 
                            print(f'Errors in {file.stem}')
                            return file.name, error_lines
                        

def get_entries_where(table, cols='*', clause='WHERE', condition='lang_code', filter_value='en', fetch_type='all'):
    with psycopg.connect(f"dbname={os.getenv('cleaning_database')} user={os.getenv('database_username')} password={os.getenv('database_password')} host={os.getenv('database_host')} port={os.getenv('database_port')}") as conn:
        with conn.cursor() as cur:
            if cur:
                if not is_public_table(table):
                    return []
                
                query = "SELECT {} FROM {} WHERE {}= '{}'".format(cols, table, condition, filter_value)
                result = cur.execute(query)
                if fetch_type == 'all':
                    return result.fetchall()
                elif fetch_type == 'one':
                    return result.fetchone()
                else:
                    print('not implemented')

                return []