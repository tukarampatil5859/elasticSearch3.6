import csv, json, os
import pandas as pd
import re, json, requests
from datetime import datetime
from elasticsearch.helpers import bulk, streaming_bulk, parallel_bulk
import confidenceScoreNewValue_correct
from fuzzywuzzy import fuzz
# Import Elasticsearch package
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch, analyzer, tokenizer

global mustList, shouldUniqList, shouldnameList, shouldkycList, shouldOtherList
global shouldnationList, shouldlocationList, NotList
kyc_list_input = []
queryBody = ""


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=
def connect_elasticsearch():
    client = Elasticsearch(
        # Add your cluster configuration here!"sniff":To inspect the cluster state to get a list of nodes upon startup, periodically and/or on failure
        [{'host': 'localhost', 'port': 9200}], maxsize=25, sniff_on_start=True,
        # If your application is long-running consider turning on Sniffing to make sure the client is up to date on the cluster location.
        sniff_on_connection_fail=True,
        sniffer_timeout=60)  # allow up to 25 connections to each node
    if client.ping():
        print('Connected to ElasticSearch!!!!')
    else:
        print('ElasticSearch could not connect!!!!')
    # es = Elasticsearch(["host1", "host2"], maxsize=25)
    return client


client = connect_elasticsearch()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=

def kycattribute(kyc_list_input):
    global shouldkycList
    global mustList
    kyc_list = ['Aadhar', 'Pan', 'Passport', 'NCRB', 'Airline', 'Company KYC', 'Driving License', 'Telecom',
                'Voter ID Card', 'Bank KYC']

    if len(kyc_list_input) > 0 and len(kyc_list_input) < 10:
        for val in kyc_list_input:
            interm = {"term": {"KYC_Attributes": val}}
            shouldkycList.append(interm)
    else:
        for val in kyc_list:
            outterm = {"term": {"KYC_Attributes": val}}
            shouldkycList.append(outterm)

def adharno(key, input_dict):
    adharterm = {"term": {"Aadhar_no": int(input_dict[key])}}
    shouldUniqList.append(adharterm)

def pan(key, input_dict):
    panterm = {"term": {"PAN_no": input_dict[key]}}
    shouldUniqList.append(panterm)

# def UnidentifiedPan(key,input_dict):
#     UnidenPanterm = {"match": {"PAN_no": int(input_dict[key])}}
#     shouldUniqList.append(UnidenPanterm)

def fuzziness_param(temp_name):
    if len(temp_name) > 4:
        return 3
    else:
        return 1


