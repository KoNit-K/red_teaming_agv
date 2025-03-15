from typing import Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator
from typing import ClassVar
from red_teaming_agv.common.Target import Target

class ChatInputSchema(BaseModel):
    tool_name: str
    tool_input_data: Union[list, str]


class SystemPromptSchema(BaseModel):
    """Schema for system prompts."""
    role: str = "You are a helpful AI assistant."
    persona: Optional[Union[Dict, BaseModel]] = None

class InputSchema(BaseModel):
    tool_name: str
    category: str = Field(default="financial", description=f"Category of the test. eg. {Target.get_all_categories()}")
    index: str = Field(default="0", description="Index of the test, 'all' or a valid integer")
    target: str = Field(default="gpt-4o-mini", description=f"Target model name eg. {Target.ALLOWED_TARGETS}")

    # 获取 Target 类中的允许值
    ALLOWED_CATEGORIES: ClassVar[set] = set(Target.get_all_categories())
    ALLOWED_TARGETS: ClassVar[set] = set(Target.ALLOWED_TARGETS)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in cls.ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{value}'. Use 'help' to see available categories: {cls.ALLOWED_CATEGORIES}")
        return value

    @field_validator("index")
    @classmethod
    def validate_index(cls, value: str, values) -> str:
        category = values.data.get("category", "financial")  # 获取 category，默认为 "financial"

        if value.lower() == "all":
            return value  # 允许 "all"

        try:
            index_num = int(value)
            max_index = Target.get_category_size(category) - 1
            if index_num < 0 or index_num > max_index:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid index '{value}'. Must be between 0 and {max_index} or 'all'.")

        return value

    @field_validator("target")
    @classmethod
    def validate_target(cls, value: str) -> str:
        if value not in cls.ALLOWED_TARGETS:
            raise ValueError(f"Invalid target model '{value}'. Choose from: {cls.ALLOWED_TARGETS}")
        return value
