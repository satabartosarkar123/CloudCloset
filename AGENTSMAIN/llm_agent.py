import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise EnvironmentError("Set MISTRAL_API_KEY environment variable")

client = Mistral(api_key=api_key)

def generate_three_outfits_mistral(event_details):
    # Clean and prepare the data - replace None/null with "no preference"
    cleaned_data = {}
    for key, value in event_details.items():
        if value is None:
            cleaned_data[key] = "no preference"
        else:
            cleaned_data[key] = value
    
    system_prompt = (
        "You are a fashion stylist AI assistant. Generate exactly 3 distinct outfit combinations in valid JSON format, strictly tailored to ALL provided details. "
        "Consider: event type, gender, location, weather, style preferences, body type, color preferences, season, and cultural context. "
        "Each outfit must include: an 'outfit_id' (integer: 1, 2, or 3), a 'description' (string), 'clothing_items' (list of strings), 'accessories' (list of strings), and 'weather_considerations' (string). "
        "Return only valid JSON, enclosed in curly braces {}, with no extra text, code blocks (e.g., ```json), or incomplete structures. "
        "When a field shows 'no preference', use your best judgment for that category based on other provided details. "
        "Example format: "
        "{\"outfits\": ["
        "{\"outfit_id\": 1, \"description\": \"A cozy look\", \"clothing_items\": [\"sweater\", \"jeans\"], \"accessories\": [\"earrings\", \"boots\"], \"weather_considerations\": \"Scarf for warmth\"},"
        "{\"outfit_id\": 2, \"description\": \"A trendy outfit\", \"clothing_items\": [\"dress\", \"tights\"], \"accessories\": [\"necklace\", \"loafers\"], \"weather_considerations\": \"Coat for cool weather\"},"
        "{\"outfit_id\": 3, \"description\": \"A modern vibe\", \"clothing_items\": [\"blazer\", \"trousers\"], \"accessories\": [\"flats\", \"tote\"], \"weather_considerations\": \"Cardigan for layering\"}"
        "]}"
    )

    user_message = json.dumps(cleaned_data, indent=2)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            max_tokens=1500,
            temperature=0.5
        )

        output_text = response.choices[0].message.content if response.choices else ""
        print("Raw API response:", output_text)
        print("Response length:", len(output_text))

        if not output_text:
            raise ValueError("Mistral API returned an empty response")

        cleaned_text = output_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.replace("```", "").strip()

        if not cleaned_text.startswith("{"):
            raise ValueError(f"Response is not valid JSON: {cleaned_text[:50]}...")

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Mistral API JSON output: {e}\nRaw response: {output_text}")
    except Exception as e:
        raise ValueError(f"Mistral API call failed: {e}\nRaw response: {output_text if 'output_text' in locals() else 'No response'}")