import os
from tqdm import tqdm
import re
from array import array
import ast
from itertools import groupby
import pandas as pd
import numpy as np
import json
from pathlib import Path
import datetime



def check_none(value):
    isna = False
    nan_forms = ['NaN', 'nan', '', ' ', 'NA', None]
    v_type = type(value)
    
    if v_type == list or v_type == dict:
        if not value:
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

# def return_non_na(df, col):
#     return df[~df[col].isna()]

# def make_raw_pages_df(file_path, save_path='', save_file_type='NA', save_increment=-1, lang_prefix='en', start=0, lang_codes=['en', 'nl'], total_lines=-1):
#     count = 0
#     df_list = []
#     batch_list = []
#     error_list = []
#     if total_lines == -1:
#         total_lines = count_lines_with_progress(file_path)
#     if save_increment == -1:
#         save_increment = total_lines
#     with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#         for line in tqdm(f, desc="Loading JSON objects", total=total_lines):
#             if count >= start:
#                 line = f.readline()
#                 line = line.strip()
#                 if not line:
#                     continue
#                 try:
#                     loaded_line = json.loads(line)
#                     loaded_line = safe_eval(loaded_line)
#                     lang_code = loaded_line.get('lang_code', None)
#                     if lang_code:
#                         if lang_code in lang_codes:
#                             batch_list.append(loaded_line)
#                 except json.JSONDecodeError:
#                     error_list.append(line)
#                     continue  # skip malformed lines

#                 if count > 0 and count%save_increment == 0:
#                     df = pd.DataFrame(batch_list)
#                     save_file = "{}/{}_json_pages_{}-{}.{}".format(save_path, lang_prefix, count-save_increment, count, save_file_type)
#                     df_list.append(df)
#                     batch_list.clear()
#                     if save_file_type == 'NA':
#                         continue
#                     elif save_file_type == 'csv':
#                         df.to_csv(save_file)
#                     elif save_file_type == 'pkl':
#                         df.to_pickle(save_file)
#                     else:
#                         df.to_csv(save_file)
                    
#             count = count + 1
#     if len(batch_list) > 0:
#         df = pd.DataFrame(batch_list)
#         df_list.append(df)
#     final_df = pd.concat(df_list, ignore_index=True) 
#     if save_file_type != 'NA':
#         save_file = "{}/{}_json_pages_{}-{}.{}".format(save_path, lang_prefix, start, count, save_file_type)
#         if save_file_type == 'csv':
#             final_df.to_csv(save_file)
#         elif save_file_type == 'pkl':
#             final_df.to_pickle(save_file)
#         else:
#             final_df.to_csv(save_file)
            
#     return final_df, error_list

# def extract_translations(df, lang_code, col_prefix=''):
#     translations_col = []
#     for i, row in df.iterrows():
#         translations = row['translations']
#         has_translation = False
#         for j in translations:
#             if j['lang_code'] == lang_code:
#                 translations_col.append(j)
#                 has_translation = True
#                 continue
#         if has_translation == False:
#             translations_col.append({})
#     new_col_name = "{}{}_translation".format(col_prefix, lang_code)
#     df[new_col_name] = translations
#     return df

# # def check_item_in_col_cell(cell_contents, value, keys_to_val = [], search_all=False):
# #     safe_dict = {'safe_dict': True}
    
# #     contents = safe_eval(cell_contents)
# #     if keys_to_val != []: 
# #         if type(contents) == list:
# #             if list[0] == 'safe_list':
# #                 temp_safe_list = []
# #         if type(contents) == dict:
# #             level = contents
# #             for i in range(len(keys_to_val)):
# #                 key = keys_to_val[i]
# #                 if level:
# #                     if i == len(keys_to_val) - 1:
# #                         level = safe_eval(level)
# #                         if type(level) == list:
# #                             if value in level:
# #                                 return value
                            
# #                     else:
# #                         level = level.get(key)
# #                         if not level and key == keys_to_val[-1]:
# #                             return None
                 
# # def get_nested_dict_val(cell_conents, final_key, prev_keys_to_val=[], search_all=False):
# #     safe_dict = {}
# #     

# def reorder_columns(df, start_cols=['word', 'pos', 'lang_code', 'senses']):
#     cols = df.columns
#     cols = cols.sort_values()
#     cols = start_cols + [i for i in cols if i not in start_cols]
#     df = df.loc[:, cols]
#     return df

# def add_table_id(df, wikt_lang, table_lang, data_source_type='P', alt_id_name=''):
#     words = df['word'].unique()
#     try:
#         words.sort()
#     except:
#         try:
#             words.sort_values()
#         except:
#             print('problem')
#     word_ids = [x for x in range(len(words))]
#     id_name = ''
#     if alt_id_name == '':
#         id_name += wikt_lang[0].upper()
#         id_name += table_lang[0].upper()
#         id_name += data_source_type
#         id_name += '_id'
#     else:
#         id_name = alt_id_name

