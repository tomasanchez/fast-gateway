"""Commands
A command represents an intent to change the state of the system, it is a message that requests some action to be taken.

Commands are passed to command handlers, which interpret them and execute
the corresponding actions to produce new events that update the system state.

Commands should be immutable, and their properties should be as minimal as possible.
"""
from pydantic import Field

from app.domain.schemas import CamelCaseModel


class RegisterUser(CamelCaseModel):
    """
    A command to create a new user.
    """
    username: str = Field(description="The user email.", example="johndoe")
    password: str = Field(description="The user password.")
    name: str | None = Field(description="The user name.", example="John")
    last_name: str | None = Field(description="The user last name.", example="Doe")
