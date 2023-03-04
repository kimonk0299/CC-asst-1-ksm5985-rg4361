#!/usr/bin/env python
# coding: utf-8

# In[1]:


#pip install elasticsearch


# In[2]:


#pip install requests_aws4auth


# In[3]:


import json
import boto3
import datetime
import requests
from decimal import *
from time import sleep
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from io import BytesIO


# In[4]:


region = 'us-east-1'
service = 'es'
credential = boto3.Session(aws_access_key_id="AKIA4J6KABAGXUV6X5E3",
                          aws_secret_access_key="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", 
                          region_name="us-east-1").get_credentials()
auth = AWS4Auth(credential.access_key, credential.secret_key, region, service)


# In[5]:


esEndPoint = 'search-rithvikchatbot-be7jjxxxug67ybvhvce4kpx2au.us-east-1.es.amazonaws.com'

# taken from stack overflow
es = Elasticsearch(
    hosts = [{'host': esEndPoint, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)
es.info()
es.ping()


# In[6]:

restaurants = {}
def addItems(data, cuisine):
    for rec in data:
            dataToAdd = {}
            try:
                if rec["alias"] in restaurants:
                    continue;
                dataToAdd['cuisine'] = cuisine
                dataToAdd['Business ID'] = str(rec["id"])
                sleep(0.001)
                print(dataToAdd)
                es.index(index="rithvikchatbot", doc_type="_doc", id=str(rec["id"]), body=dataToAdd, refresh=True)
            except Exception as e:
                print(e)
        


# In[7]:


cuisines = ['indian', 'thai', 'mediterranean', 'chinese', 'italian']
headers = {'Authorization': 'Bearer 41UL2KIGr9Og12TT-jgN6kPpfESr2skxmPjTHwWw7bYWqjY2GQBiPc9o0HeHegRMMXJJbkBsrDaYU2Z3Z-qg3vgbYnjwdVr9egcJbj9G4Hqcij6ixq4jSYZtyjABZHYx'}
DEFAULT_LOCATION = 'Manhattan'
for cuisine in cuisines:
    for i in range(0, 1000, 50):
        params = {'location': DEFAULT_LOCATION, 'offset': i, 'limit': 50, 'term': cuisine + " restaurants"}
        response = requests.get("https://api.yelp.com/v3/businesses/search", headers = headers, params=params)
        js = response.json()
        addItems(js["businesses"], cuisine)







