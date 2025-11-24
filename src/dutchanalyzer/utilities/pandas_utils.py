import pandas as pd
import datetime
# Pandas Utils

def summarize_df(df: pd.DataFrame, name: str = None, num_top_values=10) -> pd.DataFrame:
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


def sort_df_columns(df, start_cols=['word', 'pos', 'lang_code', 'standard_lang', 'senses'], end_cols=['translations', 'lang', 'wl_code'], groups=['forms', 'etymology', 'nyms', 'categories']):
    df_cols = df.columns
    start = [c for c in start_cols if c in df_cols]
    end = [c for c in end_cols if c in df_cols]
    protected_cols = start 
    
    forms_grouping = ['form_of','forms', 'alt_of', 'inflection_templates', 'derived']
    etymology_grouping = ['etymology_templates', 'etymology_text', 'etymology_tree']
    nyms_grouping = ['synonyms', 'antonyms', 'hypernyms','hyponyms', 'troponyms', 'holonyms', 'meronyms']
    categories_grouping = ['categories', 'links', 'related', 'topics']

    if groups:
        for group in groups:
            if 'forms' == group:
                forms_grouping = [c for c in forms_grouping if c in df_cols]
                protected_cols += forms_grouping
            if 'etymology' == group:
                etymology_grouping = [c for c in etymology_grouping if c in df_cols]
                protected_cols += etymology_grouping

            if 'nyms' == group:
                nyms_grouping = [c for c in nyms_grouping if c in df_cols]
                protected_cols += nyms_grouping

            if 'categories' == group:
                categories_grouping = [c for c in categories_grouping if c in df_cols]
                protected_cols += categories_grouping

    protected_cols = [c for c in protected_cols if c in df_cols]
    unprotected_cols = [c for c in df_cols if c not in protected_cols and c not in end]

    unprotected_cols.sort()
    new_cols = protected_cols + unprotected_cols + end
    df = df.loc[:, new_cols]
    return df
    
    