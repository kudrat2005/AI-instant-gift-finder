
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from groq import (
    Groq,
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    RateLimitError,
)
from urllib.parse import quote_plus
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = FastAPI(
    title="AI Gift Finder API",
    version="1.0.0",
)

# CORS configuration for React

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-instant-gift-finder.vercel.app",
        "https://ai-instant-gift-finder-jfzq8tdug-kudrat2.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
You are an intelligent gifting assistant specializing in personalized,
creative, and meaningful gift recommendations.

Generate 6-8 personalized gift suggestions based on the user's input.

Rules:
- Analyze personality, hobbies, and preferences.
- Treat social media IDs only as user-provided hints.
- Never claim to access private social media data.
- Match the occasion, relationship, and budget.
- Budget is in Indian Rupees (INR).
- Generate a short 3-6 word product search phrase.

Return ONLY valid JSON without Markdown fences, in this format:
{
  "occasion": "string",
  "relationship": "string",
  "gift_suggestions": [
    {
      "title": "Gift Name",
      "reason": "Why this gift is suitable",
      "price_range": "₹XXX–₹XXX",
      "search_query": "short product search query"
    }
  ]
}
"""


class GiftRequest(BaseModel):
    instagram_id: Optional[str] = ""
    twitter_id: Optional[str] = ""
    preferred_platform: str = "Amazon"
    budget: str
    occasion: str
    relationship: str
    description: str


class GiftSuggestion(BaseModel):
    title: str
    reason: str
    price_range: str
    search_query: str
    link: str


class GiftResponse(BaseModel):
    occasion: str
    relationship: str
    platform: str
    gift_suggestions: list[GiftSuggestion]


# Build shopping search links
PLATFORM_URL_BUILDERS = {
    "Amazon": lambda q: (
        f"https://www.amazon.in/s?k={quote_plus(q)}"
    ),
    "Flipkart": lambda q: (
        f"https://www.flipkart.com/search?q={quote_plus(q)}"
    ),
    "Etsy": lambda q: (
        f"https://www.etsy.com/search?q={quote_plus(q)}"
    ),
    "Other": lambda q: (
        f"https://www.amazon.in/s?k={quote_plus(q)}"
    ),
}


@app.post("/api/generate-gifts", response_model=GiftResponse)
async def generate_gifts(req: GiftRequest):

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. Configure it in your environment.",
        )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=2500,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": req.model_dump_json(),
                },
            ],
        )

        raw = response.choices[0].message.content

        if not raw:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty response. Please try again.",
            )

        # Remove accidental Markdown fences
        raw = raw.strip()

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]

            if raw.endswith("```"):
                raw = raw[:-3].strip()

        # Parse the AI response
        parsed = json.loads(raw)

        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid response.",
            )

        if not isinstance(parsed.get("gift_suggestions"), list):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid gift suggestions format.",
            )

        # Select shopping platform
        platform = req.preferred_platform
        link_builder = PLATFORM_URL_BUILDERS.get(
            platform,
            PLATFORM_URL_BUILDERS["Amazon"],
        )

        suggestions = []

        for gift in parsed["gift_suggestions"]:
            if not isinstance(gift, dict):
                continue

            title = gift.get("title")
            reason = gift.get("reason")
            price_range = gift.get("price_range")
            search_query = gift.get("search_query")

            if not all(
                isinstance(value, str) and value.strip()
                for value in [
                    title,
                    reason,
                    price_range,
                    search_query,
                ]
            ):
                continue

            suggestions.append(
                GiftSuggestion(
                    title=title.strip(),
                    reason=reason.strip(),
                    price_range=price_range.strip(),
                    search_query=search_query.strip(),
                    link=link_builder(search_query.strip()),
                )
            )

        if not suggestions:
            raise HTTPException(
                status_code=502,
                detail="No valid gift suggestions were returned. Please try again.",
            )

        return GiftResponse(
            occasion=parsed.get("occasion") or req.occasion,
            relationship=parsed.get("relationship") or req.relationship,
            platform=platform,
            gift_suggestions=suggestions,
        )

    except HTTPException:
        raise

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="Could not parse the AI response. Please try again.",
        )

    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Groq authentication failed. Check your GROQ_API_KEY.",
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Groq rate limit reached. Please try again later.",
        )

    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Groq. Please try again.",
        )

    except APIStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Groq API request failed with status {e.status_code}.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating gifts.",
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI Gift Finder",
    }
