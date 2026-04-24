from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime




# class _Base(BaseModel): # is a hidden class, not to be called
#     """ 
#     Base class for all models.
#     Allows reading from ORM (e.g., SQLAlchemy objects by .model_validate()).
#     """
    
#     def __init__(self, model, db: Session = Depends(get_db),):
#         self.model= model
#         self.db= db
        
    
#     async def get_by_id(self, obj_id: int):
#         return await self.db.get(self.model, obj_id)
    
    
#     async def get_by_name(self, name: str):
#         result=  await self.db.execute(
#             select(self.model).where(self.model.name== name))
#         return result.scalars().first()
     
        
    # async def get_all(self):
    #     result= await self.db.execute(select(self.model))
    #     return result.scalers().all()
    
    
    # async def save_to_db(self, data: dict):
    #     obj= self.model(**data)
    #     self.db.add(obj)
    #     await self.db.commit()
    #     await self.db.refresh(obj)
    #     return obj
        
         
    # async def update(self, obj_id: int, data: dict):
    #     obj= await self.get_by_id(obj_id)
    #     if not obj:
    #         return None 
    #     for key, value in data.items():
    #         setattr(obj, key, value)
            
    #     await self.db.commit()
    #     await self.db.refresh(obj)
    #     return obj
    
    
    # async def delete(self, obj_id: int):
    #     obj= await self.get_by_id(obj_id)
    #     if not obj:
    #         return None
        
    #     await self.db.delete(obj)
    #     await self.db.commit()
    #     return obj
    
    
    # @field_validator("*")
    # @classmethod
    # async def strip_all(cls, value):
    #     if isinstance(value, str): #for all strings, avoide crash for integer
    #         return value.strip()
    #     return value
    
    # model_config = ConfigDict(from_attributes=True)






class UserCreate(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    profile_picture: Optional[str]= None    # base64 string
    profile_picture_mime: Optional[str]= None # MIME type


class UserResponse(UserCreate):
    id: int
    profile_picture: Optional[str]       # base64 string
    profile_picture_mime: Optional[str]  # MIME type
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

