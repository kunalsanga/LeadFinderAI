def calculate_lead_score(lead: dict) -> int:
    score = 0
    
    if lead.get("Website"):
        score += 20
    if lead.get("Email"):
        score += 15
    if lead.get("Phone"):
        score += 10
        
    rating = lead.get("Google Rating")
    if rating is not None and rating > 4.0:
        score += 10
        
    reviews = lead.get("Reviews")
    if reviews is not None and int(reviews) > 100:
        score += 10
        
    if lead.get("D2C (Yes/No)") == "Yes":
        score += 20
        
    if lead.get("Place Type") == "corporate_office" or "headquarters" in str(lead.get("Company Name", "")).lower():
        score += 15
        
    return score
