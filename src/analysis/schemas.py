from typing import Literal

from pydantic import BaseModel

ShapeType = Literal[
    "rectangle",
    "rounded",
    "diamond",
    "cylinder",
    "circle",
    "asymmetric",
    "parallelogram",
    "subroutine",
]


class Component(BaseModel):
    name: str
    shape: ShapeType


class DiagramAnalysis(BaseModel):
    diagram_type: str
    components: list[Component]
    missing_components: list[Component]
    relationships: list[str]
    decision_points: list[str]
    best_practices: list[str]
