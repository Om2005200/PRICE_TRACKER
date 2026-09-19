from pydantic import BaseModel
import uuid
from sqlmodel import create_engine,text,SQLModel,Field,Column
from typing import Optional,List




class USERCREDS_MODEL(BaseModel):
    NAME:str
    AGE:str
    EMAIL_ID:str
    CONTACT_NO:str

class DYNAMIC_PRODUCT(BaseModel):
    product_name:str
    

class API_VERIFY(BaseModel):
    API_KEY:str


class DYNAMIX_PRODUCT(BaseModel):
    PRODUCT_NAME:str
    NAME:str
    AGE:int
    EMAIL_ID:str
    TELEGRAM_ID:str
    

    
