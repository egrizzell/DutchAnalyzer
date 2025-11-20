# DutchAnalyzer Project Plan

## 1. Project Overview

DutchAnalyzer is a linguistic analysis toolkit designed to extract **morphological rules** and **word frequency lists** from Dutch and English language data sources.  
It leverages:

- **Kaikki.org** (English and Dutch datasets, derived from Wiktionary)  
- **OpenTaal** (Dutch word lists)  
- **Leipzig Corpora Collection** (English and Dutch corpora for aggregate analysis)

The goal is to provide **ready-to-use frequency lists, morphological rules**, and a **reproducible Python environment** for research and educational purposes.

---

## 2. Goals
1. Scrape and refactor functions from private code 
2. Download and process relevant datasets.  
3. Generate high-quality frequency lists and morphological rules.  
4. Provide a reproducible Python environment with setup scripts.  

---

## 3. Milestones

| Milestone | Description | 
|-----------|-------------|-----------------|
| **M1** | Setup project structure, directories, and dependencies. Download data (Kaikki.org, OpenTaal, Leipzig).
| **M2** | Transfer and refactor utilities and helper functions from private code database|
| **M3** | preprocess Kaikki.org datasets. Normalize senses and top level word dictionaries. Combine into a unified dictionary. |
| **M4** | Extract morphological rules from Dutch and English data | 
| **M5** | Generate frequency lists and derived data | 
| **M6** | Create setup scripts (`setup_project.py`) and documentation | 


---
