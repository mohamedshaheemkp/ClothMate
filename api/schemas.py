"""Request/response shapes. Pydantic rejects anything that does not match."""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

MAX_COORD = 20000.0  # pixels; larger than any real photo


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=MAX_COORD)  # NaN / inf fail these checks
    y: float = Field(ge=0, le=MAX_COORD)


class CardCorners(BaseModel):
    """Corners of the reference object in photo pixels. 'top' is the LONG edge."""
    model_config = ConfigDict(extra="forbid")
    top_left: Point
    top_right: Point
    bottom_right: Point
    bottom_left: Point


class MeasureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    garment_id: str = Field(pattern=r"^[a-z0-9_]{1,60}$")
    fit: Literal["slim", "regular", "loose"] = "regular"
    reference: Literal["card", "a4"] = "card"
    user_role: Optional[Literal["customer", "tailor", "staff"]] = None
    card: CardCorners
    points: dict[str, Point] = Field(max_length=40)


class MeasurementOut(BaseModel):
    name: str
    tailor_measure: str
    flat_cm: float
    garment_circumference_cm: Optional[float] = None
    ease_cm: Optional[float] = None
    estimated_body_cm: Optional[float] = None


class MeasureResponse(BaseModel):
    garment_id: str
    fit: str
    method: Optional[str] = "scale"
    reference: str
    cm_per_pixel_at_reference: float
    measurements: list[MeasurementOut]
    warnings: list[str]
    ease_status: str