#     id_df = pd.DataFrame({id_name: word_ids, 'word':words})
#     id_df = id_df.merge(df, how='outer', on='word')
#     return id_df
    
# def add_table_wikt_cols(df, wikt_lang, table_lang, data_source_type='P', alt_source_id_name=''):
#     dsrc = ''
#     if alt_source_id_name == '':
#         dsrc += wikt_lang[0].upper()
#         dsrc += table_lang[0].upper()
#         dsrc += data_source_type
#     else:
#         dscr = alt_source_id_name  
#     df['dsrc'] = dscr
#     return df

# def sort_columns(df, start_cols=['word_id', 'word', 'pos', 'lang_code'], end_cols=['dsrc'], subsort_categories=False, sorted_categories={}, col_end_sort='word'):
#     df_cols = df.columns
#     df_cols = df_cols.sort_values()
#     e_cols = [x for x in end_cols if x in df_cols]
#     s_cols = [x for x in start_cols if x in df_cols]
#     word_id_col = ''
#     if 'word_id' in start_cols and 'word_id' not in df_cols:
#         sub_ids = ['EEP_id', 'ENP_id', 'EER_id', 'ENR_id', 'NEP_id', 'NNP_id', 'NER_id', 'NNR_id']
#         for i in sub_ids:
#             if i in df_cols:
#                 s_cols = [i] + s_cols
#                 word_id_col = i
#     elif 'word_id' in df_cols:
#         word_id_col = 'word_id'
#     reserved_cols = s_cols + e_cols
#     df_cols = [x for x in df_cols if x not in reserved_cols]
#     df_cols.sort()
#     new_cols = s_cols + df_cols + e_cols

#     if subsort_categories == False:
#         new_cols = s_cols + df_cols + e_cols
#         print(new_cols)
#     else:
#         print('not implemented')
#         new_cols = s_cols + df_cols + e_cols
    

#     df = df.loc[:, new_cols]
    
#     if col_end_sort == 'word_id':
#         df = df.sort_values(by=word_id_col)
#     elif col_end_sort == 'word':
#         df = df.sort_values(by='word')

#     return df

# def process_table(df, cols_to_drop=['abbreviations', 'anagrams', 'etymology_number', 'form_of', 'info_templates', 'alt_of', 'wikidata', 'pos_title', 'source', 'wikipedia', 'proverbs', 'lang'], col_vals_to_drop={'pos':['proverb', 'phrase', 'character', 'symbol', 'punct', 'abbrev']}, starting_cols=['word', 'pos', 'lang_code']):
#     print("Shape before: ", df.shape)
#     df = return_non_na(df, 'word')
#     rel_drop_cols = [x for x in cols_to_drop if x in df.columns]
#     has_invalid = []
#     df = df.drop(columns=rel_drop_cols)
#     for k in col_vals_to_drop.keys():
#         if k in df.columns:
#            vals = col_vals_to_drop[k]
#            for v in vals:
#                df = df[df[k] != v]
    
#     for i, row in df.iterrows():
#         w = row['word']
#         is_invalid = check_has_invalid_chars(w)
#         has_invalid.append(is_invalid)
#     df['invalid'] = has_invalid
#     df = df[df['invalid'] != True]
#     df = df.drop(columns=['invalid'])
#     if 'etymology_text' in df.columns:
#         df.rename(columns={'etymology_text': 'etymology_texts'})
#     print("Shape after: ", df.shape)
#     return df

# def full_process_df(csv_path, wikt_lang, table_lang, dscr_type, current_save_path=''):
#     df = pd.read_csv(csv_path, index_col=0)
#     df = process_table(df)
#     df = add_table_wikt_cols(df, wikt_lang, table_lang, dscr_type)
#     df = add_table_id(df, wikt_lang, table_lang, dscr_type)
#     df = sort_columns(df, start_cols=['word_id', 'word', 'pos', 'lang_code'], end_cols=['dsrc'], col_end_sort='word_id')
#     if current_save_path != '':
#         fa = wikt_lang[0].upper()
#         fa = fa + table_lang[0].upper()
#         fa = fa + dscr_type
#         fl = dscr_type.lower()
#         file_name = f"stripped_sorted_{fa}"
#         folder_name = f"{fl}_table_lang" 
#         df.to_csv(Path(current_save_path, wikt_lang, folder_name, file_name))
#     return df

