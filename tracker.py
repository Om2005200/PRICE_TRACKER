import requests as rq
import pandas as pd
import csv
import json
from datetime import datetime ,timedelta
import jwt
from bs4 import BeautifulSoup
from fastapi_mail import FastMail
from redis.asyncio import Redis
import time
from fastapi import FastAPI,APIRouter,HTTPException,status,Depends,BackgroundTasks,Request

from typing import List
from sqlmodel import select,desc
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker

from schemas import USERACCOUNT,ADD_TO_CART


from models import USERCREDS_MODEL,API_VERIFY,DYNAMIC_PRODUCT,DYNAMIX_PRODUCT

import logging
from logzero import logger 


from sqlalchemy.ext.asyncio import create_async_engine ,AsyncSession
from sqlmodel import SQLModel
import asyncio
import httpx
import json





database_url= "postgresql+asyncpg://postgres:Samnokia123%40@localhost:5432/ECOMMERCE"
jwt_key='c932c7cad4cf33dd43ca01162474b4bce1ca32a76472ac7fb5de486b81f48cd1'
jwt_algorithm='HS256'
ecommerce=FastAPI()
router=APIRouter()

engine=create_async_engine(database_url,echo=True)
@ecommerce.on_event("startup")
async def startup():
    await init_db()
    ecommerce.state.redis=Redis(host='localhost',port=6379)
    lua_script= """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')

    local tokens = tonumber(bucket[1])
    local last_refill = tonumber(bucket[2])

    if tokens == nil then
        tokens = capacity
        last_refill = now
    end

    local elapsed = now - last_refill
    local refill = elapsed * refill_rate

    local new_tokens = math.min(capacity, tokens + refill)

    if new_tokens < 1 then
        return {0, math.floor(new_tokens)}
    end

    tokens = new_tokens - 1

    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 60)

    return {1, math.floor(tokens)}
    """
    ecommerce.state.rate_limiter_sha=await ecommerce.state.redis.script_load(lua_script)

    ecommerce.state.http_client=httpx.AsyncClient()
    ecommerce.state.loop=asyncio.get_running_loop()
    print('Event loop started ')
    ecommerce.state.p=PRICE_TRACKER()
    p=ecommerce.state.p
    p.getting_the_flipkart_iphone_metadata()  
    await p.getting_the_flipkart_iphone_data_descriptions()
    await p.getting_the_flipkart_iphone_price_details()
    await p.flipkart_iphone_merged_dataset()
    p.getting_the_samsung_flipkart_data()  
    await p.getting_the_flipkart_samsung_data()
    await p.getting_the_samsung_price_list()
    await p.flipkart_samsung_merged_data()
    p.getting_the_amazon_samsung_data()  
    await p.accessing_the_amazon_s_series_pr_descri()
    await p.getting_the_price_list_samsung()
    await p.merging_the_amazon_samsung_data()
    await p.compare_samsung_prices()
    