def name_suggestor(input_dict):
    s = Search(using=client,
               # index=["kyc4","agency22big"]
               index="kyc4"
               )
    nameSuggestSet = set()

    if "Name" in input_dict:
        text = input_dict['Name'].lower()

    else:
        text = input_dict['likeName'].lower()
    nameSuggestSet.add(text)

    regex = re.compile('[*?]')
    if regex.search(text) == None:
        # text='yadav ram'
        s = s.suggest('auto_complete', text, completion={'field': 'suggest'})
        # s = s.suggest('auto_complete', text, completion={'field': 'suggest','fuzzy':{
        #     "fuzziness": fuzziness_param(text),
        #     "prefix_length": 1,
        #     "transpositions": True
        #                 }})
        # print out all the suggest options we got and put it in a list
        response = s.execute()
        for option in response.suggest.auto_complete[0].options:
            # nameSuggestList.append(option._source.Name)
            nameSuggestSet.add(option._source.Name.lower())
        # print('%10s: %25s (%d)' % (text[0], option._source.Name, option._score))
    else:
        s = s.query("wildcard", Name=text)
        response = s.execute()
        for hit in response['hits']['hits']:
            # nameSuggestList.append(hit['_source']['Name'])
            nameSuggestSet.add(hit['_source']['Name'])

    print(nameSuggestSet,"----suggest list")
    return nameSuggestSet

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=
def name(key, input_dict):
    """ name_suggestor(input_dict)
    text = input_dict['Name']
    regex = re.compile('[*?]')
    if regex.search(text) == None:
        if len(text)>3:
            nameQuery = {
                        "multi_match": {
                            "query": text,
                            "analyzer": "metaphone_analyzer",
                            "fuzziness": fuzziness_param(text),
                            "fields": ["Name", "full_name","permuted_name"],
                            "prefix_length": 1,
                            "minimum_should_match": "80%",
                            # "rewrite": "constant_score" #no supprt +no transposition
                            # "type": "cross_fields", #not this if fuzzy
                            # "fuzziness": fuzziness_param(val), #gives absurd result
                            # "fields": ["full_name"],
                            "boost": 3
                        }
                    }
        else:
            nameQuery = {
                "multi_match": {
                    "query": text,
                    "fields": ["Name", "full_name","permuted_name"],
                    "prefix_length": 1,
                    "fuzziness": fuzziness_param(text),
                    "minimum_should_match": "100%",
                    # "rewrite": "constant_score" #no supprt +no transposition
                    # "type": "cross_fields", #not this if fuzzy
                    # "fuzziness": fuzziness_param(val), #gives absurd result
                    # "fields": ["full_name"],
                    "boost": 3
                }
            }
        # nameQuery = {
        #         "more_like_this": {    #no fuzzy support
        #             "fields": ["full_name"],
        #             "like": text,
        #             "min_term_freq": 1,
        #             "max_query_terms": 2,
        #             "min_doc_freq": 1,
        #             "include":True
        #         }
        #     }

        # nameQuery = {"match_phrase_prefix": {
        #     "permuted_name": { #no fuzzy support
        #         "query": text,
        #         "max_expansions": 10
        #     }
        # }}

        # nameQuery ={"fuzzy": {
        #     "permuted_name": {
        #         # "value": text,
        #         "value": text,
        #         # "fuzziness": "AUTO",
        #         "fuzziness": fuzziness_param(text),
        #         "max_expansions": 50,
        #         "prefix_length": 1,
        #         "transpositions": True,
        #         "rewrite": "constant_score"
        #     }}}

    else:
        text_list=text.split()
        mustnameList=[]
        for val in text_list:
            nameQuery = {"wildcard": {"Name": val}}
            mustnameList.append(nameQuery)
        nameQuery={"bool":{"must":mustnameList}}
    shouldnameList.append(nameQuery)"""  # correct
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++
    list_name = name_suggestor(input_dict)
    text = input_dict['Name']
    list_name.add(text)
    regex = re.compile('[*?]')
    if regex.search(text) == None:
        if len(list_name) != 1:  # if suggest is giving answer
            list_name.add(text)
            for val in list_name:
                # nameQuery = {"match": {"Name": val}} #no fuzzy support
                # nameQuery = {"match_phrase_prefix": {"full_name": {"query": val}}}
                # nameQuery = {"match_phrase_prefix": {"Name": val}}
                # nameQuery = {"match": {"Name": {"query": val, "fuzziness":"AUTO"}}}
                # nameQuery = {"match": {"Name": {"query":val,
                #                        "fuzziness":fuzziness_param(val),
                #                        "auto_generate_synonyms_phrase_query" : True
                #                                 }}}

                # nameQuery ={"match": {"Name": {"query": val,
                #         "analyzer": "metaphone_analyzer"
                #     }}}
                if len(val) < 4:
                    nameQuery = {"match": {"Name": val}}
                    # nameQuery = {"match_phrase_prefix": {"full_name": {"query": val}}}
                else:
                    # nameQuery ={"fuzzy": {
                    #     "full_name": {
                    #         "value": val,
                    #         # "fuzziness": "AUTO",
                    #         "fuzziness": fuzziness_param(val),
                    #         "max_expansions": 100,
                    #         "prefix_length": 1,
                    #         "transpositions": True,
                    #         "rewrite": "constant_score",
                    #         # "boost":3
                    #     }}} #doesnot work for full name i.e. if selected from dropdown

                    # nameQuery = {
                    #     "more_like_this": {  # no fuzzy support
                    #         "fields": ["full_name"],
                    #         "like": val,
                    #         "min_term_freq": 1,
                    #         "max_query_terms": 2,
                    #         "min_doc_freq": 1,
                    #         "include": True
                    #     }
                    # }

                    # nameQuery = {"match_phrase_prefix": {"permuted_name": {"query": val}}}
                    # nameQuery = {"match_phrase_prefix": {"permuted_name": val}}
                    # nameQuery = {"term": {"permuted_name": val}}
                    nameQuery = {
                        "multi_match": {
                            "query": val,
                            "fuzziness": "AUTO",
                            "fields": ["Name", "full_name"],
                            "prefix_length": 1,
                            "analyzer": "metaphone_analyzer",
                            "minimum_should_match": "100%",
                            # "rewrite": "constant_score" #no supprt +no transposition
                            # "type": "cross_fields", #not this if fuzzy
                            # "fuzziness": fuzziness_param(val), #gives absurd result
                            # "fields": ["full_name"],
                            "boost": 3
                        }
                    }

                shouldnameList.append(nameQuery)
        else:
            print("Fuzzy query>>>>>>>>>>>>>>>>>>")
            # nameQuery = {"fuzzy": {
            #     "full_name": {
            #         "value": text,
            #         "fuzziness": "AUTO",
            #         # "fuzziness": fuzziness_param(text),
            #         # "max_expansions": 100,
            #         "prefix_length": 1,
            #         "transpositions": True,
            #         "rewrite": "constant_score"
            #     }}}
            nameQuery = {
                "multi_match": {
                    "query": text,
                    "fuzziness": "AUTO",
                    "fields": ["Name", "full_name"],
                    "prefix_length": 1,
                    "analyzer": "metaphone_analyzer",
                    # "minimum_should_match": "100%",
                    # "rewrite": "constant_score" #no supprt +no transposition
                    # "type": "cross_fields", #not this if fuzzy
                    # "fuzziness": fuzziness_param(val), #gives absurd result
                    # "fields": ["full_name"],
                    "boost": 3
                }
            }
    else:
            text_list = text.split()
            mustnameList = []
            for val in text_list:
                nameQuery = {"wildcard": {"full_name": val}}
                mustnameList.append(nameQuery)
            nameQuery = {"bool": {"must": mustnameList}}
    shouldnameList.append(nameQuery)
              # correct


