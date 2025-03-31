from typing import Optional
from pydantic import BaseModel

class CreateVoiceModel(BaseModel):
    voice_name: str
    language: str
    gender: str
    type: str
    platform: str
    model: str
    metadata: Optional[dict] = None

    #Define como se imprime el objeto
    def __repr__(self):
        return f"AudioModel(voice_name='{self.voice_name}', language='{self.language}', gender='{self.gender}', type='{self.type}', platform='{self.platform}', model='{self.model}')"

class InformationModel(CreateVoiceModel):
    id: int

    #Define como se imprime el objeto
    def __repr__(self):
        return f"AudioModel(id={self.id}, voice_name='{self.voice_name}', language='{self.language}', gender='{self.gender}', type='{self.type}', platform='{self.platform}', model='{self.model}')"

