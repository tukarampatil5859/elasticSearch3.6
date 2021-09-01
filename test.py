from datetime import datetime
from elasticsearch import Elasticsearch

# make sure ES is up and running
# import requests
# res = requests.get('http://localhost:9200')
# print(res.content)

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es = Elasticsearch()

#
# import json
#
# r = requests.get('http://localhost:9200')
# i = 1
# while r.status_code == 200:
#     r = requests.get('http://swapi.co/api/people/' + str(i))
#     es.index(index='sw', doc_type='people', id=i, body=json.loads(r.content))
#     i = i + 1
#
# print(i)

# es.indices.create(index="first_index")

a = es.indices.exists(index="first_index")
print(a)

# a=es.indices.delete(index="first_index")
# print(a)

doc_1 = {"city": "Paris", "country": "France"}
doc_2 = {"city": "Vienna", "country": "Austria"}
doc_3 = {"city": "London", "country": "England"}

# print(es.index(index="cities", doc_type="places", id=1, body=doc_1))
#
# print(es.index(index="cities", doc_type="places", id=1, body=doc_2))
#
# print(es.index(index="cities", doc_type="places", id=1, body=doc_3))
print(es.indices.delete(index="kyc4"))


