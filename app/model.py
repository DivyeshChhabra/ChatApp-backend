# Importing Python Libraries.
from pydantic import BaseModel


class ConversationRequest(BaseModel):
    body: str