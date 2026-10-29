"""
api.py
──────
FastAPI REST backend service for the AI-Powered Restaurant Recommendation System.
Serves the Next.js / React "AI DineSense" dark-theme frontend.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

from data.loader import load_zomato_dataset
from data.preprocessor import preprocess
from models.restaurant import UserPreferences
from services.recommender import get_recommendations
from services.output_formatter import format_all
from utils.validators import validate_preferences
from utils.logger import get_logger
from config.settings import (
    LLM_PROVIDER,
    GEMINI_MODEL,
    DATASET_NAME,
    TOP_N_CANDIDATES,
    TOP_N_RECOMMENDATIONS,
)

logger = get_logger(__name__)

app = FastAPI(
    title="Zomato AI DineSense API",
    description="Backend API providing semantic restaurant recommendations powered by Google Gemini and preprocessed Zomato data.",
    version="2.0.0",
)

# ── Enable CORS for local Next.js / React clients & Production Vercel ─────────
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
custom_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
origins = custom_origins if custom_origins else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "*",
]

is_wildcard = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory dataset cache ───────────────────────────────────────────────────
_cached_df: pd.DataFrame | None = None


def get_data() -> pd.DataFrame:
    """Retrieve or lazily ingest and preprocess the Zomato DataFrame."""
    global _cached_df
    if _cached_df is None:
        logger.info("Initializing in-memory Zomato DataFrame for API...")
        _cached_df = preprocess(load_zomato_dataset())
    return _cached_df


class PreferenceRequest(BaseModel):
    """Input payload matching user preferences from the DineSense interface."""
    location: str = Field(..., description="Target locality or city name", json_schema_extra={"example": "Koramangala, Bangalore"})
    budget: str = Field(default="medium", description="Budget tier: low, medium, or high", json_schema_extra={"example": "medium"})
    cuisines: list[str] = Field(default_factory=list, description="Target preferred cuisines", json_schema_extra={"example": ["cafe", "italian"]})
    min_rating: float = Field(default=4.0, ge=0.0, le=5.0, description="Minimum DineSense star rating", json_schema_extra={"example": 4.0})
    extras: str = Field(default="", description="Sensory vibe, occasion, or architectural preference", json_schema_extra={"example": "Cozy leafy outdoor courtyard with pour-over coffee"})


@app.get("/")
def root():
    return {
        "service": "Zomato AI DineSense API",
        "status": "online",
        "endpoints": ["/api/health", "/api/metadata", "/api/recommendations"],
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    """Healthcheck endpoint returning system diagnostics and loaded dataset size."""
    df = get_data()
    return {
        "status": "healthy",
        "llm_provider": LLM_PROVIDER,
        "model": GEMINI_MODEL,
        "records_loaded": len(df),
        "dataset": DATASET_NAME,
    }


@app.get("/api/metadata")
def metadata():
    """Returns dataset metrics, top localities, and popular cuisines for UI chips."""
    df = get_data()

    # Find the top 20 most frequent locations in the dataset for quick pills
    top_locations = (
        df["location"]
        .value_counts()
        .head(15)
        .index
        .str.title()
        .tolist()
    )

    all_locations = sorted(
        df["location"]
        .str.title()
        .unique()
        .tolist()
    )

    return {
        "total_records": len(df),
        "top_locations": top_locations,
        "all_locations": all_locations,
        "model": GEMINI_MODEL,
        "llm_provider": LLM_PROVIDER,
        "dataset": DATASET_NAME,
        "common_cuisines": [
            "Cafe",
            "Italian & Sourdough",
            "North Indian",
            "Continental",
            "Pan-Asian",
            "Artisan Desserts",
            "Fast Food",
            "Biryani",
        ],
        "budget_tiers": [
            {"id": "low", "label": "Low (≤ ₹500)", "range": "₹0–₹500"},
            {"id": "medium", "label": "Med (₹500–₹1.2k)", "range": "₹501–₹1,200"},
            {"id": "high", "label": "High (> ₹1.2k)", "range": "₹1,201+"},
        ],
        "max_candidates": TOP_N_CANDIDATES,
        "max_recommendations": TOP_N_RECOMMENDATIONS,
    }


@app.post("/api/recommendations")
def recommend(req: PreferenceRequest):
    """
    Main recommendation endpoint.
    Filters candidates, constructs prompt, invokes Gemini, and returns ranked recommendations.
    """
    df = get_data()

    prefs = UserPreferences(
        location=req.location,
        budget=req.budget.lower(),
        cuisines=req.cuisines,
        min_rating=req.min_rating,
        extras=req.extras,
    )

    # Validate preferences before pipeline
    errors = validate_preferences(prefs)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    try:
        recommendations = get_recommendations(df, prefs)
        formatted_recs = format_all(recommendations)
        return {
            "success": True,
            "count": len(formatted_recs),
            "recommendations": formatted_recs,
            "query": req.model_dump(),
        }
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {e}")
