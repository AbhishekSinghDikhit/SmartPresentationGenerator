from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from services import generate_pptx  # Assuming this is in services.py
import uvicorn
import google.generativeai as genai  
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Presentation Generator API")

# Enable CORS with safer configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "https://smart-presentation-generator.vercel.app"],
    allow_credentials=True,
    allow_methods=["POST"],  # Restrict to needed methods
    allow_headers=["Content-Type"],
)

# Gemini API Key validation
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_KEY not found in environment variables")
    raise RuntimeError("GEMINI_API_KEY is required")
genai.configure(api_key=GEMINI_API_KEY)

# Pydantic model for request validation
class PresentationRequest(BaseModel):
    title: str
    author: str
    num_slides: int
    description: Optional[str] = None

def get_ppt_content(title: str, num_slides: int, description: Optional[str] = None) -> list:
    """
    Generate structured PowerPoint content using Gemini API or description.
    
    Args:
        title: Presentation title
        num_slides: Number of slides requested
        description: Optional description to generate content from
    
    Returns:
        List of dicts containing slide data
    """
    structured_slides = []

    try:
        # Use description if provided
        if description and description.strip():
            paragraphs = [p.strip() for p in description.split("\n\n") if p.strip()]
            for i, paragraph in enumerate(paragraphs[:num_slides]):
                bullets = [b.strip() for b in paragraph.split(". ") if b.strip()][:4]
                structured_slides.append({
                    "title": f"Slide {i+1}",
                    "content": bullets or ["No content available"]
                })
            return structured_slides

        # Fallback to Gemini API
        prompt = f"""
        Create a {num_slides}-slide PPT blueprint for "{title}" with:
        - Slide number
        - Title
        - Body (3-5 bullet points)
        Separate each slide with "@". Keep it concise.
        Example:
        Slide 1
        Introduction
        - Point 1
        - Point 2
        - Point 3
        @
        Slide 2
        Main Content
        - Detail 1
        - Detail 2
        - Detail 3
        @
        """

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")

        slides = []
        current_slide = None
        lines = response.text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Slide "):
                if current_slide:
                    slides.append(current_slide)
                current_slide = {"title": "", "content": []}
            elif line == "@":
                continue
            elif current_slide and not current_slide["title"]:
                current_slide["title"] = line
            elif current_slide:
                if line.startswith("- "):  # Handle bullet points explicitly
                    current_slide["content"].append(line[2:].strip())
                elif current_slide["content"]:  # Only add if after bullets started
                    current_slide["content"][-1] += f" {line}"

        if current_slide and current_slide["title"]:
            slides.append(current_slide)

        return slides if slides else [{"title": "Error", "content": ["No content generated"]}]

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return [{"title": "Error", "content": [f"Content generation failed: {str(e)}"]}]

@app.post("/api/generate_presentation", response_model=dict)
async def generate_presentation(request: PresentationRequest):
    """
    Generate a PowerPoint presentation and return its file path.
    """
    try:
        # Validate request
        if request.num_slides <= 0:
            raise HTTPException(status_code=400, detail="Number of slides must be positive")
        if not request.title.strip() or not request.author.strip():
            raise HTTPException(status_code=400, detail="Title and author cannot be empty")

        # Generate content
        ppt_content = get_ppt_content(request.title, request.num_slides, request.description)
        
        if not ppt_content or all(slide.get("title") == "Error" for slide in ppt_content):
            raise HTTPException(status_code=500, detail="Failed to generate presentation content")

        # Generate PPTX
        pptx_path = generate_pptx(request, ppt_content)
        
        if not os.path.exists(pptx_path):
            raise HTTPException(status_code=500, detail="Failed to create presentation file")

        # Return file response instead of just path
        return FileResponse(
            path=pptx_path,
            filename=os.path.basename(pptx_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in generate_presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Default to 10000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)