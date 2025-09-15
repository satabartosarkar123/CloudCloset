'''just for testing out not a part of main system'''

import json
from llm_agent import generate_three_outfits_mistral

details = {
    "event_type": "traditional wedding",
    "weather": "humid, 28°C",
    "gender": "male",
    "location": "Kolkata",
    "style_preference": "classic",
    "body_type": "tall",
    "color_preferences": ["cream", "gold", "navy blue", "pastels"],
    "avoid_colors": ["black", "bright red", "neon colors"],
    "season": "monsoon",
    "cultural_context": "traditional Bengali"
}

try:
    dic = generate_three_outfits_mistral(details)
    print("Parsed JSON:", json.dumps(dic, indent=2))
except Exception as e:
    print(f"Error: {e}")
