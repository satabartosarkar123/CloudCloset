'''just for testing out not a part of main system'''

import json
from llm_agent import generate_three_outfits_mistral

event_details = {
    "event_type": "traditional wedding",
    "weather": "humid, 28°C",
    "gender": "male",
    "location": "Kolkata"
}

try:
    dic = generate_three_outfits_mistral(event_details)
    print("Parsed JSON:", json.dumps(dic, indent=2))
except Exception as e:
    print(f"Error: {e}")
