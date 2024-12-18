from typing import Optional
from pydantic import BaseModel

class TextToSpeechRequest(BaseModel):
    language: Optional[str] = "English"
    gender: Optional[str] = "F"
    model: Optional[int] = ""
    text: str