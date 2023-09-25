from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class LlmModelInfo:
    source: str = "replicate"
    model: str = ""

    def __str__(self):
        return f"source: {self.source}\n\nmodel: {self.model.split(':')[0]}"

    def to_dict(self):
        return {
            "source": self.source,
            "model": self.model
        }


class WriteFileInput(BaseModel):
    filename: str = Field()
    content: str = Field()
