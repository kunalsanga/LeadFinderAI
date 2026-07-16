import pandas as pd
from typing import List, Dict

def generate_excel(leads: List[Dict], filepath: str):
    df = pd.DataFrame(leads)
    
    # Rename some internal keys to match final output exactly
    rename_map = {
        "Address": "Headquarters Address",
        "Email": "Official Email",
        "Contact Us": "Contact Page"
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Reorder columns if they exist
    preferred_order = [
        "Company Name", "Founded Year", "Company Age", "Startup", "D2C", 
        "Category", "Website", "Phone", "Official Email", "Founder", 
        "LinkedIn", "Instagram", "Facebook", "Contact Page", "Careers Page", 
        "Headquarters Address", "Google Rating", "Reviews", "Meta Ads Probability", 
        "Marketing Technology", "Lead Score", "Target Fit"
    ]
    
    # Filter only columns that actually exist in the dataframe
    actual_columns = [col for col in preferred_order if col in df.columns]
    # Add any remaining columns not in preferred_order
    remaining = [col for col in df.columns if col not in actual_columns]
    
    df = df[actual_columns + remaining]
    df.to_excel(filepath, index=False)

def generate_csv(leads: List[Dict], filepath: str):
    df = pd.DataFrame(leads)
    df.to_csv(filepath, index=False)

def generate_companies_excel(companies: List[str], filepath: str):
    df = pd.DataFrame({"Company Name": companies})
    df.to_excel(filepath, index=False)
