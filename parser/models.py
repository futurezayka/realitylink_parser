from pydantic import BaseModel
from typing import List, Optional


class Residence(BaseModel):
    link: str
    title: str
    region: str
    address: str
    description: str
    publish_date: Optional[str] = None
    price: Optional[float]
    bedrooms: Optional[int]
    floor_area: Optional[float]
    image_links: List[str]
