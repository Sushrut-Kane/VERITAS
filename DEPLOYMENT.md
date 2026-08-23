# VERITAS Deployment Guide

This guide covers deploying the **FastAPI Backend on Render** and the **TanStack React Frontend on GitHub / GitHub Pages**.

---

## 1. Deploying the Backend on Render

### Method A: 1-Click / Blueprint Deployment (Recommended)
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Blueprint**.
3. Connect your GitHub repository (`Sushrut-Kane/VERITAS`).
4. Render will automatically detect [`render.yaml`](./render.yaml).
5. Fill in the required secret environment variables:
   - `DATABASE_URL`: `postgresql+asyncpg://postgres:mJ3jh6Couc1XSns0@db.dnzccqkfaznunitfbixj.supabase.co:5432/postgres` (or your pooled 6543 connection string)
   - `GROQ_API_KEY`: `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`
6. Click **Apply**. Render will build and deploy your backend with a public URL like `https://veritas-backend.onrender.com`.

### Method B: Manual Web Service
1. Click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repo.
3. Configure the following fields:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables under the **Environment** tab:
   - `PYTHON_VERSION`: `3.12.0`
   - `ENVIRONMENT`: `production`
   - `DATABASE_URL`: `postgresql+asyncpg://postgres:mJ3jh6Couc1XSns0@db.dnzccqkfaznunitfbixj.supabase.co:5432/postgres`
   - `GROQ_API_KEY`: `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`
   - `GROQ_MODEL`: `openai/gpt-oss-120b`
   - `CORS_ORIGINS`: `["*"]`
   - `JWT_SECRET`: `change-me-in-production`
5. Click **Create Web Service**.

---

## 2. Deploying the Frontend on GitHub

### GitHub Pages (Automated via GitHub Actions)
1. Go to your GitHub repository **Settings** $\rightarrow$ **Pages**.
2. Under **Build and deployment** $\rightarrow$ **Source**, select **GitHub Actions**.
3. Under **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ **Repository secrets**, add:
   - `VITE_API_BASE_URL`: `https://<your-render-service-name>.onrender.com`
4. Every push to the `main` branch will automatically run the [`.github/workflows/deploy-frontend.yml`](./.github/workflows/deploy-frontend.yml) workflow, build the frontend, and publish it to `https://<username>.github.io/VERITAS/`.

---

## 3. Security & Dataset Note
- All CSV files (`*.csv`, `Unihack_*.csv`) and environment secrets (`.env`, `.env.*`) are ignored in `.gitignore` and will never be pushed to the repository.
- Reference data and catalog items are stored in Supabase PostgreSQL.
