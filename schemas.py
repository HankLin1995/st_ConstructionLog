from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    
    # 使用新的 ConfigDict 替代舊的 Config 類
    model_config = ConfigDict(from_attributes=True)
