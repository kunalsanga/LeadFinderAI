def calculate_lead_score(lead: dict) -> int:
    score = 0
    
    if lead.get("Startup") and lead.get("Company Age", 0) <= 5 and lead.get("Company Age", 0) > 0:
        score += 25
        
    if lead.get("D2C"):
        score += 20
        
    if lead.get("Website"):
        score += 15
        
    if lead.get("Email"):
        score += 15
        
    if lead.get("Phone"):
        score += 10
        
    if lead.get("LinkedIn"):
        score += 5
        
    if lead.get("Instagram"):
        score += 5
        
    rating = lead.get("Google Rating")
    if rating is not None and rating > 4.0:
        score += 5
        
    reviews = lead.get("Reviews")
    if reviews is not None and int(reviews) > 100:
        score += 5
        
    if lead.get("Place Type") == "corporate_office" or "headquarters" in str(lead.get("Company Name", "")).lower():
        score += 10
        
    if lead.get("Marketing Technology"):
        score += 10
        
    return score

def calculate_target_fit(score: int) -> str:
    if score >= 90:
        return "⭐⭐⭐⭐⭐ Perfect Lead"
    elif score >= 75:
        return "⭐⭐⭐⭐ Good Lead"
    elif score >= 50:
        return "⭐⭐⭐ Average"
    elif score >= 30:
        return "⭐⭐ Poor"
    else:
        return "⭐ Not Target"
