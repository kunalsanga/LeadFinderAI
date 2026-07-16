def calculate_lead_score(lead: dict) -> int:
    score = 0
    
    if lead.get("Website"):
        score += 20
    if lead.get("Phone"):
        score += 10
    if lead.get("Email"):
        score += 20
    if lead.get("Meta Ads (Yes/No)") == "Yes":
        score += 30
    
    rating = lead.get("Google Rating")
    if rating is not None and rating > 4.0:
        score += 20
        
    return score
