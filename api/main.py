# Standard library import for operating system interactions
import os

# Third-party imports for web framework and data validation
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Internal import from the core phonetic matching package
from phonetic_match.matcher import PhoneticMatcher
from phonetic_match.normalizer import ScoreNormalizer

# Initialize the FastAPI application instance
app = FastAPI()
# Initialize the phonetic matching engine global instance
matcher = PhoneticMatcher()

# Configure Cross-Origin Resource Sharing (CORS) 
# This allows the API to be called from different domains/ports (important for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Permit requests from any origin
    allow_credentials=True,    # Permit cookies and credentials
    allow_methods=["*"],       # Permit all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # Permit all custom headers
)

# Calculate the absolute path to the 'frontend' directory relative to this script's location
# This ensures the server can find index.html even if run from a different CWD.
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"
)

# Define the expected JSON structure for incoming scoring requests
class ScoreRequest(BaseModel):
    name1: str  # The target name string
    name2: str  # The reference name string

# Route: Serve the login page at the root URL (http://localhost:8000/)
@app.get("/")
async def read_login():
    # Return the login.html file directly as the response
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

# Route: Explicitly serve the main application page
# Useful for direct navigation or post-login redirection
@app.get("/index.html")
async def read_index():
    # Return the index.html file directly as the response
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# API Route: Handle phonetic matching requests
@app.post("/match")
async def calculate_score(payload: ScoreRequest):
    """
    Receives two names, uses PhoneticMatcher to calculate the similarity score.
    """
    # Execute the core matching logic
    result = matcher.match(payload.name1, payload.name2)
    
    # Get the raw numeric score
    score = result.get("F1", 0.0)
    
    # Get the human-readable label based on the score
    label = ScoreNormalizer.get_label(score)
    
    # Return both the score and the label to the frontend
    return {
        "similarity_score": score,
        "similarity_label": label
    }

# Mount the static file handler last.
# This serves all other files (JS, CSS, Images) within the FRONTEND_DIR.
# We mount it at '/' so that assets can be linked as src="/script.js"
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
