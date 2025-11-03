import os
from tqdm import tqdm
import re
from array import array
import ast
from itertools import groupby
import pandas as pd
import numpy as np
import json

def count_lines_with_progress(file_path, chunk_size=1024 * 1024):
    total_size = os.path.getsize(file_path)
    lines = 0
    with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
        while chunk := f.read(chunk_size):
            lines += chunk.count(b'\n')
            pbar.update(len(chunk))
    return lines

def check_has_invalid_chars(text):
    allowed_chars = (
        "a-zA-Z"                   # Standard letters
        "áéíóúÁÉÍÓÚ"               # Acute accents
        "èàòùÈÀÒÙ"                 # Grave accents
        "ëïöüËÏÖÜ"                 # Diaeresis
        "'\\- "                     # Apostrophe, hyphen, space
        "0-9"                       # Digits
        "\\.,;:"                  # Common punctuation
    )
    try: 
        text = str(text)
        text = text.strip()
        invalid_char_pattern = re.compile(f"[^{allowed_chars}]")
        return bool(invalid_char_pattern.search(text))
    except: 
        return False
    
def check_none(value):
    isna = False
    nan_forms = ['NaN', 'nan', '', ' ', 'NA', None]
    v_type = type(value)
    if v_type == list or v_type == dict:
        return False
    if v_type == str:
        if value == 'NaN':
            isna = True 
        if value == '':
            isna = True
        if value == 'na':
            isna = True
    if v_type == None:
        isna = True
    if pd.isna(value):
        isna = True
    if v_type == pd.NA:
        isna = True
    if v_type == np.nan:
        isna = True
    return isna


def safe_eval(x):
    if check_none(x):
        return []
    elif type(x) == np.array:
        x = x.to_list()
        return x           # or return None depending on desired behaviour
    elif type(x) == array:
        x = [i for i in x]
        return x
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except Exception:
            return []        # fallback
    return x

def return_non_na(df, col):
    return df[~df[col].isna()]

def make_raw_pages_df(file_path, save_path='', save_file_type='NA', save_increment=-1, lang_prefix='en', start=0, lang_codes=['en', 'nl'], total_lines=-1):
    count = 0
    df_list = []
    batch_list = []
    error_list = []
    if total_lines == -1:
        total_lines = count_lines_with_progress(file_path)
    if save_increment == -1:
        save_increment = total_lines
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in tqdm(f, desc="Loading JSON objects", total=total_lines):
            if count >= start:
                line = f.readline()
                line = line.strip()
                if not line:
                    continue
                try:
                    loaded_line = json.loads(line)
                    loaded_line = safe_eval(loaded_line)
                    lang_code = loaded_line.get('lang_code', None)
                    if lang_code:
                        if lang_code in lang_codes:
                            batch_list.append(loaded_line)
                except json.JSONDecodeError:
                    error_list.append(line)
                    continue  # skip malformed lines

                if count > 0 and count%save_increment == 0:
                    df = pd.DataFrame(batch_list)
                    save_file = "{}/{}_json_pages_{}-{}.{}".format(save_path, lang_prefix, count-save_increment, count, save_file_type)
                    df_list.append(df)
                    batch_list.clear()
                    if save_file_type == 'NA':
                        continue
                    elif save_file_type == 'csv':
                        df.to_csv(save_file)
                    elif save_file_type == 'pkl':
                        df.to_pickle(save_file)
                    else:
                        df.to_csv(save_file)
                    
            count = count + 1
    if len(batch_list) > 0:
        df = pd.DataFrame(batch_list)
        df_list.append(df)
    final_df = pd.concat(df_list, ignore_index=True) 
    if save_file_type != 'NA':
        save_file = "{}/{}_json_pages_{}-{}.{}".format(save_path, lang_prefix, start, count, save_file_type)
        if save_file_type == 'csv':
            final_df.to_csv(save_file)
        elif save_file_type == 'pkl':
            final_df.to_pickle(save_file)
        else:
            final_df.to_csv(save_file)
            
    return final_df, error_list

def extract_translations(df, lang_code, col_prefix=''):
    translations_col = []
    for i, row in df.iterrows():
        translations = row['translations']
        has_translation = False
        for j in translations:
            if j['lang_code'] == lang_code:
                translations_col.append(j)
                has_translation = True
                continue
        if has_translation == False:
            translations_col.append({})
    new_col_name = "{}{}_translation".format(col_prefix, lang_code)
    df[new_col_name] = translations
    return df

# def check_item_in_col_cell(cell_contents, value, keys_to_val = [], search_all=False):
#     safe_dict = {'safe_dict': True}
    
#     contents = safe_eval(cell_contents)
#     if keys_to_val != []: 
#         if type(contents) == list:
#             if list[0] == 'safe_list':
#                 temp_safe_list = []
#         if type(contents) == dict:
#             level = contents
#             for i in range(len(keys_to_val)):
#                 key = keys_to_val[i]
#                 if level:
#                     if i == len(keys_to_val) - 1:
#                         level = safe_eval(level)
#                         if type(level) == list:
#                             if value in level:
#                                 return value
                            
#                     else:
#                         level = level.get(key)
#                         if not level and key == keys_to_val[-1]:
#                             return None
                 
# def get_nested_dict_val(cell_conents, final_key, prev_keys_to_val=[], search_all=False):
#     safe_dict = {}
#     

def reorder_columns(df, start_cols=['word', 'pos', 'lang_code', 'senses']):
    cols = df.columns
    cols = cols.sort_values()
    cols = start_cols + [i for i in cols if i not in start_cols]
    df = df.loc[:, cols]
    return df