from pydantic import BaseModel, Field


class MarcIssue(BaseModel):
    barcode: str
    issuance_type: str = Field(..., alias="issuanceType")
    volume_number: str | None = Field(None, alias="volumeNumber")
    volume_year: str | None = Field(None, alias="volumeYear")
    bundle: str | None

    class Config:
        def to_camel_case(string: str) -> str:
            return "".join(
                word.capitalize() if i else word
                for i, word in enumerate(string.split("_"))
            )

        allow_population_by_field_name = True
        alias_generator = to_camel_case
