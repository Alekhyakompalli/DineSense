# Deployment Plan: DineSense (Zomato AI Recommendation Engine)

This document provides a step-by-step production deployment guide for the **DineSense** platform:
- **Backend (FastAPI REST Service)**: Deployed on **Railway**
- **Frontend (Next.js 14 Web Application)**: Deployed on **Vercel**

---

## 1. System Architecture & Topology

```
                       ┌────────────────────────────────────────┐
                       │           End User Browser             │
                       └───────────────────┬────────────────────┘
                                           │ HTTPS
                                           ▼
                       ┌────────────────────────────────────────┐
                       │          Vercel Edge Network           │
                       │    Next.js 14 App Router Frontend       │
                       │  (Dark-theme Midnight Glassmorphism)   │
                       └───────────────────┬────────────────────┘
                                           │ Client Fetch (HTTPS)
                                           ▼
                       ┌────────────────────────────────────────┐
                       │             Railway Service            │
                       │          FastAPI (Uvicorn / Python)    │
                       │    - /api/health                       │
                       │    - /api/metadata                     │
                       │    - /api/recommendations              │
                       └──────┬──────────────────────────┬──────┘
                              │                          │
                              ▼                          ▼
               ┌────────────────────────┐      ┌────────────────────────┐
               │    HuggingFace Hub     │      │   Google Gemini API    │
               │ (12,140 Clean Records) │      │ (gemini-2.5-flash LLM) │
               └────────────────────────┘      └────────────────────────┘
```

---

## 2. Pre-Deployment Checklist

