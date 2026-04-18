from pydantic import BaseModel


class CreateDocument(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True
