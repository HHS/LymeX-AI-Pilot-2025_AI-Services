from pydantic import BaseModel, Field


class ChecklistAnswer(BaseModel):
    question_number: str
    question: str
    answer: str


class ChecklistBase:
    answers: list[ChecklistAnswer]


class ChecklistSchema(BaseModel, ChecklistBase): ...
