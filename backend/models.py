from pydantic import BaseModel

class PresentationRequest(BaseModel):
    title: str
    author: str
    num_slides: int
    description: str  # Can be empty if AI is used
    useAI: bool
