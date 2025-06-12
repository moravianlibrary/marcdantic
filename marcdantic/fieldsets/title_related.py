from pydantic import BaseModel

from .common import VariableFieldModel


class TitleStatement(VariableFieldModel):
    title: str
    subtitle: str | None = None


class TitleRelated(BaseModel):
    title_statement: TitleStatement | None = None
