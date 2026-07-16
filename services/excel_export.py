import pandas as pd
from typing import List, Dict

def generate_excel(leads: List[Dict], filepath: str):
    df = pd.DataFrame(leads)
    df.to_excel(filepath, index=False)

def generate_csv(leads: List[Dict], filepath: str):
    df = pd.DataFrame(leads)
    df.to_csv(filepath, index=False)

def generate_companies_excel(companies: List[str], filepath: str):
    df = pd.DataFrame({"Company Name": companies})
    df.to_excel(filepath, index=False)
