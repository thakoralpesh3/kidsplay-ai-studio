# 🌐 24/7 Online Cloud Deployment Guide (Always Accessible When Laptop is Off)

To access **KidsPlay AI Studio** online from any phone, tablet, iPad, or computer in the world **even when your laptop is completely powered off**, host it on a free 24/7 cloud platform.

We have already prepared all the deployment files (`Dockerfile`, `render.yaml`, `Procfile`, `requirements.txt`). Here are the best free options:

---

## 🌟 Method 1: Hugging Face Spaces (100% Free, Permanent 24/7 Online) — ⭐ Recommended

Hugging Face Spaces provides a permanent free HTTPS URL, runs 24/7 without shutting down, and supports full Docker/FastAPI apps.

### Quick Steps:
1. Go to **[huggingface.co](https://huggingface.co/)** and create a free account.
2. Click **New Space** (or go to `https://huggingface.co/new-space`).
3. Fill in:
   - **Space Name**: `kidsplay-ai-studio`
   - **License**: `MIT`
   - **Space SDK**: Choose **Docker** $\rightarrow$ **Blank**
   - **Space Hardware**: **Free (CPU Basic)**
4. In your space settings $\rightarrow$ **Variables and Secrets**:
   - Add Secret: `GEMINI_API_KEY` = `your_gemini_api_key_here`
5. Push the code from your laptop to the space:
   ```bash
   cd /home/alpesh/kids-game-studio
   git init
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/kidsplay-ai-studio
   git add .
   git commit -m "Deploy KidsPlay AI Studio 24/7"
   git push space main --force
   ```
6. **Done!** Your studio is live at:
   `https://YOUR_USERNAME-kidsplay-ai-studio.hf.space`

---

## 🚀 Method 2: Render.com (1-Click Free Web Service)

1. Push your folder to a private or public GitHub repository:
   ```bash
   cd /home/alpesh/kids-game-studio
   git init
   git add .
   git commit -m "KidsPlay Studio Cloud"
   # Push to your GitHub account (e.g. github.com/your-username/kidsplay-ai-studio)
   ```
2. Go to **[render.com](https://render.com/)** and create a free account.
3. Click **New $\rightarrow$ Web Service** and select your GitHub repository.
4. Render will automatically read `render.yaml` and configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add:
   - `GEMINI_API_KEY`: `your_gemini_api_key_here`
   - `DEFAULT_LANGUAGE`: `gu-IN`
6. Click **Create Web Service**.
7. In ~2 minutes, your link will be live: `https://kidsplay-ai-studio.onrender.com`!

---

## ⚡ Method 3: Google Cloud Run (Free Tier - 2 Million Requests/Month)

If you have Google Cloud SDK (`gcloud`) installed:
```bash
cd /home/alpesh/kids-game-studio
gcloud run deploy kidsplay-ai-studio \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your_gemini_api_key_here",DEFAULT_LANGUAGE="gu-IN"
```
It gives you an official Google HTTPS link (e.g. `https://kidsplay-ai-studio-xxxx.a.run.app`) that stays online 24/7 forever.

---

## 📱 Adding to Phone / Tablet Home Screen as an App (PWA)

Once hosted online:
1. Open your online link (e.g. `https://your-app.hf.space`) in **Chrome** on Android or **Safari** on iPhone/iPad.
2. Tap the browser menu $\rightarrow$ **"Add to Home Screen"** (અથવા **"હોમ સ્ક્રીન પર ઉમેરો"**).
3. Kids can tap the icon anytime like a native mobile game app!
