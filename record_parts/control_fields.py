from datetime import datetime

from pydantic import BaseModel

ControlNumber = str
ControlNumberIdentifier = str


class FixedLengthDataElements(BaseModel):
    date_entered: datetime


class ControlFields(BaseModel):
    control_number: ControlNumber
    control_number_identifier: ControlNumberIdentifier
    latest_transaction: datetime
    fixed_length_data_elements: FixedLengthDataElements
