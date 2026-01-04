# 🚜 SIH 2025: Farmer Assistance Platform Backend

FastAPI backend for Smart India Hackathon 2025—empowering Indian farmers with AI-driven crop diagnostics, voice queries, and secure data management.

## 🌾 Key Features
- 🔐 JWT Authentication & User Management
- 📁 Image Upload for Crop Disease Detection (AI integration ready)
- 🎤 Voice Recording & Speech-to-Text for Farming Queries
- 🗺 Location Services for Geo-Targeted Advice
- 📊 Full REST APIs with Swagger Docs

## 🛠 Setup & Run
1. Clone: `git clone https://github.com/MOKSH90/App-Backend.git && cd App-Backend`
2. Install: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --reload`
4. API Docs: http://127.0.0.1:8000/docs

## 📁 Structure
- `main.py`: FastAPI app
- `auth/`: Auth routes, DB models, utils
- `requirements.txt`: Deps (FastAPI, SQLAlchemy, Pydantic, etc.)

## 🚀 Deploy
- Free on Render.com: Connect GitHub repo, set build: `pip install -r requirements.txt`, start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Env vars: Add DATABASE_URL, JWT_SECRET in Render dashboard.

## 🤝 Contribute
Fork > Branch > PR. Ideal for GSoC/ML projects!

---
SIH 2025 | Built with ❤️ | Open Source ❤️
