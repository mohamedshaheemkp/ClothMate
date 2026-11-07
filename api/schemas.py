from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MAX_COORD = 20000.0  # pixels; bigger than any real photo


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=MAX_COORD)
    y: float = Field(ge=0, le=MAX_COORD)


class CardCorners(BaseModel):
    """The 4 corners of the reference card, in photo pixels. 'top' is the long edge."""
    model_config = ConfigDict(extra="forbid")
    top_left: Point
    top_right: Point
    bottom_right: Point
    bottom_left: Point


class MeasureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    garment_id: str = Field(pattern=r"^[a-z0-9_]{1,60}$")
    fit: Literal["slim", "regular", "loose"] = "regular"
    method: Literal["scale", "homography"] = "scale"
    card: CardCorners
    points: dict[str, Point] = Field(max_length=40)