def likename(key, input_dict):
    """list_name = name_suggestor(input_dict)
    text = input_dict[key]
    list_name.add(text)
    if len(list_name) != 1:  # if suggest is giving answer
        list_name.add(text)
        for val in list_name:
            nameQuery = {
                    "multi_match": {
                        "query": val,
                        "fuzziness": "AUTO",
                        "fields": ["Name", "full_name"],
                        "prefix_length": 1,
                        "analyzer": "metaphone_analyzer",
                        "minimum_should_match": "100%",
                        "boost": 3
                    }
            }

            shouldnameList.append(nameQuery)
    else:
        print("Fuzzy query>>>>>>>>>>>>>>>>>>")
        nameQuery = {
            "multi_match": {
                "query": text,
                "fuzziness": "AUTO",
                "fields": ["Name", "full_name"],
                "prefix_length": 1,
                "analyzer": "metaphone_analyzer",
                "boost": 3
            }
        }
        shouldnameList.append(nameQuery)"""  # correct


    list_name = name_suggestor(input_dict)
    text = input_dict[key]
    list_name.add(text)
    print(list_name)
    for val in list_name:
        nameQuery = {
            "multi_match": {
                "query": val,
                "fuzziness": "AUTO",
                "fields": ["Name", "full_name"],
                "analyzer": "metaphone_analyzer",
                "prefix_length": 1,
                "minimum_should_match": "100%",
                # "rewrite": "constant_score" #no supprt +no transposition
                # "type": "cross_fields", #not this if fuzzy
                # "fuzziness": fuzziness_param(val), #gives absurd result
                # "fields": ["full_name"],
                "boost": 3
            }
        }
        # nameQuery ={"fuzzy": {
        #             "Name": {
        #                 "value": val,
        #                 "fuzziness": "AUTO",
        #                 # "analyzer": "metaphone_analyzer", #no support for fuzzy
        #                 # "fuzziness": fuzziness_param(val),
        #                 "max_expansions": 100,
        #                 "prefix_length": 1,
        #                 "transpositions": True,
        #                 "rewrite": "constant_score",
        #                 "boost":3
        #             }}} #doesnot work for full name i.e. if selected from dropdown
        shouldnameList.append(nameQuery)

