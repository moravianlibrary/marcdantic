from .common import VariableFieldSelector


class TitleStatement(VariableFieldSelector):
    @property
    def title(self) -> str | None:
        return self._select("245", "a")

    @property
    def subtitle(self) -> str | None:
        return self._select("245", "b")


class TitleRelated(VariableFieldSelector):
    @property
    def title_statement(self) -> TitleStatement:
        return TitleStatement(self._variable_fields)
