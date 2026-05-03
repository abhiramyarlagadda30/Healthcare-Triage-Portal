# PROMPTS.md - AI Development Challenges & Solutions

## Challenge 1: LLM Integration & JSON Parsing Issues

**The Problem:**
Initial prompt to AI: "Create a function that uses LLM to parse medical transcripts"

The AI generated code that returned plain text responses instead of structured JSON, and didn't handle API failures gracefully. The parser would break completely if the LLM API returned an error.

**How I Fixed It:**
I refined the prompt to be more specific:
"Create a robust LLM parser function that:
1. Always returns valid JSON with exact schema: {symptoms: [], vitals: {}, plan: "", follow_up: ""}
2. Implements fallback to rule-based parsing when LLM fails
3. Includes error handling for API timeouts
4. Uses temperature=0.1 for consistent outputs"

**Result:** The improved code now includes try-catch blocks, a fallback parser using regex, and ensures the response always matches the Pydantic schema.

---

## Challenge 2: CORS Configuration & API Integration

**The Problem:**
The AI initially set up the FastAPI backend without proper CORS headers. When the React frontend tried to call the API, we got: "Access-Control-Allow-Origin" errors.

The AI's first solution was to add `allow_origins=["*"]` which is insecure, and the React proxy wasn't configured correctly.

**How I Fixed It:**
I prompted: "Configure CORS properly for production and development, using environment-specific origins. Add the proxy setting in package.json and explain the security implications."

**Solution implemented:**
- Specific CORS origins: ["http://localhost:3000", "http://localhost:3001"]
- Added proxy in package.json
- Created environment variables for API URLs
- Implemented proper error handling for network requests

---

## Challenge 3: Risk Prediction Model Training

**The Problem:**
The AI first tried to use a complex deep learning model that required external datasets and had long training times. It generated code that tried to load a pre-trained model from a non-existent file.

**How I Fixed It:**
I changed my prompt strategy: "Create a lightweight, rule-based risk prediction model using synthetic data. Don't rely on external files. Use Random Forest with generated realistic medical data."

**The fix:**
- Generated synthetic training data based on medical guidelines
- Used Random Forest classifier (lightweight, no external dependencies)
- Implemented clear risk scoring rules based on vitals
- Added model as a singleton instance to avoid re-training

This approach works immediately without needing to download or train external models.