Before deploying, ensure you have:
1. **GitHub / GitLab Repository**: The codebase committed and pushed to a remote repository.
2. **Railway Account**: [railway.app](https://railway.app) (Free tier or Developer plan).
3. **Vercel Account**: [vercel.com](https://vercel.com) (Hobby or Pro plan).
4. **Google Gemini API Key**: Obtained from [Google AI Studio](https://aistudio.google.com/app/apikey).
5. **Verified Local Repo Files**:
   - [`Procfile`](file:///c:/Nextleap/Zomato/Procfile): `web: uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}`
   - [`Dockerfile`](file:///c:/Nextleap/Zomato/Dockerfile): Container configuration with healthcheck and dynamic port binding.
   - [`requirements.txt`](file:///c:/Nextleap/Zomato/requirements.txt): Python dependencies (`fastapi`, `uvicorn`, `google-generativeai`, etc.).
   - [`frontend/package.json`](file:///c:/Nextleap/Zomato/frontend/package.json): Next.js build scripts and dependencies.

---

## 3. Phase 1: Deploy Backend on Railway

Railway will host the FastAPI service, download the preprocessed HuggingFace dataset into memory on startup, and interface with Google Gemini.

### Step 1.1: Create New Project on Railway
1. Log into your [Railway Dashboard](https://railway.app/dashboard).
2. Click **"+ New Project"**.
3. Select **"Deploy from GitHub repo"**.
4. Choose your `Zomato` repository.

### Step 1.2: Configure Service Settings
Railway will automatically detect either the `Dockerfile` or `Procfile`.
- **Root Directory**: Leave as `/` (repository root).
- **Builder**: Nixpacks (default) or Dockerfile (both are fully supported).
- **Healthcheck Path**: `/` or `/api/health`.

### Step 1.3: Configure Environment Variables
In your Railway Service dashboard, navigate to the **Variables** tab and add:

| Variable Name | Required | Example / Recommended Value | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** | `AIzaSy...` | Your active Google Gemini API key. |
| `LLM_PROVIDER` | No | `gemini` | Default LLM provider. |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model name. |
| `DATASET_NAME` | No | `ManikantaReddy09/Zomato-Bengaluru-Restaurants` | HuggingFace dataset repository. |
| `TOP_N_CANDIDATES` | No | `20` | Pre-filtering candidate pool size. |
| `TOP_N_RECOMMENDATIONS`| No | `5` | Final recommendation count. |
| `ALLOWED_ORIGINS` | No | `*` *(or your Vercel URL once deployed)* | Comma-separated list of allowed CORS origins. |

> **Note on Port**: Railway automatically assigns a dynamic port and sets the `$PORT` environment variable. Our `Procfile` and `Dockerfile` automatically bind to `${PORT:-8000}`.

### Step 1.4: Generate Public Domain
1. In Railway, click on your deployed service.
2. Go to **Settings** > **Networking** > **Public Networking**.
3. Click **"Generate Domain"** (e.g. `zomato-backend-production.up.railway.app`).
4. Copy this URL (ensure it starts with `https://`).

### Step 1.5: Verify Railway Deployment
Run the following test commands using your generated domain:

```bash
# 1. Root diagnostic endpoint
curl https://<YOUR-RAILWAY-DOMAIN>.up.railway.app/

# Expected response:
# {"service":"Zomato AI DineSense API","status":"online","endpoints":["/api/health","/api/metadata","/api/recommendations"],"docs":"/docs"}

# 2. Health check (loads dataset)
curl https://<YOUR-RAILWAY-DOMAIN>.up.railway.app/api/health

# Expected response:
# {"status":"healthy","llm_provider":"gemini","model":"gemini-2.5-flash","records_loaded":12140,"dataset":"..."}
```

---

## 4. Phase 2: Deploy Frontend on Vercel

Vercel will host the Next.js 14 frontend on its edge network with automatic SSL, preview deployments, and asset optimization.

### Step 2.1: Import Project to Vercel
1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **"Add New..."** > **"Project"**.
3. Select and import your `Zomato` repository.

### Step 2.2: Configure Root Directory (CRITICAL)
Because the Next.js application lives inside the `frontend` subfolder:
1. In the **Configure Project** screen, find **Root Directory**.
2. Click **"Edit"** and select or type: `frontend`.
3. Vercel will immediately detect **Next.js** as the Framework Preset.

### Step 2.3: Configure Build & Output Settings
The detected defaults should be:
- **Framework Preset**: `Next.js`
- **Build Command**: `next build` (or leave default toggle ON)
- **Output Directory**: `.next` (or leave default toggle ON)
- **Install Command**: `npm install` (or leave default toggle ON)

### Step 2.4: Set Environment Variables
Under **Environment Variables**, add:

| Key | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<YOUR-RAILWAY-DOMAIN>.up.railway.app` | Point to your live Railway backend (no trailing slash). |

### Step 2.5: Deploy
1. Click **"Deploy"**.
2. Vercel will install dependencies, compile the TypeScript source, optimize assets, and deploy the application.
3. Once completed, Vercel provides your live URL (e.g. `https://zomato-dinesense.vercel.app`).

---

## 5. Phase 3: Post-Deployment Handshake & Security Tightening

### Step 3.1: Tighten CORS on Railway
Once you have your production Vercel domain:
1. Go to your **Railway Dashboard** > Service > **Variables**.
2. Update or add `ALLOWED_ORIGINS`:
   ```env
   ALLOWED_ORIGINS=https://<YOUR-VERCEL-DOMAIN>.vercel.app,http://localhost:3000
   ```
3. Railway will automatically redeploy the service with the restricted CORS whitelist.

### Step 3.2: End-to-End Verification Flow
1. Open `https://<YOUR-VERCEL-DOMAIN>.vercel.app` in your browser.
2. Confirm the top header displays:
   - Green pulse badge: **"Powered by Gemini 2.5 Flash"**
   - Database pill: **"12,140 Curated Restaurants"**
3. Select a location from the dropdown (e.g., `Indiranagar`, `Koramangala`, or `Brigade Road`).
4. Select budget tier and cuisines.
5. Click **"Synthesize Recommendations"**.
6. Verify that:
   - Skeleton loading cards appear smoothly.
   - 5 ranked recommendations display with match score badges, ratings, Unsplash imagery, and AI rationale.
   - Menu modal opens and links to the official Zomato restaurant listing.

---

## 6. Troubleshooting & Edge Cases

| Issue | Root Cause | Solution |
|---|---|---|
| **Vercel Build Error: Cannot find package.json** | Root Directory not set to `frontend` | In Vercel Project Settings > General, set **Root Directory** to `frontend` and trigger a redeploy. |
| **CORS error: Blocked by CORS policy** | Backend not allowing Vercel domain | Ensure `ALLOWED_ORIGINS` on Railway includes your exact Vercel domain (e.g. `https://dinesense.vercel.app`) without trailing slash, or set to `*`. |
| **Timeout on first request (/api/health)** | Initial Hugging Face download takes ~10-15s | Railway allows up to 5 minutes for startup. Once cached in RAM, subsequent requests return in <50ms. |
| **Recommendation synthesis returns 500** | Missing or invalid `GEMINI_API_KEY` | Verify `GEMINI_API_KEY` in Railway Variables and check Railway runtime logs. |
| **Rate limit 429 from Gemini** | API quota exceeded | The backend automatically implements fallback to top-rated candidate restaurants if LLM rate limits are encountered. Consider upgrading to a paid tier in Google AI Studio if high traffic is expected. |

---

## 7. CI/CD & Ongoing Maintenance

- **Automated Deployments**: Both Railway and Vercel automatically redeploy on every `git push` to your `main` branch.
- **Rollback Support**:
  - **Vercel**: Instant rollbacks with zero downtime via the **Deployments** tab.
  - **Railway**: Rollback to any previous deployment with 1-click in the **Deployments** history.
- **Monitoring**:
  - Railway provides CPU, memory, and stdout/stderr stream logs in real time.
  - Vercel provides Speed Insights and Edge Analytics.

