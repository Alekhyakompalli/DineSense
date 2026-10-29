"""
app.py
───────
Streamlit explorer and verification dashboard for the Zomato AI Restaurant Recommendation System.
Provides interactive data exploration, candidate filtering, and LLM recommendation testing.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="🍽️ Zomato AI DineSense — Explorer & Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
import sys
from utils.logger import get_logger
from data.loader import load_zomato_dataset
from data.preprocessor import preprocess
from models.restaurant import UserPreferences
from services.filter_restaurants import filter_restaurants, serialize_candidates
from services.recommender import get_recommendations
from services.output_formatter import format_all
from utils.validators import validate_preferences

logger = get_logger(__name__)

# ── Config validation (import triggers all startup checks) ────────────────────
try:
    from config.settings import (
        LLM_PROVIDER,
        TOP_N_CANDIDATES,
        TOP_N_RECOMMENDATIONS,
        DATASET_NAME,
        GEMINI_MODEL,
    )
    config_ok = True
    config_error = None
except (EnvironmentError, ValueError, RuntimeError) as e:
    config_ok = False
    config_error = str(e)


# ── Data Loading (cached) ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_dataframe():
    """Load and preprocess the Zomato dataset once and cache the resulting DataFrame."""
    raw_df = load_zomato_dataset()
    return preprocess(raw_df)


# ── Config Error Guard ────────────────────────────────────────────────────────
if not config_ok:
    st.error("**Configuration Error — App cannot start.**")
    st.code(config_error, language="text")
    st.info(
        "**Fix:**\n"
        "1. Copy `.env.example` to `.env`\n"
        "2. Add your API key for the chosen LLM provider\n"
        "3. Restart the app with `streamlit run app.py`"
    )
    st.stop()

# ── Load Dataset ──────────────────────────────────────────────────────────────
with st.spinner("📦 Loading & preprocessing Zomato dataset from HuggingFace..."):
    try:
        df = get_dataframe()
        data_loaded = True
        data_error = None
    except Exception as e:
        df = None
        data_loaded = False
        data_error = str(e)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🍽️ DineSense Engine")
    st.caption("Admin & Verification Dashboard")
    st.divider()

    # Active LLM Provider & System Info
    st.success("✅ System Status: Active")
    st.markdown(f"**Active LLM:** `{LLM_PROVIDER.upper()}`")
    st.markdown(f"**Model:** `{GEMINI_MODEL}`")
    st.markdown(f"**Filter Pool Limit:** `{TOP_N_CANDIDATES}` candidates")
    st.markdown(f"**Top Recommendations:** `{TOP_N_RECOMMENDATIONS}`")
    st.markdown(f"**Python Runtime:** `{sys.version.split()[0]}`")

    st.divider()
    # Dataset Metrics Section
    st.subheader("📊 Dataset Metrics")
    if data_loaded and df is not None:
        st.metric("Total Curated Records", f"{len(df):,}")
        st.metric("Unique Neighborhoods", f"{df['location'].nunique():,}")
        st.metric("Average Star Rating", f"{df['rating'].mean():.2f} / 5.0")
    else:
        st.error("Failed to load dataset")

    st.divider()
    # About Section
    with st.expander("ℹ️ About DineSense", expanded=False):
        st.markdown("""
        **Zomato AI DineSense** is a semantic restaurant recommendation engine.
        
        - **Data Source:** Curated HuggingFace dataset with 12,140 verified dining spots.
        - **Pipeline:** Preprocessing → 3-Tier Fallback Filter → Prompt Synthesis → Gemini Multimodal Reasoning → Hallucination-Checked Output.
        - **Frontend:** Next.js dark-theme glassmorphism UI with real-time FastAPI backend.
        """)

    st.divider()
    st.caption("📄 [Problem Statement](doc/ProblemStatement.md)")
    st.caption("🏗️ [Architecture](doc/architecture.md)")
    st.caption("📋 [Implementation Plan](doc/ImplementationPlan.md)")
    st.caption("📦 [Dataset on HuggingFace](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)")

# ── Main Area ─────────────────────────────────────────────────────────────────
st.title("🍽️ Zomato AI DineSense Verification Console")
st.caption("Explore Candidate Filtering, LLM Prompt Generation, and Full Recommendation Synthesis")
st.divider()

if not data_loaded:
    st.error("❌ **Data Loading Error — App cannot load dataset.**")
    st.code(data_error, language="text")
    st.stop()

# ── Status Banner ─────────────────────────────────────────────────────────────
st.success("✅ **Phases 1–6 Complete** — Dataset Ingestion, Filtering with Fallback, LLM Reasoning, FastAPI Backend, Next.js UI, & Test Suite.")

# ── Tabbed Explorer ────────────────────────────────────────────────────────────
tab_recommend, tab_filter, tab_data = st.tabs([
    "🤖 LLM Recommendation Pipeline",
    "🔍 Candidate Filter & Fallback",
    "📊 Dataset Inspector",
])

with tab_recommend:
    st.subheader("🚀 End-to-End Recommendation Test")
    col1, col2 = st.columns(2)
    with col1:
        rec_loc = st.text_input("📍 Location", value="Koramangala, Bangalore", key="rec_loc")
        rec_budget = st.selectbox("💰 Budget Tier", ["medium", "low", "high"], index=0, key="rec_budget")
        rec_rating = st.slider("⭐ Minimum Rating", 3.0, 5.0, 4.0, step=0.1, key="rec_rating")
    with col2:
        cuisine_opts = ["cafe", "italian", "chinese", "north indian", "south indian", "continental", "desserts", "pan-asian"]
        rec_cuisines = st.multiselect("🍛 Cuisines", cuisine_opts, default=["cafe", "italian"], key="rec_cuisines")
        rec_extras = st.text_area(
            "✨ Dining Vibe / Natural Language Prompt",
            value="Cozy leafy outdoor courtyard with specialty pour-over coffee, artisanal sourdough bakes, quiet for conversation.",
            key="rec_extras",
        )

    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        generate_clicked = st.button("🚀 Generate AI Recommendations", type="primary", use_container_width=True)
    with btn_col2:
        clear_clicked = st.button("🗑️ Clear Results", use_container_width=True)

    if clear_clicked:
        st.session_state.pop("last_recommendations", None)
        st.info("Results cleared.")

    if generate_clicked:
        prefs = UserPreferences(
            location=rec_loc,
            budget=rec_budget.lower(),
            cuisines=rec_cuisines,
            min_rating=rec_rating,
            extras=rec_extras,
        )
        errors = validate_preferences(prefs)
        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        else:
            with st.spinner("🤖 Consulting Gemini AI & ranking candidates..."):
                try:
                    recs = get_recommendations(df, prefs)
                    if not recs:
                        st.warning("No recommendations returned after filtering.")
                    else:
                        formatted = format_all(recs)
                        st.session_state["last_recommendations"] = formatted
                except Exception as ex:
                    st.error(f"Recommendation failed: {ex}")

    if "last_recommendations" in st.session_state and st.session_state["last_recommendations"]:
        formatted = st.session_state["last_recommendations"]
        st.success(f"🎯 Successfully generated {len(formatted)} recommendations!")
        for r in formatted:
            with st.container():
                st.markdown(f"### {r['medal']} #{r['rank']} {r['name']} — ⭐ {r['rating_str']} ({r['match_score']}% Match)")
                st.markdown(f"**Cuisine:** {r['cuisine']} | **Cost:** {r['cost_str']}")
                st.info(f"💡 **AI DineSense Reason:** {r['explanation']}")
                st.divider()

with tab_filter:
    st.subheader("🔍 Filter & Fallback Explorer")
    with st.form("filter_test_form"):
        col1, col2 = st.columns(2)
        with col1:
            loc_input = st.text_input("📍 Location", value="koramangala", placeholder="e.g. koramangala, indiranagar")
            budget_input = st.radio("💰 Budget Tier", ["Low", "Medium", "High"], index=1, horizontal=True)
        with col2:
            rating_input = st.slider("⭐ Minimum Rating", 0.0, 5.0, 4.0, step=0.1)
            cuisine_options = ["cafe", "italian", "chinese", "north indian", "south indian", "continental", "desserts", "burger"]
            cuisines_input = st.multiselect("🍛 Cuisines (optional)", cuisine_options, default=["cafe"])

        test_submitted = st.form_submit_button("🔎 Filter Candidates", use_container_width=True)

    if test_submitted:
        prefs = UserPreferences(
            location=loc_input,
            budget=budget_input.lower(),
            cuisines=cuisines_input,
            min_rating=rating_input,
        )
        validation_errors = validate_preferences(prefs)
        if validation_errors:
            for err in validation_errors:
                st.error(f"⚠️ {err}")
        else:
            candidates = filter_restaurants(df, prefs)
            if candidates.empty:
                st.warning("😕 No matching restaurants found after all fallback tiers.")
            else:
                st.success(f"🎯 Found **{len(candidates)}** candidate restaurants (capped at {TOP_N_CANDIDATES}):")
                st.dataframe(candidates, use_container_width=True)
                with st.expander("📝 Serialized Candidate Text (Prepared for LLM Prompt)", expanded=False):
                    st.code(serialize_candidates(candidates), language="text")

with tab_data:
    st.subheader("📊 Preprocessed Dataset Preview")
    st.dataframe(df.head(25), use_container_width=True)
    st.caption(f"Total clean records available: **{len(df):,}** (Deduplicated, Normalized, and Mapped)")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.85rem;'>"
    "🍽️ <strong>Zomato AI DineSense</strong> • "
    "Data Source: <a href='https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation' target='_blank'>ManikaSaini/zomato-restaurant-recommendation</a> on HuggingFace • "
    "Powered by Google Gemini 1.5 Flash"
    "</div>",
    unsafe_allow_html=True,
)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
