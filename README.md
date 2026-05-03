# 🏥 Intelligent Patient Triage & Voice-Notes Portal

An AI-powered healthcare dashboard for patient risk prediction and clinical note structuring.

## Features
- **Risk Triage** — Enter patient vitals to get a Low / Medium / High risk score via a Random Forest model
- **Clinical Notes Parser** — Paste messy voice-to-text doctor notes; Groq LLM extracts structured JSON

---

## Prerequisites
- Python 3.11+
- Node.js 18+
- A free Groq API key from [console.groq.com](https://console.groq.com)

---

## Setup & Run Locally

### 1. Add your Groq API key
Edit `Backend/.env`:
```
GROQ_API_KEY=your_actual_key_here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

```

### 2. Start the Backend
```bash
cd Backend
pip install -r requirements.txt
uvicorn App:app --reload --port 8000
```
Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 3. Start the Frontend
```bash
cd Frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

---

## Run with Docker

```bash
# Add your key to Backend/.env first, then:
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/triage` | Accepts patient vitals, returns risk level |
| POST | `/summarize` | Accepts transcript text, returns structured JSON |

### Example `/triage` request
```json
{
  "age": 65,
  "systolicBP": 150,
  "diastolicBP": 95,
  "heartRate": 88,
  "temperature": 98.6
}
```

### Example `/summarize` request
```json
{
  "transcript": "Patient feels dizzy, BP is 140/90, suggest rest and follow up in 10 days."
}
```

---

## AWS Deployment

### Option 1 — AWS App Runner (Recommended for Backend)
1. Push code to GitHub
2. In AWS Console → App Runner → Create Service → Source: GitHub
3. Set **Source directory** to `Backend/`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn App:app --host 0.0.0.0 --port 8080`
6. Add `GROQ_API_KEY` and `ALLOWED_ORIGINS` under Environment Variables
7. Update `REACT_APP_API_URL` in frontend to the App Runner URL

### Option 2 — AWS Amplify (Frontend)
1. Push `Frontend/` to GitHub
2. AWS Amplify → New App → Connect GitHub repo
3. Set build settings: `npm run build`, publish directory: `build`
4. Set `REACT_APP_API_URL` environment variable to your backend URL