def nameother(key, input_dict):
    name_suggestor(input_dict)
    text = input_dict['Name']
    regex = re.compile('[*?]')
    if regex.search(text) == None:
        if len(text) > 3:
            nameQuery = {
                "multi_match": {
                    "query": text,
                    "analyzer": "metaphone_analyzer",
                    "fuzziness": fuzziness_param(text),
                    "fields": ["Name", "full_name","permuted_name"],
                    "prefix_length": 1,
                    "minimum_should_match": "80%",
                    "boost": 3
                }
            }
        else:
            nameQuery = {
                "multi_match": {
                    "query": text,
                    "fields": ["Name", "full_name"],
                    "prefix_length": 1,
                    "minimum_should_match": "100%",
                    "boost": 3
                }
            }
    else:
        nameQuery = {"wildcard": {"Name": text}}
    shouldnameList.append(nameQuery)  # correct

def surname(key, input_dict):
    surnameQuery = {"match_phrase_prefix": {
        "Surname": {
            "query": input_dict[key],
            "max_expansions": 50,
        }
    }}
    shouldOtherList.append(surnameQuery)  # shoulList:correct


def father(key, input_dict):
    fatherNameQuery = {"match": {
        "Father_Name": {
            "query": input_dict[key],
            # "max_expansions": 50,
        }
    }}
    shouldOtherList.append(fatherNameQuery)  # mustList:correct


def mother(key, input_dict):
    motherNameQuery = {"match": {
        "Mother_Name": {
            "query": input_dict[key],
            # "max_expansions": 10,
        }}}
    shouldOtherList.append(motherNameQuery)  # shoulList:correct


def spouse(key, input_dict):
    spouseNameQuery = {"match": {
        "Spouse_Name": {
            "query": input_dict[key],
            "max_expansions": 50,
        }
    }}
    shouldOtherList.append(spouseNameQuery)  # shoulList:correct


def address(key, input_dict):
    # addressQuery = {"terms": {"Home_Address":input_dict[key]}}
    print(input_dict[key])
    for loc in input_dict[key]:
        # addressQuery = {"match": {"Home_Address": loc}}
        if loc.isdigit():
            addressQuery = {"term": {"Home_Address": loc}}
        else:
            addressQuery = {"match":{"Home_Address":loc}}
            # addressQuery = {"match": {"Home_Address": {"query": loc,
            #                                            "fuzziness": fuzziness_param(loc),
            #                                            "prefix_length": 3,
            #                                            "auto_generate_synonyms_phrase_query": True
            #                                            }}}
        shouldlocationList.append(addressQuery)  # shoulList:correct

def addressother(key, input_dict):
    # addressQuery = {"terms": {"Home_Address":input_dict[key]}}
    print(input_dict[key])
    for loc in input_dict[key]:
        # addressQuery = {"match": {"Home_Address": loc}}
        if loc.isdigit():
            addressQuery = {"term": {"Home_Address": loc}}
        else:
            addressQuery = {"match":{"Home_Address":loc}}
            # addressQuery = {"match": {"Home_Address": {"query": loc,
            #                                            "fuzziness": fuzziness_param(loc),
            #                                            "prefix_length": 3,
            #                                            "auto_generate_synonyms_phrase_query": True
            #                                            }}}
        shouldlocationList.append(addressQuery)  # shoulList:correct

