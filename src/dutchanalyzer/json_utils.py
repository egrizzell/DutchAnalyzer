import os
from tqdm import tqdm
import re
from array import array
import ast
from itertools import groupby
import pandas as pd
import numpy as np
import ujson
from pathlib import Path
import datetime

def count_lines_with_progress(file_path, chunk_size=1024 * 1024):
    total_size = os.path.getsize(file_path)
    lines = 0
    longest_line = 0
    num_chunks_longest = 0
    current_chunks_count = 1
    with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
        while chunk := f.read(chunk_size):
            chunk_count = chunk.count(b'\n')
            
            lines += chunk_count
            pbar.update(len(chunk))
    return lines

def get_longest_line(file_path, chunk_size=1024 * 1024):
    total_size = os.path.getsize(file_path)
    lines = 0
    longest_line = 0
    longest_lines = []
    num_chunks_longest = 0
    current_chunks_count = 1
    current_line = 0
    lowest_chunks_per_line = 1000000
    with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
        current_chunk = b''
        last_chunk = b''
        while chunk := f.read(chunk_size):
            chunk_count = chunk.count(b'\n')
            if chunk_count < lowest_chunks_per_line:
                lowest_chunks_per_line = chunk_count
                longest_lines.append(((1, chunk_count), chunk))

            else:
                if chunk_count == 0:
                    if current_chunks_count == 1:
                        current_chunk = last_chunk
                    current_chunk += chunk
                    current_chunks_count += 1
                else:
                    last_chunk = chunk
                    if current_chunks_count > num_chunks_longest:
                        longest_line = current_chunk
                        num_chunks_longest =  current_chunks_count
                        longest_lines.append((current_chunks_count, current_chunk))
                        current_chunks_count = 1

            lines += chunk_count
            pbar.update(len(chunk))
            
    return lines, longest_lines
                
def check_has_valid_chars(text, num_to_check=2):
    allowed_letters = "a-zA-ZáéíóúÁÉÍÓÚèàòùÈÀÒÙëïöüËÏÖÜ"
    # punctuation (we escape it safely)
    allowed_punct = re.escape("'- .,;:")
    # combine safely; note the hyphen is at the *end* to avoid range issues
    allowed_chars = allowed_letters + allowed_punct + "-"
    try: 
        text = str(text).strip()
        first_chars = text[:num_to_check]  # take first one or two characters
        # check each character individually
        for ch in first_chars:
            if not re.match(f"[{allowed_chars}]", ch):
                return False
        return True
    except Exception as e: 
        print("Error:", e)
        return False