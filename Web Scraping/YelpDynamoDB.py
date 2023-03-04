#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import boto3
import datetime
import requests
from decimal import *
from time import sleep


# In[2]:


client = boto3.resource('dynamodb', aws_access_key_id="AKIA4J6KABAGXUV6X5E3", aws_secret_access_key="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",region_name = 'us-east-1')
table = client.Table('yelp-restaurants')


# In[3]:


restaurants = {}
def addItems(data, cuisine):
   global restaurants
   with table.batch_writer() as batch:
        for rec in data:
            try:
                if rec["alias"] in restaurants:
                    continue;
                rec["Business ID"] = str(rec["id"])
                rec["rating"] = Decimal(str(rec["rating"]))
                restaurants[rec["alias"]] = 0
                rec['cuisine'] = cuisine
                rec['insertedAtTimestamp'] = str(datetime.datetime.now())
                rec["coordinates"]["latitude"] = Decimal(str(rec["coordinates"]["latitude"]))
                rec["coordinates"]["longitude"] = Decimal(str(rec["coordinates"]["longitude"]))
                rec['address'] = rec['location']['display_address']
                rec.pop("distance", None)
                rec.pop("location", None)
                rec.pop("transactions", None)
                rec.pop("display_phone", None)
                rec.pop("categories", None)
                if rec["phone"] == "":
                    rec.pop("phone", None)
                if rec["image_url"] == "":
                    rec.pop("image_url", None)

                # print(rec)
                batch.put_item(Item=rec)
                sleep(0.001)
            except Exception as e:
                print(e)
                print(rec)


# In[4]:


cuisines = ['indian', 'thai', 'mediterranean', 'chinese', 'italian']
headers = {'Authorization': 'Bearer 41UL2KIGr9Og12TT-jgN6kPpfESr2skxmPjTHwWw7bYWqjY2GQBiPc9o0HeHegRMMXJJbkBsrDaYU2Z3Z-qg3vgbYnjwdVr9egcJbj9G4Hqcij6ixq4jSYZtyjABZHYx'}
DEFAULT_LOCATION = 'Manhattan'
for cuisine in cuisines:
    for i in range(0, 1000, 50):
        params = {'location': DEFAULT_LOCATION, 'offset': i, 'limit': 50, 'term': cuisine + " restaurants"}
        response = requests.get("https://api.yelp.com/v3/businesses/search", headers = headers, params=params)
        js = response.json()
        #print(js["businesses"])
        addItems(js["businesses"], cuisine)
