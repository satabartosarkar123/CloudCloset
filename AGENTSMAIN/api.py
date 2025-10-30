import json
import logging
from typing import List, Optional

from fastapi import Body, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .llm_agent import generate_three_outfits_mistral

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CloudCloset Outfit API",
    description=(
        "Generate personalised outfit recommendations backed by Mistral. "
        "Provide event context, receive three curated looks."
    ),
    version="1.0.0",
)


class EventDetails(BaseModel):
    date: Optional[str] = Field(
        default=None,
        description="Date of the occasion (ISO format preferred).",
        example="2025-10-10",
    )
    event_type: Optional[str] = Field(
        default=None, description="Type of event.", example="wedding"
    )
    gender: Optional[str] = Field(
        default=None, description="Recipient's gender identity.", example="female"
    )
    weather: Optional[str] = Field(
        default=None,
        description="Weather forecast or conditions.",
        example="cool, windy evening, 18°C",
    )
    location: Optional[str] = Field(
        default=None, description="Event location.", example="London, outdoor venue"
    )
    time: Optional[str] = Field(
        default=None, description="Time of day for the event.", example="evening"
    )
    occasion: Optional[str] = Field(
        default=None,
        description="Dress code or purpose for the event.",
        example="semi-formal business gala",
    )
    vibe: Optional[str] = Field(
        default=None,
        description="Desired styling vibe.",
        example="professional, elegant",
    )
    dress_code: Optional[str] = Field(
        default=None,
        description="Explicit dress code, if provided.",
        example="cocktail attire",
    )


class Outfit(BaseModel):
    outfit_id: Optional[int] = Field(
        default=None, description="Identifier of the recommended outfit."
    )
    description: Optional[str] = Field(
        default=None, description="Narrative description of the look."
    )
    clothing_items: Optional[List[str]] = Field(
        default=None, description="List of core clothing pieces."
    )
    accessories: Optional[List[str]] = Field(
        default=None, description="Recommended accessories."
    )
    weather_considerations: Optional[str] = Field(
        default=None, description="Notes on weather-appropriate adjustments."
    )


class OutfitResponse(BaseModel):
    outfits: List[Outfit] = Field(
        default_factory=list, description="List of recommended outfits."
    )


@app.get("/", tags=["Health"])
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "CloudCloset outfit service is running."}


@app.post(
    "/outfits",
    response_model=OutfitResponse,
    tags=["Outfits"],
    summary="Generate three personalised outfits",
)
async def generate_outfits(
    request: Request, details: Optional[EventDetails] = Body(default=None)
):
    """
    Accept structured event details and return three outfit recommendations.
    Any missing values are interpreted as user having "no preference".
    """
    try:
        payload_dict = None

        if details is not None:
            payload_dict = details.model_dump()
        else:
            raw_body = await request.body()
            if not raw_body:
                raise HTTPException(status_code=400, detail="Empty request body.")
            try:
                payload_dict = json.loads(raw_body)
            except json.JSONDecodeError as err:
                raise HTTPException(status_code=400, detail="Invalid JSON payload.") from err

        validated_details = EventDetails.model_validate(payload_dict)
        response_payload = generate_three_outfits_mistral(validated_details.model_dump())
        return OutfitResponse.model_validate(response_payload)
    except ValueError as err:
        logger.exception("Failed to generate outfits: %s", err)
        raise HTTPException(status_code=502, detail=str(err)) from err
    except Exception as err:  # pragma: no cover - safeguard for unexpected issues
        logger.exception("Unexpected error: %s", err)
        raise HTTPException(status_code=500, detail="Internal server error") from err