def dob(key, input_dict):
    dobterm = {"range": {"Date_of_Birth": {
        "gte": input_dict[key],
        "lte": input_dict[key],
        "format": "yyyy-MM-dd"
    }}}
    shouldList.append(dobterm)

def gender(key, input_dict):
    genterm = {"match": {"Gender": input_dict[key].title()}}
    shouldOtherList.append(genterm)

def bloodgroup(key, input_dict):
    for val in input_dict[key]:
        bgterm = {"term": {"Blood_Group": val.upper()}}
    shouldOtherList.append(bgterm)

def passport(key, input_dict):
    passterm = {"term": {"Passport_no": input_dict[key]}}
    shouldUniqList.append(passterm)

def bank(key, input_dict):
    bankterm = {"term": {"BankAcDetails": input_dict[key]}}
    shouldUniqList.append(bankterm)

def credit(key, input_dict):
    creditterm = {"term": {"CreditCard": input_dict[key]}}
    shouldUniqList.append(creditterm)

def voter(key, input_dict):
    voterterm = {"term": {"Voter_Card_ID": input_dict[key]}}
    shouldUniqList.append(voterterm)

def drivinglicence(key, input_dict):
    licenseterm = {"term": {"DL": input_dict[key]}}
    shouldUniqList.append(licenseterm)

def mobile(key, input_dict):
    # for mob in input_dict[key]:
    #     mobterm = {"terms": {"Mobile_No": mob}}
    mobterm = {"terms": {"Mobile_No": input_dict[key]}}
    shouldUniqList.append(mobterm)

def email(key, input_dict):
    for mail in input_dict[key]:
        # mailterm = {"match_phrase_prefix":{"Email_Id": mail}}  #correct:match_prefix for mail
        mailterm = {"term": {"Email_Id": mail}}  # correct:match_prefix for mail
        shouldUniqList.append(mailterm)

def nationality(key, input_dict):
    for nation in input_dict[key]:
        nationQuery = {"match": {"Nationality": nation}}
        shouldnationList.append(nationQuery)

def age(key, input_dict):
    ageterm = {"Age": {"gte": int(input_dict[key][0]),
                       "lte": int(input_dict[key][0])}}
    # for MID queries:
    # ageterm = {"Age": {"gte": int(input_dict[key][0]) - 5,
    #                    "lte": int(input_dict[key][0]) + 5}}
    shouldOtherList.append({"range": ageterm})  # correct final

def YOB(key, input_dict):
    print("key is......",key)
    # print("Input Dict is......",input_dict, int(input_dict[key][1]))
    yearterm = {"year_of_Birth": {"gte": int(input_dict[key][0]),
                      "lte": int(input_dict[key][0])}}
    # yearterm = {"year_of_Birth": {"gte": int(input_dict[key][1]),
    #                               "lte": int(input_dict[key][0])}}
    # for MID queries:
    # ageterm = {"Age": {"gte": int(input_dict[key][0]) - 5,
    #                    "lte": int(input_dict[key][0]) + 5}}
    shouldOtherList.append({"range": yearterm})  # correct final

def ageother(key, input_dict):
    ageterm = {"year_of_Birth": {
                       "gte": int(input_dict[key][1]),
                        "lte": int(input_dict[key][0])}}
    shouldOtherList.append({"range": ageterm})  # correct final

def ageover(key, input_dict):
    # print(input_dict[key][0],"hiiiiiiiiiiiii")
    ageterm = {"year_of_Birth": {"lte": input_dict[key][0]}}
    shouldOtherList.append({"range": ageterm})  # correct final

