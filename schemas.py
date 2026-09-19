from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import create_engine,text,SQLModel,Field,Column
import uuid
from sqlalchemy.dialects.postgresql import JSON
from typing import List,Optional




class USERACCOUNT(SQLModel,table=True):
    __tablename__='ECOMMERCE_ACCOUNT'
    id:Optional[int]=Field(default=None,primary_key=True)
    NAME:str
    AGE:str
    EMAIL_ID:str=Field(index=True,unique=True)
    CONTACT_NO:str
    API_KEY:Optional[str]=Field(default=None,unique=True,index=True)

class ADD_TO_CART():
    __tablename__='DYNAMIX_DATA'
    id:Optional[int]=Field(default=None,primary_key=True)
    NAME:str
    AGE:int
    EMAIL_ID:str
    TELEGRAM_ID:str
    PRODUCT_NAME:str

    
     




    
