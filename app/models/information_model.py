from typing import Optional
from pydantic import BaseModel

class information_model(BaseModel):
    id: int
    voice_name: str
    language: str
    gender: str
    type: str
    platform: Optional[str] = None
    model: str

    #Define como se imprime el objeto
    def __repr__(self):
        return f"AudioModel(id={self.id}, voice_name='{self.voice_name}', language='{self.language}', gender='{self.gender}', type='{self.type}', platform='{self.platform}', model='{self.model}')"

