from pydantic import BaseModel


class Suggestion(BaseModel):
    id: str
    title: str
    description: str
    category: str
    updated_diagram: str


class EnhancementResponse(BaseModel):
    suggestions: list[Suggestion]
