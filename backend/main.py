from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from groq import Groq          # 👈 swap to: from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Gift Finder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))   # 👈 swap to OpenAI(...) if needed

SYSTEM_PROMPT = """You are an intelligent gifting assistant specializing in personalized, creative, and meaningful gift recommendations.

Given user input as JSON, generate 6–8 highly personalized gift suggestions.

Rules:
- Analyze the description deeply for personality, hobbies, and preferences
- If social media IDs are provided, infer general interest themes (do NOT access private data)
- Suggestions must be relevant to the occasion, within budget, and relationship-appropriate
- Prioritize creativity and usefulness over generic gifts
- Budget is in Indian Rupees (₹)
- For the "search_query" field, generate a short 3–6 word search string (NOT a full URL)

Return ONLY valid JSON with no markdown fences, no preamble, no explanation:
{
  "occasion": "string",
  "relationship": "string",
  "gift_suggestions": [
    {
      "title": "Gift Name",
      "reason": "Why this gift is suitable (1–2 sentences)",
      "price_range": "₹XXX–₹XXX",
      "search_query": "short search query for the gift"
    }
  ]
}"""


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


PLATFORM_URL_BUILDERS = {
    "Amazon":   lambda q: f"https://www.amazon.in/s?k={q.replace(' ', '+')}",
    "Flipkart": lambda q: f"https://www.flipkart.com/search?q={q.replace(' ', '+')}",
    "Etsy":     lambda q: f"https://www.etsy.com/search?q={q.replace(' ', '+')}",
    "Other":    lambda q: f"https://www.amazon.in/s?k={q.replace(' ', '+')}",
}


@app.post("/api/generate-gifts", response_model=GiftResponse)
async def generate_gifts(req: GiftRequest):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.model_dump_json()}
            ]
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        link_builder = PLATFORM_URL_BUILDERS.get(req.preferred_platform, PLATFORM_URL_BUILDERS["Amazon"])

        suggestions = []
        for g in parsed.get("gift_suggestions", []):
            suggestions.append(GiftSuggestion(
                title=g["title"],
                reason=g["reason"],
                price_range=g["price_range"],
                search_query=g["search_query"],
                link=link_builder(g["search_query"])
            ))

        return GiftResponse(
            occasion=parsed.get("occasion", req.occasion),
            relationship=parsed.get("relationship", req.relationship),
            platform=req.preferred_platform,
            gift_suggestions=suggestions
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except anthropic.APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to Anthropic API.")
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid Anthropic API key. Check your .env file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "service": "AI Gift Finder"}
