### 28-10-25: 
- The post processing json file is much shorter than the raw one at 1,423,954 to the 10,329,308 million in the raw file

### 29-10-25: 
- Together the Dutch/English post processed dfs are (1096880, 45) and 1040023 unique words
- The raw df without the mul lang code is (1558932, 37) with 1446918 unique words
- The total accounting of all words in the combined dfs is (1691350, 4) with information about whether left or right was in the df in the 'all_words_in_combo_dictionaries_2025-10-29.csv' file. 

- After filtering the raw df is (1549681 rows × 38 columns)

### 30-10
- Have determined that all words have a sense
- Shape of df after dropping several columns and the categories of symbol, character, 'num', and 'phrase' from df we are down to (2625841, 37) from (2637038, 51), after removing proverb and name it is now (2334244, 37)