def agebelow(key, input_dict):
    ageterm = {"year_of_Birth": {"gt": int(input_dict[key][0])}}
    shouldOtherList.append({"range": ageterm})  # correct final

def notquery(key, input_dict):
    for key, value in input_dict[key].items():
        for itr in value:
            notTerm = {"match": {key: itr}}
            NotList.append(notTerm)

def unidentified(key, input_dict):
    unidenTerm={
        "query": {
            "multi_match": {
                "query": input_dict[key],
                "fields": ["Name", "Surname", "Home_Address"]
            }
        }
    }
    shouldOtherList.append({"range": unidenTerm})

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=
def dynamic_switch(arg):
    switcher = {
        "Aadhar_no": adharno,
        "PAN_no": pan,
        "Name": name,
        "Surname": surname,
        "Father_Name": father,
        "Mother_Name": mother,
        "Spouse_Name": spouse,
        "Date_of_Birth": dob,
        "Gender": gender,
        "Blood_Group": bloodgroup,
        "Home_Address": address,
        # "Office_Address": {"type": "text"},
        # "Communication_Address": {"type": "text"},
        "Passport_no": passport,
        "BankAcDetails": bank,
        "CreditCard": credit,
        "Mobile_No": mobile,
        "Email_Id": email,
        "Nationality": nationality,
        "Voter_Card_ID": voter,
        "DL":drivinglicence,
        # "Age": age,
        "ageOther": ageother,
        "AgeOver": ageover,
        "AgeBelow": agebelow,
        "likeName": likename,
        "nameOther":nameother,
        "addressOther":addressother,
        "notQuery": notquery,
        "year_of_Birth": YOB,
        "Unidentified":unidentified
    }
    # get() method of dictionary data type returns value of passed argument if it is present in dictionary otherwise second argument will be assigned as default value of passed argument
    # return switcher.get(arg, lambda key,val : "invalid input")
    return switcher.get(arg, lambda key1: "invalid input")


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=
def search_output(input_dict, kyc_list_input,query):
    # kyc_list_input = []
    global mustList, shouldList, shouldOtherList, shouldUniqList, shouldnameList, shouldkycList
    global shouldnationList, shouldlocationList, TotResponse, x, NotList
    mustList = []
    shouldList = []
    shouldOtherList = []
    shouldUniqList = []
    shouldnameList = []
    shouldkycList = []
    shouldnationList = []
    shouldlocationList = []
    NotList = []
    TotResponse = 0
    OtherList=[]
    x = []

    for key in input_dict:
        method = dynamic_switch(key)
        # method(key,val)
        method(key, input_dict)

    kycattribute(kyc_list_input)
    if len(shouldkycList) != 0:
        mustList.append({"bool": {"should": shouldkycList}})
        flagSearch="valid"
    if len(shouldUniqList) != 0:
        mustList.append({"bool": {"should": shouldUniqList}})
        res = Query(mustList)
        TotResponse = res['hits']['total']['value']
        print("Got KYC Hits:", TotResponse)
        if TotResponse != 0:
            x = Response(res, input_dict)
            flagSearch = "valid"
        mustList.pop(1)

    if (TotResponse == 0):
        if len(shouldnameList) != 0:
            mustList.append({"bool": {"should": shouldnameList}})
            res = Query(mustList)
            TotResponse = res['hits']['total']['value']
            print("Got Name Hits:", TotResponse)
            if TotResponse != 0:
                x = Response(res, input_dict)
                flagSearch = "valid"
            # del mustList[1:2]
            mustList.pop(1)
        else:
            print("In fuzzy not bool query")
            try:
                mustList.append(shouldnameList[0])
                res = Query(mustList)
                TotResponse = res['hits']['total']['value']
                print("Got Name Hits:", TotResponse)
                if TotResponse != 0:
                    x = Response(res, input_dict)
                    flagSearch = "valid"
                # del mustList[1:2]
                mustList.pop(1)
            except:
                IndexError


    if (TotResponse == 0):
        if len(shouldList) != 0:
            # mustList.append(shouldList[0])
            mustList.append({"bool": {"should": shouldList}})
            res = Query(mustList)
            TotResponse = res['hits']['total']['value']
            print("Got Date Hits:", TotResponse)
            if TotResponse != 0:
                x = Response(res, input_dict)
                flagSearch = "valid"
            # del mustList[1:2]
            mustList.pop(1)
    if (TotResponse == 0):
        counter = 0
        if len(shouldnationList) != 0:
            mustList.append({"bool": {"should": shouldnationList}})
            counter = counter + 1
        if len(shouldlocationList) != 0:
            mustList.append({'bool': {'should': shouldlocationList}})
            counter = counter + 1
        if len(shouldOtherList) != 0:
            mustList.append({"bool": {"must": shouldOtherList}})
            counter = counter + 1
        if counter != 0:
            res = Query(mustList)
            TotResponse = res['hits']['total']['value']
            print("Got Other Hits:", TotResponse)
            x = Response(res, input_dict)
            flagSearch = "valid"
        else:
            print("NO RESULT FOUND..Finding some more data for..",query)
            body={
                "query": {
                    "query_string": {
                        "query": query
                    }
                }
            }
            # headers = {
            #     "Content-Type":"application/json"
            # }
            # res1 = requests.post('http://localhost:9200/kyc3/_search',data=json.dumps(body), headers=headers)
            # print(res1.text)
            # print(res1.json())
            res = client.search(
                # index=["kyc4","agency22big"],
                index="kyc4",
                body=body, size=2000, request_timeout=30)
            print("+++++++++",res['hits']['hits'])
            TotResponse = res['hits']['total']['value']
            print("Got Query Hits:", TotResponse)
            for hit in res['hits']['hits']:
                del hit['_source']['permuted_name']
                del hit['_source']['suggest']
                del hit['_source']['Created_timestamp']
                del hit['_source']['Sr._No.']
                del hit['_source']['year_of_Birth']
                OtherList.append(hit['_source'])
            x = OtherList
            flagSearch = "random"
    print(flagSearch)
            # x = Response(res, input_dict)
    print("++++++++++++++++++++++++++++++++++++++++++++++")
    return x,flagSearch


