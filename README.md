# CloudCloset Agents Integration Guide

## Overview

This folder hosts the Mistral-powered outfit recommendation agent and optional Stable Diffusion image generator. The core flow:

1. Collect structured event details.
2. Call `generate_three_outfits_mistral` to fetch tailored outfit JSON from Mistral.
3. (Optional) Feed each outfit description to `generate_images_for_outfits` to render visuals with Hugging Face diffusers.

Everything is synchronous and Python-based, so you can drop these functions into CLI tools, web backends, or other automations.

## Key Modules

- `AGENTSMAIN/llm_agent.py` – wraps the Mistral SDK, sanitises inputs, and enforces JSON output.
- `AGENTSMAIN/imagine.py` – loads Stable Diffusion, handles device selection (CPU/MPS), and generates images per outfit description.
- `AGENTSMAIN/temp.py` – minimal script that wires the two for quick smoke tests.

## Prerequisites

- Python 3.11 (matches the lockfile versions).
- Ability to install the packages listed in `AGENTSMAIN/requirements.txt`.
- A valid [Mistral API key](https://docs.mistral.ai/).
- (Optional, for image generation) A Hugging Face access token with permission to download Stable Diffusion weights.

## Setup

1. Create or activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r CloudCloset/AGENTSMAIN/requirements.txt
   ```
3. Configure environment variables. The code calls `load_dotenv()`, so you can store secrets in `CloudCloset/.env` (already created) or export them in your shell:
   ```bash
   # CloudCloset/.env
   MISTRAL_API_KEY=your_mistral_key
   HUGGINGFACE_TOKEN=your_hf_token   # only required for imagine.py
   ```
   When running the image generator, ensure `HUGGINGFACE_TOKEN` is available so diffusers can pull the model checkpoint.

## Usage

### REST API (FastAPI)

Start the service with Uvicorn (locally):
```bash
uvicorn CloudCloset.AGENTSMAIN.api:app --host 0.0.0.0 --port 8000
```

Once running you get:
- Interactive Swagger UI at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`
- Health check at `GET /`
- Outfit generator at `POST /outfits`

**Sample request**
```bash
curl -X POST http://localhost:8000/outfits \
  -d '{
        "date": "2025-10-10",
        "event_type": "wedding",
        "gender": "female",
        "weather": "cool, windy evening, 18°C",
        "location": "London, outdoor venue",
        "time": "evening",
        "occasion": "semi-formal business gala",
        "vibe": "professional, elegant",
        "dress_code": null
      }'
```

`Content-Type: application/json` is recommended, but the API also accepts raw bodies without that header and will attempt to parse them as JSON for Postman or curl setups that omit it.

Perfect for Postman: point it to `POST /outfits` with the same JSON body; responses follow the schema below.

**Deploying to Render**
1. Commit and push the repo (note the root-level `requirements.txt` simply delegates to `CloudCloset/AGENTSMAIN/requirements.txt` so Render installs the same stack).
2. Either:
   - **Use `render.yaml`** – Create a *Blueprint* service in Render and point it to the repo. The blueprint sets the build/start commands for you.
   - **Manual Web Service** – Create a new Python web service and configure:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn CloudCloset.AGENTSMAIN.api:app --host 0.0.0.0 --port $PORT`
3. In Render’s dashboard add `MISTRAL_API_KEY` (required) and `HUGGINGFACE_TOKEN` (optional) as environment variables.
4. Deploy; Render exposes the API at `https://<your-service>.onrender.com` with `/docs` and `/outfits` available.

### Outfit JSON generation (standalone helper)

```python
from CloudCloset.AGENTSMAIN.llm_agent import generate_three_outfits_mistral

details = {
    "date": "2025-10-10",
    "event_type": "wedding",
    "gender": "female",
    "weather": "cool, windy evening, 18°C",
    "location": "London, outdoor venue",
    "time": "evening",
    "occasion": "semi-formal business gala",
    "vibe": "professional, elegant",
    "dress_code": None,          # Any None becomes "no preference"
}

outfit_json = generate_three_outfits_mistral(details)
```

**Expected response shape**
```json
{
  "outfits": [
    {
      "outfit_id": 1,
      "description": "Evening ...",
      "clothing_items": ["..."],
      "accessories": ["..."],
      "weather_considerations": "..."
    },
    { "outfit_id": 2, ... },
    { "outfit_id": 3, ... }
  ]
}
```

The helper automatically replaces missing fields with `"no preference"` before talking to Mistral and validates the JSON before returning it.

### Image generation (optional)

```python
from AGENTSMAIN.imagine import generate_images_for_outfits

descriptions = [o["description"] for o in outfit_json["outfits"]]
images = generate_images_for_outfits(descriptions)

for item in images:
    print(item["description"], item.get("image_path", item.get("error")))
```

Outputs include local file paths under `generation/` or error messages if the diffusers pipeline fails to load or render.

By default the pipeline tries `SG161222/Realistic_Vision_V2.0` and falls back to `runwayml/stable-diffusion-v1-5`. On Apple Silicon the Metal backend (MPS) is used when available; otherwise CPU mode is selected automatically.

### Local sanity check

Run the sample script to verify both pieces together:
```bash
cd CloudCloset/AGENTSMAIN
python temp.py
```
It logs any parsing errors so you can adjust prompts or credentials quickly.

## Integration Notes

- The LLM call is synchronous; wrap it in asyncio executors or background tasks if you integrate with async frameworks like FastAPI.
- Guard against external failures: network hiccups, invalid JSON (rare but handled), or exhausted API credits.
- Log the raw Mistral response before parsing in production to help diagnose prompt drifts.
- For large-scale usage, consider caching outfits per event signature to avoid repeated API costs.

With the environment ready, you can import these functions anywhere inside your application stack and orchestrate personalised wardrobes backed by Mistral and Stable Diffusion.
