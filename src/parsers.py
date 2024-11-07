from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class imageQualitySingle(BaseModel):
    quality: str = Field(description="quality of the image")
    discard: bool = Field(description="whether to discard the image")
    note: str = Field(description="note about the image")


class imageQuality(BaseModel):
    images: List[imageQualitySingle] = Field(
        description="list of images with quality and discard status"
    )


class Final_report(BaseModel):
    title: str = Field(description="title of the product")
    description: str = Field(description="description of the product")
    category: str = Field(description="category of the product")
    price: float = Field(description="price of the product")
    currency: str = Field(description="currency of the product")
    condition: str = Field(description="condition of the product")
    location: str = Field(description="location of the product")
    brand: str = Field(description="brand of the product")
    model: str = Field(description="model of the product")


def get_parsers():
    return {
        "final_report": JsonOutputParser(pydantic_object=Final_report),
        "image_quality": JsonOutputParser(pydantic_object=imageQuality),
    }
