from pydantic import BaseModel


class PerguntaRequest(BaseModel):
    pergunta: str


class FeedbackRequest(BaseModel):
    session_id: str | None = None
    score: int