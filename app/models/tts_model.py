from typing import Optional
from pydantic import BaseModel

class TextToSpeechRequest(BaseModel):
    language: Optional[str] = "en-US"
    gender: Optional[str] = "F"
    model: Optional[str] = ""
    text: str