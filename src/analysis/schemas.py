from pydantic import BaseModel


class DiagramAnalysis(BaseModel):
    diagram_type: str
    components: list[str]
    missing_components: list[str]
    relationships: list[str]
    decision_points: list[str]
    best_practices: list[str]