def Query(mustList):
    Dict_all = dict()
    if len(mustList) != 0:
        Dict_all.update({"must": mustList})
    if len(NotList) != 0:
        Dict_all.update({"must_not": NotList})

    # print(Dict_all)
    # body={"sort": [
    #         {"post_date": {"order": "asc"}},
    #         "user",
    #         {"Name": "desc"},
    #         {"Age": "desc"},
    #         "_score"
    #     ],
    #     "query": {"bool": Dict_all}}

    body = {"query": {"bool": Dict_all}}
    print("This is the query:-", body)
    res = client.search(
        # index=["kyc4","agency22big"],
        index="kyc4",
        body=body, size=2000, request_timeout=30)
    return res


def Response(res, input_dict):
    output_list = []
    output_list_more=[]
    result=[]
    try:
        del input_dict['notQuery']
    except KeyError:
        print("Key 'notQuery' not found")

    for hit in res['hits']['hits']:
        # print(hit['_id'])
        # print(hit['_source'])
        #     desired_order_list = ["Sr._No.","ConfidenceScore","full_name",
        #  "KYC_Attributes", "Surname", "Name", "Father_Name", "Mother_Name", "Spouse_Name", "Date_of_Birth",
        # "Gender", "Blood_Group", "Home_Address", "Office_Address", "Communication_Address", "PAN_no", "Aadhar_no",
        # "Passport_no","DL", "BankAcDetails", "CreditCard", "Mobile_No", "Email_Id", "Nationality", "Voter_Card_ID","Age"]
        #
        #     reordered_dict = {k: hit['_source'][k] for k in desired_order_list}
        #     print(reordered_dict)
        newconfdict = confidenceScoreNewValue_correct.search_input(input_dict, hit['_id'], hit['_source'])
        del newconfdict['permuted_name']
        del newconfdict['suggest']
        del newconfdict['Created_timestamp']
        del newconfdict['Sr._No.']
        del newconfdict['year_of_Birth']
        if newconfdict['ConfidenceScore']>95:
            output_list.append(newconfdict)
        elif newconfdict['ConfidenceScore']>0 and newconfdict['ConfidenceScore']<=95:
            output_list_more.append(newconfdict)
    result.append(output_list)
    result.append(output_list_more)
    # with open(r'/home/sunbeam/Desktop/Agency22/myproject/data/Result.json', 'w') as fp:
    #         json.dump(output_list, fp)
    return result

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=

