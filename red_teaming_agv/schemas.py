from pydantic import BaseModel
from typing import Dict, Optional, Union

class ChatInputSchema(BaseModel):
    tool_name: str
    tool_input_data: Union[list, str]

class InputSchema(BaseModel):
    tool_name: str
    tool_input_data: Union[list, str]

class SystemPromptSchema(BaseModel):
    """Schema for system prompts."""
    role: str = "You are a helpful AI assistant."
    persona: Optional[Union[Dict, BaseModel]] = None