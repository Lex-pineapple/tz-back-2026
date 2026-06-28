from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import TypedDict

class ReqStatusEnum(str, Enum):
  new = 'new'
  in_progress = 'in_progress'
  done = 'done'

class ReqModelEnum(str, Enum):
  low = 'low'
  normal = 'normal'
  high = 'high'

class NewRequest(BaseModel):
  title: str
  description: str | None = None
  status: ReqStatusEnum = ReqStatusEnum.new
  priority: ReqModelEnum = ReqModelEnum.low

class RequestData(BaseModel):
  id: int | None
  title: str
  description: str | None = None
  status: ReqStatusEnum | None
  priority: ReqModelEnum
  created_at: datetime | None
  updated_at: datetime | None

class DataCreated(BaseModel):
  message: str
  id: int

class UpdateStatus(BaseModel):
  status: ReqStatusEnum

class RequestsList(TypedDict):
  pages: int
  items: list[RequestData]