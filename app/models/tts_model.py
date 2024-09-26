from typing import Optional
from pydantic import BaseModel

class TextToSpeechRequest(BaseModel):
    text: str
    model: Optional[int] = None