# def make_folder(parent_folder_path, folder_dict):
#     path_list = []
#     if not parent_folder_path.exists():
#         Path.mkdir(parent_folder_path, parents=True, exist_ok=True)
#         path_list.append(parent_folder_path)
#     for k, v in folder_dict.items():
#         Path.mkdir(Path(parent_folder_path, k), parents=True, exist_ok=True)
#         path_list.append(Path(parent_folder_path, k))
#         if type(v) == list:
#             for i in v:
#                 if type(i) == str:
#                     Path.mkdir(Path(parent_folder_path, k, i), parents=True, exist_ok=True)
#                     path_list.append(Path(parent_folder_path, k, i))
#                 elif type(i) == dict:
#                     pl = make_folder(Path(parent_folder_path, k), i)
#                     path_list.append(pl)
#         elif type(v) == dict:    
#             pl = make_folder(Path(parent_folder_path, k), i)
#             path_list.append(pl)
#     return path_list

# def combine_columns_to_list(df, cols=[], combined_col_name='combined', drop_cols=False):
#     df[combined_col_name]= df[cols].apply(
#         lambda row: [x for x in row if pd.notna(x)],
#         axis=1)
#     if drop_cols:
#         df.drop(colums=cols, inplace=True)
#     return df

# def find_len_list_dict_in_col(df, column):
#     df['len'] = df[column].apply(lambda x: len(x) if isinstance(x, (list, dict, np.array)) else None)
#     return df

# def filter_list_dict_in_col_by_len(df, column, filter_function='gt', filter_value=1):
#     """
#     returns a df with rows that have lists/dicts/np.arrays in column that are gt, ge, lt, le, eq, ne filter value
#     """
#     if filter_function == 'gt':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) > filter_value))]
#     elif filter_function == 'ge':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) >= filter_value))]
#     elif filter_function == 'lt':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) < filter_value))]
#     elif filter_function == 'le':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) <= filter_value))]
#     elif filter_function == 'eq':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) == filter_value))]
#     elif filter_function == 'ne':
#         df2 = df[df[column].apply(lambda x: isinstance(x, (list, dict, np.array) and len(x) != filter_value))]
#     return df2


# def summarize_df(df: pd.DataFrame, name: str = None, num_top_values=10, dsrc='EEP') -> pd.DataFrame:
#     """
#     Summarize a DataFrame similar to df.info(), but with:
#       - shape
#       - non-null count
#       - unique count
#       - top 10 value counts (as string)
#     """
#     summary_data = []

#     for col in df.columns:
#         non_null = df[col].notna().sum()
#         unique_vals = df[col].nunique(dropna=True)
#         top_vals = df[col].value_counts(dropna=False).head(num_top_values)
#         top_vals_str = ", ".join(f"{idx}:{val}" for idx, val in top_vals.items())

#         summary_data.append({
#             "dataframe_name": name,
#             'column_number': df.get_loc(col),
#             "column": col,
#             "dtype": str(df[col].dtype),
#             "non_null_count": non_null,
#             "unique_count": unique_vals,
#             "top_10_values": top_vals.values,
#             "top_10_values_str": top_vals_str,
#             "shape_rows": df.shape[0],
#             "shape_cols": df.shape[1],
#         })
#     summary_df = pd.DataFrame(summary_data)
#     summary_df['dsrc'] = dsrc
#     return summary_df


# def log_df_summary(df_log, df, name, notes='', dsrc='', date=datetime.date.today().__format__("%d-%m-%y"), num_top_values=10):
#     """
#     Append a DataFrame summary to an existing log DataFrame.
#     Creates a new one if df_log is None or empty.
#     """
#     summary = summarize_df(df, name, num_top_values, dsrc)
#     if df_log is None or df_log.empty:
#         df_log = summary
#         df_log['notes'] = notes
#         df_log['date'] = date
#         return df_log
#     else:
#         return pd.concat([df_log, summary], ignore_index=True)
    
# def ensure_nested_types(df):
#     """Walk all columns of a DataFrame and fix JSON-type columns."""
#     for col in df.columns:
#         df[col] = df[col].apply(recursively_fix_json_types)
#     return df

# def recursively_fix_json_types(obj):
#     """Ensure nested lists/dicts are proper Python types, not strings."""
#     if isinstance(obj, str):
#         obj = obj.strip()
#         if (obj.startswith("{") and obj.endswith("}")) or (obj.startswith("[") and obj.endswith("]")):
#             try:
#                 obj = json.loads(obj)
#                 return recursively_fix_json_types(obj)
#             except json.JSONDecodeError:
#                 return obj  # leave as string if invalid JSON
#         else:
#             return obj
#     elif isinstance(obj, list):
#         return [recursively_fix_json_types(x) for x in obj]
#     elif isinstance(obj, dict):
#         return {k: recursively_fix_json_types(v) for k, v in obj.items()}
#     else:
#         return obj