from pydantic import BaseModel


class ChecklistAnswer(BaseModel):
    question_number: str
    question: str
    answer: str


class ChecklistBase:
    answers: list[ChecklistAnswer]


class ChecklistSchema(BaseModel, ChecklistBase): ...
