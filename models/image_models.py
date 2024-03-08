from pydantic import BaseModel, Field
from typing import List

class ImageRequest(BaseModel):
    name: str = Field(description="User's name")
    user_fullname: str = Field(description="User's full name")
    user_university_code: str = Field(description="User's university code")
    command_name: str = Field(description="Command name", default="")
    device_name: str = Field(description="Device name", default="")
    base64Images: List[str] = Field(description="List of base64 images")
# class ImageRequest(BaseModel):
#     name: str = Field(description="users name")
#     command_name: str = Field(description="command name", default="")
#     device_name: str = Field(description="device name", default="")
#     base64Images: list[str] = Field(description="list of base 64 images")

class ImageResponse(ImageRequest):
    id: str = Field(description="group id")

class UsersResponse(BaseModel):
    id: str = Field(description="id usuario")
    user_university_code: str = Field(description="User's university code")
    user_fullname: str = Field(description="User's full name")
    type_assintance: str = Field(type="User's type attendance")

class AttendanceRequest(BaseModel):
    # id: str = Field(description="id usuario")
    user_university_code: str = Field(description="User's university code")
    user_fullname: str = Field(description="User's full name")
    type_assintance: str = Field(type="User's type attendance")