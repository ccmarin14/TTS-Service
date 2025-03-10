from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Gender(str, Enum):
    FEMALE = "F"
    MALE = "M"

class VoiceType(str, Enum):
    ADULT = "adult"
    CHILD = "child"
    ROBOT = "robot"

class TextToSpeechRequestById(BaseModel):
    read: str = Field(
        default="", 
        description="Texto usado para la lectura"
    )
    text: str = Field(
        default="", 
        description="Texto original"
    )

class TextToSpeechRequestByName(TextToSpeechRequestById):
    language: Optional[str] = Field(
        default="", 
        description="Taquigrafía internacional, ejemplo: 'en-US', 'es-ES'", 
    )
    model: Optional[str] = Field(
        default="", 
        description="Nombre del modelo"
    )

class TextToSpeechRequestOptional(TextToSpeechRequestById):
    language: Optional[str] = Field(
        default="", 
        description="Taquigrafía internacional, ejemplo: 'en-US', 'es-ES'", 
    )
    gender: Optional[Gender] = Field(
        default=Gender.FEMALE, 
        description="Hombre:'M', Mujer:'F'"
    )
    type: Optional[VoiceType] = Field(
        default=VoiceType.ADULT, 
        description="Adulto:'adult', Niño:'child', Robotizada:'robot'"
    )