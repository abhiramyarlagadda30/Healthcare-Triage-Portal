from dotenv import load_dotenv
load_dotenv()  # Must be first, before any os.getenv() calls

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
import json
import re
from model import risk_model

# Groq LLM client
try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception:
    groq_client = None

app = FastAPI(title="Healthcare Triage Portal")

# CORS — reads from env so it works in both dev and production (AWS)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class VitalsInput(BaseModel):
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    systolic_bp: int = Field(..., alias="systolicBP", ge=50, le=250)
    diastolic_bp: int = Field(..., alias="diastolicBP", ge=30, le=150)
    heart_rate: int = Field(..., alias="heartRate", ge=30, le=200)
    temperature: float = Field(..., ge=90, le=110)

    class Config:
        populate_by_name = True

class TriageResponse(BaseModel):
    risk_level: str
    risk_score: int
    recommendations: List[str]
    vital_signs_summary: Dict

class TranscriptInput(BaseModel):
    transcript: str = Field(..., min_length=5)

class StructuredReport(BaseModel):
    symptoms: List[str]
    vitals: Dict[str, str]
    plan: str
    follow_up: str
    medications: Optional[List[str]] = []
    diagnosis: Optional[str] = ""


def parse_transcript_with_llm(transcript: str) -> dict:
    """Use LLM to structure messy doctor notes into JSON"""

    if not groq_client:
        return fallback_parser(transcript)

    prompt = f"""Extract medical information from this doctor's transcript and return ONLY valid JSON.

Transcript: "{transcript}"

Return JSON with this exact structure:
{{
    "symptoms": ["list", "of", "symptoms"],
    "vitals": {{"bp": "value", "hr": "value", "temp": "value"}},
    "plan": "treatment plan",
    "follow_up": "X days/weeks",
    "medications": ["medicine1", "medicine2"],
    "diagnosis": "tentative diagnosis"
}}

Rules:
- If information is missing, use empty string or empty array
- Do NOT include any explanation, markdown, or code blocks
- Return ONLY the raw JSON object, nothing else
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code blocks if LLM wraps response in them
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        # Extract JSON object even if there's surrounding text
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in LLM response")

        result = json.loads(json_match.group())

        # Ensure all required keys exist with safe defaults
        result.setdefault("symptoms", [])
        result.setdefault("vitals", {})
        result.setdefault("plan", "")
        result.setdefault("follow_up", "")
        result.setdefault("medications", [])
        result.setdefault("diagnosis", "")

        # Convert any None values to empty string/list
        if result["symptoms"] is None:
            result["symptoms"] = []
        if result["medications"] is None:
            result["medications"] = []
        if result["diagnosis"] is None:
            result["diagnosis"] = ""
        if result["plan"] is None:
            result["plan"] = ""
        if result["follow_up"] is None:
            result["follow_up"] = ""

        # Ensure vitals values are all strings
        result["vitals"] = {
            k: str(v) for k, v in result["vitals"].items() if v is not None
        }

        return result

    except Exception as e:
        print(f"LLM parsing error: {e}")
        return fallback_parser(transcript)


def fallback_parser(transcript: str) -> dict:
    """Rule-based fallback parser when LLM is unavailable"""
    text = transcript.lower()

    symptoms = []
    common_symptoms = ["dizzy", "fever", "cough", "headache", "pain", "nausea", "fatigue", "vomiting", "swelling"]
    for symptom in common_symptoms:
        if symptom in text:
            symptoms.append(symptom)

    bp_match = re.search(r'(\d{2,3})/(\d{2,3})', text)
    bp_value = bp_match.group(0) if bp_match else "unknown"

    follow_up = "7 days"
    days_match = re.search(r'(\d+)\s*days?', text)
    if days_match:
        follow_up = f"{days_match.group(1)} days"

    meds = []
    known_meds = ["aspirin", "paracetamol", "ibuprofen", "metformin", "lisinopril", "amoxicillin"]
    for med in known_meds:
        if med in text:
            meds.append(med)

    return {
        "symptoms": symptoms,
        "vitals": {"bp": bp_value},
        "plan": "Further evaluation needed",
        "follow_up": follow_up,
        "medications": meds,
        "diagnosis": "Under investigation"
    }


# API Endpoints
@app.get("/")
def root():
    return {"message": "Healthcare Triage Portal API", "status": "running"}


@app.post("/triage", response_model=TriageResponse)
async def triage_patient(vitals: VitalsInput):
    """Predict patient risk level based on vitals"""

    # Guard: reject Celsius input — 37°C would pass the 90–110 range check silently
    if vitals.temperature < 95:
        raise HTTPException(
            status_code=422,
            detail="Temperature must be in Fahrenheit (normal range: 95–105°F). Did you enter a Celsius value?"
        )

    try:
        risk_level = risk_model.predict(
            age=vitals.age,
            systolic_bp=vitals.systolic_bp,
            diastolic_bp=vitals.diastolic_bp,
            heart_rate=vitals.heart_rate,
            temperature=vitals.temperature
        )

        risk_scores = {"Low": 1, "Medium": 2, "High": 3}

        if risk_level == "High":
            recommendations = ["Immediate hospitalization", "Cardiology consult", "ICU monitoring"]
        elif risk_level == "Medium":
            recommendations = ["Schedule follow-up in 48 hours", "Monitor vitals", "Medication adjustment"]
        else:
            recommendations = ["Routine follow-up", "Lifestyle modifications", "Continue current medications"]

        return TriageResponse(
            risk_level=risk_level,
            risk_score=risk_scores[risk_level],
            recommendations=recommendations,
            vital_signs_summary={
                "age": vitals.age,
                "blood_pressure": f"{vitals.systolic_bp}/{vitals.diastolic_bp}",
                "heart_rate": vitals.heart_rate,
                "temperature": vitals.temperature
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/summarize", response_model=StructuredReport)
async def summarize_notes(transcript_data: TranscriptInput):
    """Convert messy voice notes to structured medical report"""
    try:
        structured_data = parse_transcript_with_llm(transcript_data.transcript)
        return StructuredReport(**structured_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parsing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)