@ecommerce.on_event('shutdown')
async def shutdown_event():
   await ecommerce.state.redis.close()
   await ecommerce.state.http_client.aclose()



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
async def get_session():
    Session=sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False

    )
    async with Session() as session:
        yield session

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class PRICE_TRACKER:
    """THIS APPLICATION IS A BETA VERSION OF PRICE TRACKING"""





    def accessing_the_amazon_metadata(self):
        endpoint='http://amazon.in/s?k=iphones&crid=2GKGYJQQUGLUW&sprefix=iphones%2Caps%2C427&ref=nb_sb_noss_2'
        endpoint_2='https://www.amazon.in/s?k=iphone&s=price-desc-rank&ds=v1%3AN03Sgt32ZqtgFKRUHNTaDzxNYt46EwSpNMZcTc28ybg&crid=2GKGYJQQUGLUW&qid=1774817252&sprefix=iphones%2Caps%2C427&ref=sr_st_price-desc-rank'
        headers = {
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
         "Accept-Language": "en-US,en;q=0.9",
    
         "Accept-Encoding": "gzip, deflate, br",
    
         "Connection": "keep-alive",
    
         "Upgrade-Insecure-Requests": "1",
    
         "DNT": "1",  
    
         "Sec-Fetch-Dest": "document",
         "Sec-Fetch-Mode": "navigate",
         "Sec-Fetch-Site": "none",
         "Sec-Fetch-User": "?1",
        }
        requests=rq.get(endpoint,headers=headers)
        request2=rq.get(endpoint_2,headers=headers)

        


        soup=BeautifulSoup(requests.text,'html.parser')
        with open('price_tracker_amazon_fastapi_ecommerce.html','wb',encoding='utf-8') as x:
            x.write(requests.content+request2.content)
        #print(requests.text)
        return requests.content,request2.content
    
    def accesing_the_amazon_metdata_files(self):
        with open('price_tracker_amazon_fastapi_ecommerce.html','rb') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('h2')
            for datas in items:
                titles=soup.find_all('a-size-medium-plus a-spacing-none a-color-base a-text-bold')
                return titles
            
    async def getting_the_description_amazon_products(self):
        with open('price_tracker_ecommerce.html','rb') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            product_list=[]
            for datas in items:
                names=soup.find_all('h2')
                for sets in names:
                    if sets.has_attr('aria-label'):
                        if sets['aria-label'] not in product_list:
                            product_list.append(sets['aria-label'])
            with open('amazon_iphone_listings.json','w',encoding='utf-8') as x:
                json.dump(product_list,x,indent=4)

            await ecommerce.state.redis.set('amazon_iphone_listings',json.dumps(product_list),ex=3600)
            return product_list
        
    async def getting_the_amazon_iphone_price_list(self):
        with open('price_tracker_fastapi_ecommerce.html','rb') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            price_list=[]
            data=soup.find_all('span')
            prices=soup.find_all('span',class_='a-price-whole')
            for datas in items:
                for spnas in data:
                    for prs in prices:
                        if prs.text not in price_list:
                            price_list.append(prs.text)
            with open('amazon_iphone_price_list.json','w',encoding='utf-8') as x:
                json.dump(price_list,x,indent=4)
            await ecommerce.state.redis.set('amazon_iphone_prices',json.dumps(price_list),ex=3600)
            return price_list
        

    def getting_the_amazon_samsung_data(self):
        amazon_endpoint='https://www.amazon.in/s?k=samsung+s+series&rh=n%3A22736673031%2Cp_123%3A46655%2Cp_n_g-1003492455111%3A81332994031%257C81332996031&s=price-desc-rank&dc&crid=30MNA7ELXTEDY&qid=1774562103&rnid=44349045031&sprefix=samsung+s+series+%2Caps%2C452&xpid=jk6U-zm0QhrEk&ref=sr_pg_1'
        endpoint2='https://www.amazon.in/s?k=samsung+s+series&rh=n%3A22736673031%2Cp_123%3A46655%2Cp_n_g-1003492455111%3A81332994031%257C81332996031&s=price-desc-rank&dc&page=2&crid=30MNA7ELXTEDY&qid=1774791458&rnid=44349045031&sprefix=samsung+s+series+%2Caps%2C452&xpid=jk6U-zm0QhrEk&ref=sr_pg_2'

        headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
          "Accept-Language": "en-US,en;q=0.9",
    
          "Accept-Encoding": "gzip, deflate, br",
    
          "Connection": "keep-alive",
    
          "Upgrade-Insecure-Requests": "1",
    
          "DNT": "1", 
    
          "Sec-Fetch-Dest": "document",
          "Sec-Fetch-Mode": "navigate",
          "Sec-Fetch-Site": "none",
          "Sec-Fetch-User": "?1",
        }
    
        
        requests=rq.get(amazon_endpoint,headers=headers)
        request2=rq.get(endpoint2,headers=headers)
        soup=BeautifulSoup(requests.text,'html.parser')

        with open('price_tracker_fastapi_ecommerce_s_series_samsung.html','wb') as x:

          x.write(requests.content+request2.content)
    #print(requests)

        return requests.content,request2.content
    
    
    async def accessing_the_amazon_s_series_pr_descri(self):
        with open('price_tracker_fastapi_ecommerce_s_series_samsung.html','rb') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            #soup.find_all('a')
            items=soup.find_all('a')
            product_list=[]
            for datas in items:
                names=soup.find_all('h2')
                for sets in names:
                    if sets.has_attr('aria-label'):
                        if sets['aria-label'] not in product_list:
                            product_list.append(sets['aria-label'])
            with open('product_description_samsung_s_series.json','w',encoding='utf-8') as x:
                json.dump(product_list,x,indent=4)
            await ecommerce.state.redis.set('amazon_s_series_product_listings',json.dumps(product_list),ex=3600) 
            return product_list
        
    async def getting_the_price_list_samsung(self):
        with open('price_tracker_fastapi_ecommerce_s_series_samsung.html','rb',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            price_list=[]
            items=soup.find_all('a')
            msport=soup.find_all('span')
            prices=soup.find_all('span',class_='a-price-whole')
            for datas in items:
                for spans in msport:
                    for prs in msport:
                        if prs.text not in price_list:
                            price_list.append(prs.text)
            with open('product_price_list_samsung_s_series.json','w',encoding='utf-8') as x:
                json.dump(price_list,x,indent=4)
            await ecommerce.state.redis.set('amazon_samsung_s_series_price_listings',json.dumps(price_list),ex=3600)
            return price_list
        

    def getting_the_flipkart_iphone_metadata(self):
        flipkart_endpoint='https://www.flipkart.com/search?q=iphone&as=on&as-show=on&otracker=AS_Query_OrganicAutoSuggest_8_1_na_na_na&otracker1=AS_Query_OrganicAutoSuggest_8_1_na_na_na&as-pos=8&as-type=RECENT&suggestionId=iphone&requestId=6277740d-cfff-40e2-bf76-fa782a86f03d&as-searchtext=i&sort=price_desc&page=2'

        endpoint2='https://www.flipkart.com/search?q=iphone&as=on&as-show=on&otracker=AS_Query_OrganicAutoSuggest_8_1_na_na_na&otracker1=AS_Query_OrganicAutoSuggest_8_1_na_na_na&as-pos=8&as-type=RECENT&suggestionId=iphone&requestId=6277740d-cfff-40e2-bf76-fa782a86f03d&as-searchtext=i&sort=price_desc'

        headers = {
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
         "Accept-Language": "en-US,en;q=0.9",
    
         "Accept-Encoding": "gzip, deflate, br",
    
         "Connection": "keep-alive",
    
         "Upgrade-Insecure-Requests": "1",
    
         "DNT": "1", 
    
         "Sec-Fetch-Dest": "document",
         "Sec-Fetch-Mode": "navigate",
         "Sec-Fetch-Site": "none",
         "Sec-Fetch-User": "?1",
        }
        requests=rq.get(flipkart_endpoint,headers=headers)
        requests2=rq.get(endpoint2,headers=headers)

        soup=BeautifulSoup(requests.text,'html.parser')
        with open('flipkart_fastapi_ecommerce_iphone_data.html','w',encoding='utf-8') as x:
            x.write(requests.text+requests2.text)
        
        return requests.text,requests2.text
    
 
    def getting_the_flipkart_iphone_data(self):
        with open('flipkart_fastapi_ecommerce_iphone_data.html','r',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')

    
    async def getting_the_flipkart_iphone_data_descriptions(self):
        with open('flipkart_fastapi_ecommerce_iphone_data.html','r',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            product_list=[]
            for datas in items:
                apple=datas.find_all('div',class_='RG5Slk')
                for apples in apple:
                    if apples.text not in product_list:
                        product_list.append(apples.text)
            with open('flipkart_fastapi_ecommerce_iphones_data.json','w',encoding='utf-8') as x:
                json.dump(product_list,x,indent=4)
            await ecommerce.state.redis.set('flipkart_iphone_product_listings',json.dumps(product_list),ex=3600)
            return product_list
        
    async def getting_the_flipkart_iphone_price_details(self):
        with open('flipkart_fastapi_ecommerce_iphone_data.html','r',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            price_list=[]
            for datas in items:
                apple=datas.find_all('div',class_='hZ3P6w DeU9vF')
                for prices in apple:
                    if prices.text not in price_list:
                        price_list.append(prices.text)
            with open('flipkart_fastapi_ecommerce_iphone_price_listings.json','w',encoding='utf-8') as x:
                            json.dump(price_list,x,indent=4)
            await ecommerce.state.redis.set('flipkart_iphone_price_listings',json.dumps(price_list),ex=3600)

            return price_list
        
    def getting_the_samsung_flipkart_data(self):
        flipkart_endpoint='https://www.flipkart.com/search?q=iphone&as=on&as-show=on&otracker=AS_Query_OrganicAutoSuggest_8_1_na_na_na&otracker1=AS_Query_OrganicAutoSuggest_8_1_na_na_na&as-pos=8&as-type=RECENT&suggestionId=iphone&requestId=6277740d-cfff-40e2-bf76-fa782a86f03d&as-searchtext=i'
        endpoint2='https://www.flipkart.com/search?q=samsung+s+24+s25+s26+series+&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&as-pos=1&as-type=HISTORY&sort=price_desc&page=2'

        headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
          "Accept-Language": "en-US,en;q=0.9",
    
          "Accept-Encoding": "gzip, deflate, br",
    
          "Connection": "keep-alive",
    
          "Upgrade-Insecure-Requests": "1",
    
          "DNT": "1", 
    
          "Sec-Fetch-Dest": "document",
          "Sec-Fetch-Mode": "navigate",
          "Sec-Fetch-Site": "none",
          "Sec-Fetch-User": "?1",
        }
        requests=rq.get(flipkart_endpoint,headers=headers)
        request2=rq.get(endpoint2,headers=headers)

        soup=BeautifulSoup(requests.text,'html.parser')
        with open('flipkart_fastapi_ecommerce_samsung_data.html','w',encoding='utf-8') as x:
            x.write(requests.text+request2.text)
        return requests.text,request2.text
    
    async def getting_the_flipkart_samsung_data(self):
        with open('flipkart_fastapi_ecommerce_samsung_data.html','r',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            product_list=[]
            for datas in items:
                samsung=datas.find_all('div',class_='RG5Slk')
                for samsungs in samsung:
                    if samsungs.text not in product_list:
                        product_list.append(samsungs.text)
            with open('flipkart_fastapi_ecommerce_samsung_data.json','w',encoding='utf-8') as x:
                json.dump(product_list,x,indent=4)
            await ecommerce.state.redis.set('flipkart_samsung_listings',json.dumps(product_list),ex=3600)
            return product_list
        
    async def getting_the_samsung_price_list(self):
        with open('flipkart_fastapi_ecommerce_samsung_data.html','r',encoding='utf-8') as x:
            soup=BeautifulSoup(x.read(),'html.parser')
            items=soup.find_all('a')
            price_list=[]
            for datas in items:
                samsung=datas.find_all('div','hZ3P6w DeU9vF')
                for prices in samsung:
                    if prices.text not in price_list:
                        price_list.append(prices.text)
            with open('flipkart_fastapi_ecommerce_samsung_price_list.json','w',encoding='utf-8') as x:
                json.dump(price_list,x,indent=4)
            await ecommerce.state.redis.set('flipkart_samsung_price_list',json.dumps(price_list),ex=3600)
            return price_list
        
             
    async def flipkart_iphone_merged_dataset(self):
        products=await self.getting_the_flipkart_iphone_data_descriptions()
        prices=await self.getting_the_flipkart_iphone_price_details()
        merged_data=[
            {
                'MODEL':name,
                'PRICE':price
            }
            for name,price in zip(products,prices)
        ]
        with open('flipkart_iphone_fastapi_merged_data.json','w',encoding='utf-8') as x:
            json.dump(merged_data,x,indent=4,ensure_ascii=False)
        await ecommerce.state.redis.set('flipkart_iphone_merged_data',json.dumps(merged_data),ex=3600)
        return  merged_data
    
    async def flipkart_samsung_merged_data(self):
        products=await self.getting_the_flipkart_samsung_data()
        prices=await self.getting_the_samsung_price_list()
        merged_data=[
            {
            'MODEL':name,
            'PRICE':price
            }
            for name , price in zip(products,prices)
        ]

        with open('flipkart_merged_data_samsung.json','w',encoding='utf-8') as x:
            json.dump(merged_data,x,indent=4,ensure_ascii=False)
        await ecommerce.state.redis.set('flipkart_merged_samsung_data',json.dumps(merged_data),ex=3600)
    
    async def merging_the_amazon_iphone_data(self):
        products=await self.getting_the_description_amazon_products()
        prices=await self.getting_the_amazon_iphone_price_list()
        merged_data=[
            {
                'MODEL':name,
                'PRICE':price

            }
            for name,price in zip(products,prices)


        ]
        with open('amazon_iphone_merged_data.json','w',encoding='utf-8') as x:
            json.dump(merged_data,x,indent=4,ensure_ascii=False)
        await ecommerce.state.redis.set('amazon_merged_iphone_data',json.dumps(merged_data),ex=3600)
    async def merging_the_amazon_samsung_data(self):
        products= await self.accessing_the_amazon_s_series_pr_descri()
        prices= await self.getting_the_price_list_samsung()
        merged_data=[
            {
                'MODEL':name,
                'PRICE':price

            }
            for name,price in zip(products,prices)

        ]
        with open('amazon_samsung_merged_data.json','w',encoding='utf-8') as x:
            json.dump(merged_data,x,indent=4,ensure_ascii=False)
        await ecommerce.state.redis.set('amazon_samsung_merged_data',json.dumps(merged_data),ex=3600)
    
    async def compare_iphone_prices(self):
        flipkart = await ecommerce.state.redis.get('flipkart_iphone_merged_data')
        amazon = await ecommerce.state.redis.get('amazon_iphone_merged_data')

        if not flipkart or not amazon:
          return {"error": "Data not available"}

        flipkart = json.loads(flipkart)
        amazon = json.loads(amazon)

        comparison = []

        for f, a in zip(flipkart, amazon):
           comparison.append({
              "MODEL": f["MODEL"],
              "FLIPKART_PRICE": f["PRICE"],
              "AMAZON_PRICE": a["PRICE"]
              })

        await ecommerce.state.redis.set('iphone_price_comparison', json.dumps(comparison), ex=3600)

        return comparison
    


    async def compare_samsung_prices(self):
        flipkart = await ecommerce.state.redis.get('flipkart_samsung_merged_data')
        amazon = await ecommerce.state.redis.get('amazon_samsung_merged_data')

        if not flipkart or not amazon:
          return {"error": "Data not available"}

        flipkart = json.loads(flipkart)
        amazon = json.loads(amazon)

        comparison = []

        for f, a in zip(flipkart, amazon):
            comparison.append({
               "MODEL": f["MODEL"],
               "FLIPKART_PRICE": f["PRICE"],
               "AMAZON_PRICE": a["PRICE"]
            })

        await ecommerce.state.redis.set('samsung_price_comparison', json.dumps(comparison), ex=3600)

        return comparison
    
    def dynamic_product_service(self,user_input:str):
        amazon_endpoint='https://www.amazon.in/s?k={}&s=price-desc-rank'.format(user_input)
        headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
          "Accept-Language": "en-US,en;q=0.9",
    
          "Accept-Encoding": "gzip, deflate, br",
    
          "Connection": "keep-alive",
    
          "Upgrade-Insecure-Requests": "1",
    
          "DNT": "1", 
    
          "Sec-Fetch-Dest": "document",
          "Sec-Fetch-Mode": "navigate",
          "Sec-Fetch-Site": "none",
          "Sec-Fetch-User": "?1",
        }
        requests=rq.get(amazon_endpoint,headers=headers)
        soup=BeautifulSoup(requests.text,'html.pasrer')
        with open('dynamic_product.html','wb',encoding='utf-8') as h:
            h.write(requests.content)
        return requests.content
    
    async def accesing_the_product_description(self):
        with open('dynamic_product.html','rb',encoding='utf-8') as i:
            soup=BeautifulSoup(i.read(),'html.parser')
            items=soup.find_all('a')
            product_list=[]
            for datas in items:
                names=soup.find_all('h2')
                for sets in names:
                    if sets.has_attr('aria-label'):
                        model_name=sets['aria-label']
                        if model_name not in product_list:
                            product_list.append({'MODEL':model_name})
            
                        
            with open('dynamic_product_description.json','w',encoding='utf-8') as v:
                json.dump(product_list,v,indent=4)
            return product_list
        
    async def getting_the_product_prices(self):
        with open('dynamic_product.html','r',encoding='utf-8') as k:
            soup=BeautifulSoup(k.read(),'html.pasrer')
            price_list=[]
            items=soup.find_all('a')
            m340i=soup.find_all('span')
            prices=soup.find_all('span',class_='a-price-whole')
            for datas in items:
                for spans in m340i:
                    for prs in m340i:
                        if prs.text not in price_list:
                            price_list.append({'PRICE':prs.text})
            with open('dynamic_price_list.json','w') as v:
                json.dump(price_list,v,incent=4)
            return price_list
    def opening_the_old_file(self):
        with open('dynamic_merged_data.json','r') as h:
            data=json.load(h)
            return data
    async def merge_model_and_price(self):
        models=await self.accesing_the_product_description()
        prices=await self.getting_the_product_prices()  
        merged_data=[]
        length=min(len(models),len(prices))
        for i in range(length):
            merged_data.append({
                'MODEL':models[i]['MODEL'],
                'PRICE':prices[i]['PRICE']


            })
        with open('dynamic_merged_data.json','e',encoding='utf-8') as x:
            json.dump(merged_data,x,indent=4)
        return merged_data
    async def analyzing_the_main_data(self):
        main_data=self.merge_model_and_price()
        old_data=self.opening_the_old_file()
        for datas in main_data:
            new_model=datas['MODEL']
            for model in old_data:
                old_model=model['MODEL']
                if old_model==new_model:
                    new_price=datas['PRICE']
                    old_price=datas['PRICE']
                    if new_price!=old_price:
                        new=int(new_price.replace(',',''))
                        old_mode_price=int(old_price.replace(',',''))
                        if new>old_mode_price:
                            price_difference=new-old_mode_price
                            print('The price of the model {} has been increased by {}'.format(new_model,price_difference))
                        elif old_mode_price<new:
                            price_difference=old_mode_price-new
                            print('The price of the model {} has been decreased by {}'.format(new_model,price_difference))
                        else:
                            print('The price of the model {} is same as it is '.format(model))
    def getting_the_desired_host_data(user_input):
        api_endpint='https://www.amazon.in/s?k={}&crid=2GKGYJQQUGLUW&sprefix=iphones%2Caps%2C427&ref=nb_sb_noss_2'.format(user_input)
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    
        "Accept-Language": "en-US,en;q=0.9",
    
        "Accept-Encoding": "gzip, deflate, br",
    
        "Connection": "keep-alive",
    
        "Upgrade-Insecure-Requests": "1",
    
        "DNT": "1", 
    
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        }
        product_list=[]
        price_list=[]
        requests=rq.get(api_endpint,headers=headers)
        soup=BeautifulSoup(requests.text,'html.parser')
        with open('amaozn_dynamix_desired_data.html','wb') as u:
            u.write(requests.content)
        with open('amazon_dynamix_desired_data.html','rb')  as j:
            soup=BeautifulSoup(j.read(),'htnml.parser')
            main_data=soup.find_all('a')
            for datas in  main_data:
                product_description=soup.find_all('h2')
                for sets in product_description:
                    if sets.has_attr('aria-label'):
                        if sets['aria-label'] not in product_list:
                            product_list.append(sets['aria-label'])
            with open('amazon_dynamix_product_description.json','w',encoding='utf-8') as d:
                json.dump(product_list,d,indent=4)
            price_data=soup.find_all('span') 
            raw_price_data=soup.find_all('span',class_='a-price-whole')
            for data in main_data:
                for span in price_data:
                    for prs in raw_price_data:
                        if prs.text  not in price_list:
                            price_list.append(prs.text)
            with open('amazon_dynamix_product_price_list.json','w',encoding='utf-8') as v:
                json.dump(price_list,v,indent=4)
            return product_list,price_list
        

    async def merger_of_the_dynamix_data():
        with open('amazon_dynamix_product_description.json','r') as j:
            main_data=json.load(j)
        with open('amazon_dynamix_product_price_list.json','r') as k:
            price_data=json.load(k)
        set_data=[
            {
            'PRODUCT':products,
            'PRICES':prices
            }
            for products,prices in zip(main_data,price_data)


        ]
        with open('user_dynamix_merged_data.json','w',encoding='utf-8') as k:
            json.dump(set_data,k,indent=4)
        return set_data
    

    async def creating_the_path_for_continious_data_processing(self,session:AsyncSession):
        main_data=await session.execute(select(ADD_TO_CART))
        whole_data=main_data.scalars().all()
        tele_list=[]
        async with httpx.AsyncClient() as client:

            for products in whole_data:
                sourec_feed=await self.getting_the_desired_host_data(products.PRODUCT_NAME)
                if sourec_feed is not None:
                   data_merger=await self. merger_of_the_dynamix_data()
                   telegram_ids=products.TELEGRAM_ID
                   if telegram_ids not in tele_list:
                      tele_list.append(telegram_ids)
                      url='https://api.telegram.org/bot{}/sendDocument'.format()
                      with open(data_merger,'rb') as f:
                          
                          requests=await client.post(url,data={'chat_id':telegram_ids},files={'document':f})
        return requests
            



      
        

e=PRICE_TRACKER()

class PRICE_TRACKER_SERVICE:
     
    """THIS IS THE SERVICE CLASS FOR THE PRICE_TRACKER APPLICATION"""




    # USER ACCOUNT CREATION
    async def creating_the_account(self,user_data:USERCREDS_MODEL,session:AsyncSession):
        new_user=USERACCOUNT(NAME=user_data.NAME,AGE=user_data.AGE,EMAIL_ID=user_data.EMAIL_ID,CONTACT_NO=user_data.CONTACT_NO)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    # USER VERIFICATION FUNCTION 
    async def verify_user(self,user_data:USERCREDS_MODEL,session:AsyncSession):
        verify_user=select(USERACCOUNT).where(USERACCOUNT.EMAIL_ID==user_data.EMAIL_ID,USERACCOUNT.CONTACT_NO==user_data.CONTACT_NO)
        execution=await session.execute(verify_user)
        result=execution.first()
        return result
    
    #  API KEY CREATING FUNCTION
    async def creating_the_api_key(self,user_data:dict):
        payload={}
        payload['user']=user_data
        token=jwt.encode(payload,jwt_key,algorithm=jwt_algorithm)
        return token
    # API DECODING FUNCTION 
    async def  decoding_the_api_key(self,token:str):
        try:
            token_data=jwt.decode(token,jwt_key,algorithms=[jwt_algorithm])
            return token_data
        except jwt.PyJWTError as e:
            logging.exception(e)
            return None
    
    async def user_api_key_verify(self,user_data:API_VERIFY,session:AsyncSession):

        api_verify=select(USERACCOUNT.API_KEY).where(USERACCOUNT.API_KEY==user_data.API_KEY)

        exceute=await session.execute(api_verify)
        result=exceute.first()
        return result
   
    async def check_redis_api_limit(self,request,capacity=10,refill_rate=1):
        redis=request.app.state.redis

        sha=request.app.state.rate_limiter_sha
        api_key=request.headers.get('x-api-key','anonymous')
        key=('api_rate_limit:{}'.format(api_key))
        now=int(time.time())
        allowed,tokens_left= await redis.evalsha(sha,1,key,capacity,refill_rate,now)
        return allowed,tokens_left
    async def serving_the_dynamic_product_service(self,user_input:DYNAMIC_PRODUCT,session:AsyncSession):
        dynamic_product=user_input
        if dynamic_product:
            func=e.dynamic_product_service(user_input)
            if func:
                the=e.analyzing_the_main_data()
            return the
    async def cattering_the_servers(self,models:DYNAMIX_PRODUCT,session:AsyncSession):
        user_input=e.getting_the_desired_host_data()
        if user_input:
            return e.merger_of_the_dynamix_data()
        else:
           return None
    async def creating_the_wishlist_account(self,model:DYNAMIX_PRODUCT,session:AsyncSession):
        product_check=ADD_TO_CART(NAME=model.NAME,AGE=model.AGE,EMAIL_ID=model.EMAIL_ID,TELEGRAM_ID=model.TELEGRAM_ID,PRODUCT_NAME=model.PRODUCT_NAME)
        session.add(product_check)
        await session.commit()
        await session.refresh(product_check)
        return product_check
    


service=PRICE_TRACKER_SERVICE()

@router.post('/new/user/signup/')
async def creating_new_account(user_data:USERCREDS_MODEL,bg_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
    user_exists=await service.verify_user(user_data,session)
    if user_exists is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='USER ALREADY EXISTS')
    new_user= await service.creating_the_account(user_data,session)

    api_key=await service.creating_the_api_key(user_data={
        'email':user_data.EMAIL_ID,
        'age':user_data.AGE,
        'name':user_data.NAME
    })
    new_user.API_KEY=api_key
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return JSONResponse(content={
        'message':'Account creation is succesfull',
        'API_KEY':api_key,
        'NAME':user_data.NAME
    })
    
    

@router.get('/get/flipkart/iphone/listings/')
async def getting_the_flipkart_iphone_listings(request:Request,user_data:API_VERIFY,bg_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEDED PLEASE TRY AFTER SOMETIME')
    
    user_verify=await service.user_api_key_verify(user_data,session)

    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Please enter valid details to access the data')
    flipkart_iphone_data= await ecommerce.state.redis.get('flipkart_iphone_product_listings')
    if flipkart_iphone_data is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='No data available for now please try again after sometime')
    return json.loads(flipkart_iphone_data.decode())

@router.get('/iphone/prices/flipkart/')
async def getting_the_prices_of_iphones(request:Request,user_data:API_VERIFY,bg_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEDED PLEASE TRY FATER SOMETIME')
    user_verify= await service.user_api_key_verify(user_data,session)
    
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Please enter valid keys to access the data')
    flipkart_iphone_listings=await ecommerce.state.redis.get('flipkart_iphone_price_listings')
    if flipkart_iphone_listings is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBALE FOR NOW PLEASE TRY AFTER SOMETIME')
    
    
    return  json.loads(flipkart_iphone_listings.decode())

@router.get('/samsung/flipkart/products/')
async def getting_the_samsung_products(request:Request,user_data:API_VERIFY,bg_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed :
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DEIALS TO ACCESS THE DATA')
    samsung_products=await ecommerce.state.redis.get('flipkart_samsung_listings')
    if samsung_products is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILABLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(samsung_products.decode())

@router.get('/flipkart/samsung/price/listings/')
async def getting_the_samsung_price_list(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME ')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE NETER VALID DETAILS TO ACCESS THE DATA ')
    samsung_price_listings=await ecommerce.state.redis.get('flipkart_samsung_price_list')
    if samsung_price_listings is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILAIBLE FOR NOW PLEAESE TRY AFTER SOMETIME ')
    return json.loads(samsung_price_listings.decode())

@router.get('/iphone/merged/data')
async def getting_the_flipkart_iphone_merged_data(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCCEDED PLEASE TRY AFTER SOMETIME ')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DETAILS TO ACCESS THE DATA')
    flipkart_iphone_merged_data=await ecommerce.state.redis.get('flipkart_iphone_merged_data')
    if flipkart_iphone_merged_data is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILAIBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(flipkart_iphone_merged_data.decode())

@router.get('/samsung/merged/detail')
async def getting_the_merged_data_sasmung(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER  VALID DETAILS TO ACCESS THE DATA')
    samsung_merged_data=await ecommerce.state.redis.get('flipkart_samsung_merged_data')
    if samsung_merged_data is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(samsung_merged_data.decode())

@router.get('/amazon/iphone/listings/')
async def getting_the_amazon_iphone_listings(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DETAILS TO ACCESS THE DATA ')
    amazon_iphone_listings=await ecommerce.state.redis.get('amazon_iphone_listings')
    if amazon_iphone_listings is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVALIBLE FOR NOW PLEASE TRY AFTER SOMETIME ')
    return json.loads(amazon_iphone_listings.decode())

@router.get('/amazon/iphone/price/listings/')
async def fetching_the_live_prices(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE NETER VALID DETAILS TO ACCESS THE DATA')
    amazon_iphone_price_listings=await ecommerce.state.redis.get('amazon_iphone_prices')
    if amazon_iphone_price_listings is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(amazon_iphone_price_listings.decode())

@router.get('/amazon/iphone/merged/')
async def getting_the_iphone_merged_data(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)        
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DETAILS TO ACCESS THE DATA')
    amazon_iphone_merged=await ecommerce.state.redis.get('amazon_iphone_merged_data')
    if amazon_iphone_merged is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(amazon_iphone_merged.decode())

@router.get('/amazon/samsung/product/listings/')
async def getting_the_amazon_samsung_products(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DETAILKS TO ACCESS THE DATA')
    amazon_samsung_products=await ecommerce.state.redis.get('amazon_samsung_s_series_product_listings')
    if amazon_samsung_products is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(amazon_samsung_products.decode())

@router.get('/amazon/samsung/price/listings/')
async def getting_the_price_list(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE ENTER VALID DETAILS TO ACCESS THE DATA ')
    amazon_samsung_price=await ecommerce.state.redis.get('amazon_samsung_s_series_product_listings')
    if amazon_samsung_price is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='DATA NOT AVAILBLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return json.loads(amazon_samsung_price.decode())

@router.get('/amazon/samsung/merged/')
async def getting_the_samsung_merged_data(request:Request,bg_tasks:BackgroundTasks,user_data:API_VERIFY,session:AsyncSession=Depends(get_session)):
    allowed,tokens_left=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME')
    user_verify=await service.user_api_key_verify(user_data,session)
    if user_verify is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='PLEASE NETR VALID DETAILS TO ACCESS THE DATA')
    amazon_samsung_merged=await ecommerce.state.redis.get('amazon_samsung_merged_data')
    if amazon_samsung_merged is None:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail='PLEASE ENTER VALID  DETAILS TO ACCESS THE DATA')
    return json.loads(amazon_samsung_merged.decode())


@router.get('/compare/iphone/prices/')
async def compare_iphone(request: Request, user_data: API_VERIFY, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    allowed, tokens_left = await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=429, detail='Rate limit exceeded')
    user_verify = await service.user_api_key_verify(user_data, session)
    if user_verify is None:
        raise HTTPException(status_code=401, detail='Invalid API key')
    data = await ecommerce.state.redis.get('iphone_price_comparison')
    return data



@router.get('/compare/samsung/prices/')
async def compare_samsung(request: Request, user_data: API_VERIFY, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    allowed, tokens_left = await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=429, detail='Rate limit exceeded')
    user_verify = await service.user_api_key_verify(user_data, session)
    if user_verify is None:
        raise HTTPException(status_code=401, detail='Invalid API key')
    data = await ecommerce.state.redis.get('samsung_price_comparison')
    return data

@router.get('/dynamic/products/')
async def getting_the_dynamic_products_data(request:Request,user_data:DYNAMIC_PRODUCT,session:AsyncSession=Depends(get_session)):
    allowed=await service.check_redis_api_limit(request)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail='API LIMT EXCEEDED PLEASE TRY AFTER SOMETIME')
    
    dynamic_product= await service.serving_the_dynamic_product_service(user_data)
    if dynamic_product:
        raise HTTPException(status_code=status.HTTP_204,detail='NO DATA AVAILABLE FOR NOW PLEASE TRY AFTER SOMETIME')
    return dynamic_product




@router.post('/Add_to_cart/')
async def adding_the_desired_product_into_wishlist(shervify:USERCREDS_MODEL,user_model:DYNAMIX_PRODUCT,session:AsyncSession=Depends(get_session)):
    user_verification=await service.verify_user(shervify,session)
    if user_verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='NO ACCOUNT AVAILBLE FOR THE GIVEN CRDENTIALS PLEASE CREATE ACCOUNT TO UNLOCK FEATURES')
    enter_product_name=await service.cattering_the_servers(user_model,session)
    if enter_product_name is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='NO USER FOUND FOR THE GIVEN CRDES PLEASE SIGNUP TO UNLOCK MORE FEATURES')
    #add_to_cart_account=service.creating_the_wishlist_account(user_model,session)
    user_chexk=select(ADD_TO_CART).where(ADD_TO_CART.EMAIL_ID==user_model.EMAIL_ID,ADD_TO_CART.NAME==user_model.NAME)
    product_check=select(ADD_TO_CART).where(ADD_TO_CART.EMAIL_ID==user_model.EMAIL_ID,ADD_TO_CART.PRODUCT_NAME==user_model.PRODUCT_NAME)
    pr_check=(await session.execute(product_check)).scalars().first()
    db_check=(await session.execute(user_chexk)).scalars().first()
    if db_check is None:
        add_to_cart_account=service.creating_the_wishlist_account(user_model,session)
        session.add(add_to_cart_account)
        await session.commit()
        await session.refresh(add_to_cart_account)
        return JSONResponse(
            content={
                'PRODUCT ADDED INTO THE CART'
            }
        )
    elif pr_check:
        raise HTTPException(status_code=status.HTTP_306_RESERVED,detail='THE GIVEN PRODUCT ALREADY EXISTS IN THE CART NO DUPLICATES ALLOWED ')
    

    



   

ecommerce.include_router(router)


        




    
