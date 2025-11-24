from dutchanalyzer.config import *
import pandas as pd
import datetime
from pathlib import Path
from dutchanalyzer.utilities.utils import *
from dutchanalyzer.utilities.json_utils import *

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


