from dutchanalyzer.config import *
import pandas as pd
import datetime
from pathlib import Path
from dutchanalyzer.utilities.utils import *
from dutchanalyzer.utilities.json_utils import *
# Pandas Utils

def summarize_df(df: pd.DataFrame, name: str = None, num_top_values=10, dsrc='EEP') -> pd.DataFrame:
    """
    Summarize a DataFrame similar to df.info(), but with:
      - shape
      - non-null count
      - unique count
      - top 10 value counts (as string)
    """
    summary_data = []

    for col in df.columns:
        non_null = df[col].notna().sum()
        unique_vals = df[col].nunique(dropna=True)
        top_vals = df[col].value_counts(dropna=False).head(num_top_values)
        top_vals_str = ", ".join(f"{idx}:{val}" for idx, val in top_vals.items())

        summary_data.append({
            "dataframe_name": name,
            'column_number': df.get_loc(col),
            "column": col,
            "dtype": str(df[col].dtype),
            "non_null_count": non_null,
            "unique_count": unique_vals,
            "top_10_values": top_vals.values,
            "top_10_values_str": top_vals_str,
            "shape_rows": df.shape[0],
            "shape_cols": df.shape[1],
        })
    summary_df = pd.DataFrame(summary_data)
    summary_df['dsrc'] = dsrc
    return summary_df


def log_df_summary(df_log, df, name, notes='', dsrc='', date=datetime.date.today().__format__("%d-%m-%y"), num_top_values=10):
    """
    Append a DataFrame summary to an existing log DataFrame.
    Creates a new one if df_log is None or empty.
    """
    summary = summarize_df(df, name, num_top_values, dsrc)
    if df_log is None or df_log.empty:
        df_log = summary
        df_log['notes'] = notes
        df_log['date'] = date
        return df_log
    else:
        return pd.concat([df_log, summary], ignore_index=True)

def get_equal_definitions(df):
    return df[df['word'] == df['gloss']]

def get_duplicate_words(df, filter_by=['word', 'pos', 'gloss']):
    # repeated = (
    # df.groupby(['word', 'pos', 'gloss'])
    # .filter(lambda g: len(g) > 1)
    # .groupby(['word', 'pos', 'gloss'], as_index=False)
    # .agg({'gloss': list})
    #         )
    # duplicates = duplicates[duplicates['pos'] > 1]
    duplicates = df[df.duplicated(subset=filter_by, keep=False)]
    return duplicates


def get_translations_list(tlist: list):
    new_t_list = []
    if tlist:
        for tl in tlist:
            if type(tl) == dict:
                if tl.get('word'):
                    new_t_list.append(tl)
                else:
                    tl.get('sense')
    return new_t_list

def return_non_na(df, col):
    return df[~df[col].isna()]

def replace_letters_in_word(word, original_letters, replace_with, na_return=''):
    if len(word) < len(original_letters):
        return na_return
    index = word.find(original_letters)
    if index != -1:
        word = word.replace(original_letters, replace_with)
        return word
    return na_return

def replace_beginning_letters(word, original_prefix, replace_with, na_return=''):
    if len(word) < len(original_prefix):
        return na_return
    
    if word.beginswith(original_prefix):
        word = replace_with + word[len(original_prefix):]
        return word
    return na_return

def replace_end_letters(word, original_suffix, replace_with, na_return=''):
    if len(word) < len(original_suffix):
        return na_return
    if word.endswith(original_suffix):
        word = word[0:-len(original_suffix)] + replace_with
        return word
    return na_return

def apply_test_no_context(df, check_df, test_num, test_description, original_letters, replace_with, replace_function='middle', na_val='', with_pos_check=False):
    df[f'test{test_num}'] = test_description
    if replace_function == 'begin':
        if not na_val == 'word':
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_beginning_letters(x, original_letters, replace_with, na_val))
        else:
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_beginning_letters(x, original_letters, replace_with, x))
    if replace_function == 'end':
        if not na_val == 'word':
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_end_letters(x, original_letters, replace_with, na_val))
        else:
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_end_letters(x, original_letters, replace_with, x))
    if replace_function == 'middle':
        if not na_val == 'word':
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_letters_in_word(x, original_letters, replace_with, na_val))
        else:
            df[f'word{test_num}'] = df['word'].apply(lambda x: replace_letters_in_word(x, original_letters, replace_with, x))
    if with_pos_check:
        df['temp_col'] = df[f'word{test_num}'] + '_' + df['pos']
        df[f'result{test_num}'] = df['temp_col'].isin(check_df['word_code'])
        df.drop(columns=['temp_col'], inplace=True)
    else:
        df[f'result{test_num}'] = df[f'word{test_num}'].isin(check_df['word'])
    return df

def display_results_overview(df, check_changed=True):
    test_indexes = []
    word_indexes = []
    result_indexes = []
    number_words_changed = None
    for i, col in enumerate(df.columns):
        if 'test' in col:
            print('------------')
            print('Test: ', df.iloc[0, i])
        elif 'word' in col and col != 'word_code':
            if check_changed:
                number_words_changed = df[df['word'] != df[col]]
            
                print('Words affected: ', number_words_changed.shape[0])
                
        elif 'result' in col:
            print("Number of words in other dictionary from test: ", len(df[df[col] == True]))
            
            print("Number of words changed in other dictionary: ", number_words_changed[col].value_counts())