from typing import TypedDict


class ValidationErrorItem(TypedDict):
    location: str
    message: str


class ValidationError(TypedDict):
    type: str
    errors: list[ValidationErrorItem]
