# VERITAS Deployment Guide

This guide covers deploying the **FastAPI Backend on Render** and the **TanStack React Frontend on Vercel**.

---

## 1. Deploy the Backend on Render

### Step 1: Create the Web Service
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Blueprint** (or **Web Service**).
3. Connect your GitHub repository (`Sushrut-Kane/VERITAS`).
4. If using **Blueprint**, Render automatically reads [`render.yaml`](./render.yaml).
5. If creating a **Web Service** manually:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 2: Configure Environment Variables on Render
Add the following in the **Environment** tab on Render:
- `DATABASE_URL`: `postgresql+asyncpg://postgres:mJ3jh6Couc1XSns0@db.dnzccqkfaznunitfbixj.supabase.co:5432/postgres` (or your pooled connection string)
- `GROQ_API_KEY`: `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`
- `GROQ_MODEL`: `openai/gpt-oss-120b`
- `CORS_ORIGINS`: `["*"]`
- `ENVIRONMENT`: `production`
- `JWT_SECRET`: `change-me-in-production`

Click **Deploy**. Copy your public Render URL once deployed (e.g. `https://veritas-backend.onrender.com`).

---

## 2. Deploy the Frontend on Vercel

### Step 1: Import Project into Vercel
1. Log into [Vercel](https://vercel.com/) and click **Add New...** $\rightarrow$ **Project**.
2. Import your GitHub repository (`Sushrut-Kane/VERITAS`).

### Step 2: Configure Project Settings on Vercel
1. **Framework Preset**: `Vite` (or `Other`)
2. **Root Directory**: Click `Edit` and select `frontend` (or leave default if using root `vercel.json`).
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist/client`
5. **Environment Variables**:
   - Add **`VITE_API_BASE_URL`**: `https://<your-render-service-name>.onrender.com`

### Step 3: Deploy
Click **Deploy**. Vercel will build the frontend and give you a live production URL (e.g. `https://veritas.vercel.app`).

---

## 3. Dataset & Security
- All local CSV files (`*.csv`, `Unihack_*.csv`) and environment secret files (`.env`, `.env.*`) are strictly ignored in `.gitignore`.
- Reference taxonomy and catalog specs are queried live from Supabase PostgreSQL.
