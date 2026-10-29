# 🍽️ Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

## Overview

You are tasked with building an **AI-powered restaurant recommendation service** inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining **structured data** with a **Large Language Model (LLM)**.

---

## 🎯 Objective

Design and implement an application that:

- Takes **user preferences** (such as location, budget, cuisine, and ratings)
- Uses a **real-world dataset** of restaurants
- Leverages an **LLM** to generate personalized, human-like recommendations
- Displays **clear and useful results** to the user

---

## 🔄 System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:
  > 📦 [`ManikaSaini/zomato-restaurant-recommendation`](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine type
  - Cost / Budget range
  - Rating

---

### 2. User Input

Collect user preferences including:

| Preference | Example Values |
|---|---|
| **Location** | Delhi, Bangalore, Mumbai |
| **Budget** | Low, Medium, High |
| **Cuisine** | Italian, Chinese, Indian |
| **Minimum Rating** | e.g., ≥ 4.0 |
| **Additional Preferences** | Family-friendly, Quick service, etc. |

---

### 3. Integration Layer

- **Filter** and prepare relevant restaurant data based on user input
- **Pass** structured results into an LLM prompt
- **Design** a prompt that helps the LLM reason and rank options intelligently

---

### 4. Recommendation Engine

Use the LLM to:

- ✅ **Rank** restaurants based on relevance to user preferences
- 💬 **Explain** why each recommendation fits the user's needs
- 📝 Optionally **summarize** all choices for easy comparison

---

### 5. Output Display

Present top recommendations in a user-friendly format:

| Field | Description |
|---|---|
| **Restaurant Name** | Name of the recommended restaurant |
| **Cuisine** | Type of cuisine served |
| **Rating** | Aggregated user rating |
| **Estimated Cost** | Approximate cost for two |
| **AI-Generated Explanation** | LLM reasoning for the recommendation |

---

## 🏗️ High-Level Architecture

```
User Input (Location, Budget, Cuisine, Rating, Preferences)
        │
        ▼
┌──────────────────────┐
│   Data Ingestion     │  ← Hugging Face Dataset (Zomato)
│   & Preprocessing    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Filtering & Ranking │  ← Structured data matching user criteria
│  (Integration Layer) │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   LLM Prompt Engine  │  ← Sends filtered data + user context to LLM
│  (Recommendation)    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   Output Display     │  ← Top-N restaurant recommendations with explanations
└──────────────────────┘
```

---

## 📦 Dataset

- **Source:** [Hugging Face — ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Key Fields Used:**
  - `name` — Restaurant name
  - `location` / `city` — Geographic location
  - `cuisines` — Type of food served
  - `cost` / `approx_cost` — Budget indicator
  - `rating` / `aggregate_rating` — User rating score

---

## 🤖 LLM Integration

- The filtered restaurant list is passed as **structured context** into the LLM prompt
- The LLM is instructed to:
  - Rank results by best fit for the user's stated preferences
  - Generate a natural-language explanation for each recommendation
  - Optionally produce a brief summary of all top picks

---

## ✅ Acceptance Criteria

- [ ] Dataset is successfully loaded and preprocessed from Hugging Face
- [ ] User input is collected and validated (location, budget, cuisine, rating, extras)
- [ ] Filtering logic correctly narrows down restaurants based on criteria
- [ ] LLM prompt is well-structured and produces coherent ranked recommendations
- [ ] Output displays restaurant name, cuisine, rating, cost, and AI explanation
- [ ] Application handles edge cases (no matching restaurants, invalid input, etc.)

---

## 🛠️ Tech Stack (Suggested)

| Layer | Technology |
|---|---|
| Dataset | Hugging Face Datasets (`datasets` library) |
| Backend / Logic | Python |
| LLM Integration | OpenAI API / Gemini API / HuggingFace Inference |
| Prompt Engineering | LangChain / custom prompt templates |
| UI (optional) | Streamlit / Gradio / CLI |

---

> **Note:** This project is inspired by Zomato's restaurant discovery experience and aims to showcase the power of combining structured data filtering with LLM-based natural language generation for intelligent recommendations.

