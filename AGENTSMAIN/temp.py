import json
from llm_agent import generate_three_outfits_mistral

details = {
        "date": "2025-10-10",
        "event_type": "wedding",
        "gender": "female",
        "weather": "cool, windy evening, 18°C",
        "location": "London, outdoor venue",
        "time": "evening",
        "occasion": "semi-formal business gala",
        "vibe": "professional, elegant",
        "dress_code": None  # Simulate missing field
}

try:
    outfits = generate_three_outfits_mistral(details)
    print("Parsed JSON:", json.dumps(outfits, indent=2))
except Exception as e:
    print(f"Error: {e}")