def get_index_by_id(id):
    print("hiiiii Sapna the Id is:",id)
    results = client.get(
        index="kyc4",
        id=id)
    return results


def kyc_data():
    print("Enter your choice--- \n"
          "0:'All' \n"
          "1:'Aadhar', \n"
          "2:'Pan', \n"
          "3:'Passport', \n"
          "4:'NCRB', \n"
          "5:'Airline', \n"
          "6:'Company KYC', \n"
          "7:'Driving License', \n"
          "8:'Telecom', \n"
          "9:'Voter ID Card',\n"
          "10:'Bank KYC':- \n")
    kyc = int(input("Enter your choice--- "))
    if kyc is 1:
        kyc_list_input.append('Aadhar')
    elif kyc is 2:
        kyc_list_input.append('Pan')
    elif kyc is 3:
        kyc_list_input.append('Passport')
    elif kyc is 4:
        kyc_list_input.append('NCRB')
    elif kyc is 5:
        kyc_list_input.append('Airline')
    elif kyc is 6:
        kyc_list_input.append('Company KYC')
    elif kyc is 7:
        kyc_list_input.append('Driving License')
    elif kyc is 8:
        kyc_list_input.append('Telecom')
    elif kyc is 9:
        kyc_list_input.append('Voter ID Card')
    elif kyc is 10:
        kyc_list_input.append('Bank KYC')
    else:
        pass
    ch = input('Do you want to continue....Yes..Y or No...N')
    if ch == 'Y' or ch == 'y' or ch == 'yes' or ch == 'YES':
        kyc_data()
    else:
        pass
    return kyc_list_input


def call_app(query, kyc_list_input):
    input_dict = confidenceScoreNewValue_correct.main(query)
    search_output(input_dict, kyc_list_input)


# for manually running:-------
# kyc_list_input = kyc_data()
# print(kyc_list_input)
# query=input("Enter query...:-")
# call_app(query,kyc_list_input)
# relevance_score.main()


# name is dines
# age is 25
# Ramch Yadav an Indian mlae wih age 42      :correct
# Ramch Yadav an Indian mlae adhar no. 123456789101 :correct
# Ramch Yadav an Indian mlae and adhar no. 123456789101,ABCDE1234F or J1234567
# Ram an Indian mlae and adhar no. 123456789101,ABCDE1234F or J1234567 b+
# name is dines , mother is jaya
# name is Amar Gurnani, mother is jaya
# ABCDE1234F a male and an indian having B+ blood group
# Ramcharan Yadav an Indian male with age 78 and adhar 123456789101,ABCDE1234F or J1234567
# Rajashtan
# ramadulla 1959-09-23
# Lakshmi BM Desai , Father Name Bijoya  , Mother Name Muktai  , Spouse name is  Jaydev , age 40 , Female , Alaknanda Villas , Jaipur  878886068589 , lbmd@gmail.com , Indian
# Lakshmi BM Desai , Father Name Bijoya  , Mother Name Muktai  , Spouse name is  Jaydev , age 40 , Female , Alaknanda Villas , Jaipur  878886068589,lbmd@gmail.com	,Indian
