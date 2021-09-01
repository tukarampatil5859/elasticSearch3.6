import csv, json, os
import sys
import re
import tqdm
from itertools import permutations
import urllib3
import pandas as pd
import datetime
from elasticsearch.helpers import bulk, streaming_bulk, parallel_bulk
# import confidenceScore
from datetime import date
import pandas as pd
import _datetime

today = _datetime.date.today()

# Import Elasticsearch package
from elasticsearch import Elasticsearch

global id


# to start/run elastic search terminal cmd:sudo  service elasticsearch start
# ++++++++++++++++++++++++++++++++++++++
# custom analyzer for names
# ==================================================================================
def connect_elasticsearch():
    client = Elasticsearch(
        # Add your cluster configuration here!"sniff":To inspect the cluster state to get a list of nodes upon startup, periodically and/or on failure
        [{'host': 'localhost', 'port': 9200}], maxsize=25,
        timeout=30, sniff_on_start=True,
        sniff_on_connection_fail=True,
        sniffer_timeout=60,
        sniff_timeout=10,
        max_retries=10
        # If your application is long-running consider turning on Sniffing to make sure the client is up to date on the cluster location.
    )  # allow up to 25 connections to each node
    if client.ping():
        print('Connected to ElasticSearch!!!!')
    else:
        print('ElasticSearch could not connect!!!!')
    # es = Elasticsearch(["host1", "host2"], maxsize=25)
    return client


# ==================================================================================
def create_index(client):
    """Creates an index in Elasticsearch if one isn't already there."""
    # or: elastic = Elasticsearch(hosts=["localhost"])

    # mapping dictionary that contains the settings and
    # _mapping schema for a new Elasticsearch index:
    mapping = {"settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "default_pipeline": "time_pipeline",
        # "index.default_pipeline": "access_log",
        "analysis": {
            "analyzer": {
                "edge_ngram": {
                    "filter": ["lowercase", "edge_ngram_filter"],
                    "tokenizer": "standard",
                    # "type": "custom"
                },

                "my_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "snowball", "my_multiplexer"]
                },

                "analyzer_case_insensitive": {
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                },

                "ascii_fold_my": {
                    "tokenizer": 'whitespace',
                    "filter": ['lowercase', 'ascii_folding_filter']},

                'metaphone_analyzer': {
                    "type": "custom",
                    'tokenizer': 'standard',
                    'filter': [
                        'ascii_folding_filter', 'lowercase', 'metaphone_filter'
                    ]}},

            "filter": {
                "edge_ngram_filter": {
                    "max_gram": "15",
                    "min_gram": "2",
                    "side": "front",
                    "type": "edgeNGram"},

                'ascii_folding_filter': {
                    'type': 'asciifolding',
                    'preserve_original': True
                },
                'metaphone_filter': {
                    'type': 'phonetic',
                    # 'encoder': 'metaphone',
                    # 'encoder': 'soundex',
                    # 'encoder': 'refinedsoundex',
                    'encoder': 'doublemetaphone',
                    # 'encoder': 'nysiis',
                    # 'encoder': 'cologne',
                    'replace': False
                },
                "my_multiplexer": {
                    "type": "multiplexer",
                    "filters": ["lowercase", "lowercase, porter_stem"]
                }
            }
        }
    },
        "mappings": {
            "_source": {"enabled": True},
            "properties": {
                "Sr._No.": {"type": "integer"},
                "KYC_Attributes": {"type": "keyword"},
                "Surname": {"type": "text",
                            "analyzer": "metaphone_analyzer",  # correct->phonetic analyzer
                            "search_analyzer": "edge_ngram",
                            # "search_quote_analyzer": "my_analyzer",
                            # "copy_to": "full_name"
                            },
                "Name": {"type": "text",
                         "analyzer": "metaphone_analyzer",  # correct->phonetic analyzer
                         "search_analyzer": "edge_ngram",
                         # "analyzer": "analyzer_case_insensitive"
                         # "index_analyzer":"my_analyzer", #not supported
                         # "search_quote_analyzer": "my_analyzer",
                         # "copy_to": "full_name"
                         },
                "full_name": {
                    "analyzer": "metaphone_analyzer",
                    #               "search_analyzer":"edge_ngram",
                    "type": "text"},
                "Father_Name": {"type": "text", "analyzer": "my_analyzer"},
                "Mother_Name": {"type": "text", "analyzer": "my_analyzer"},
                "Spouse_Name": {"type": "text", "analyzer": "my_analyzer"},
                "Date_of_Birth": {"type": "date", "format": "yyyy-MM-dd"},
                "Gender": {"type": "text", "analyzer": "my_analyzer"},
                "Blood_Group": {"type": "keyword"},
                "Home_Address": {"type": "text"},
                "Office_Address": {"type": "text"},
                "Communication_Address": {"type": "text"},
                "PAN_no": {"type": "text", "analyzer": "my_analyzer"},
                "Aadhar_no": {"type": "keyword"},
                "Passport_no": {"type": "keyword"},
                "BankAcDetails": {"type": "keyword"},
                "CreditCard": {"type": "keyword"},
                "Mobile_No": {"type": "keyword"},
                "Email_Id": {"type": "keyword"},
                "Nationality": {"type": "text"},
                "Voter_Card_ID": {"type": "text", "analyzer": "my_analyzer"},
                # "Age": {"type": "integer"},
                "permuted_name": {"type": "text"},  # "index":False,"norms": False
                "DL": {"type": "text", "analyzer": "analyzer_case_insensitive", },
                "suggest": {"type": "completion",
                            # "analyzer": "ascii_fold_my"
                            },
                "year_of_Birth": {"type": "integer"},
                # "query": {"type": "percolator"},
                # "CreatedDate":{
                #         "_timestamp" : {
                #             "enabled" : True,
                #             "store" : True
                #         }
                #     },
                # "ModifiedDate":{"_timestamp" : {
                #             "enabled" : True,
                #             "store" : True
                #         }}
            }
        }
    }
    # make an API call to the Elasticsearch cluster
    # and have it return a response:
    # es.index(index='kyc2', doc_type='Blog2', id=id,
    # body={"settings": {"number_of_shards": 1},"data":json.dumps(csvRow),"timestamp": datetime.now()},ignore=400,)

    response = client.indices.create(
        index="kyc4",
        body=mapping,
        ignore=400  # ignore 400 already exists code
    )

    if 'acknowledged' in response:
        if response['acknowledged'] == True:
            print("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])

    # catch API error response
    elif 'error' in response:
        print("ERROR:", response['error']['root_cause'])
        print("TYPE:", response['error']['type'])

    # print out the response:
    print('\nresponse:', response)


# ==================================================================================
def generate_actions(path, id):
    """Reads the file through csv.DictReader() and for each row
    yields a single document. This function is passed into the bulk()
    helper to create many documents in sequence.

    """
    csvFilePath = path
    data = {}
    # # read the csv and add the data to a dictionary
    with open(csvFilePath) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for csvRow in csvReader:
            # id = csvRow["Sr._No."]
            # id = id1
            # name = csvRow["Name"]
            id_new = "kyc" + str(id)
            # csvRow["NameR"]=csvRow["Name"].replace(" ","")
            full_name = csvRow["Name"] + ' ' + csvRow["Surname"]
            csvRow["full_name"] = full_name

            suggest = {
                'input': [' '.join(p) for p in permutations(full_name.split())],
                # 'weight': self.popularity
            }
            csvRow["suggest"] = suggest
            csvRow["permuted_name"] = [' '.join(p) for p in permutations(full_name.split())]
            doc = {"_id": id_new, "_source": json.dumps(csvRow)}
            id = id + 1

            yield doc


##########################################################
def date_normalizer(df):
    df['Date_of_Birth'] = pd.to_datetime(df['Date_of_Birth'], errors='coerce')
    x = datetime.datetime.now()
    date_list = []
    for val in df['Date_of_Birth']:
        if val.year > x.year:
            val = val.replace(val.year - 100)
            date_list.append(val)
            # print(val)
        else:
            # print(val)
            date_list.append(val)
    df['Date_of_Birth'] = date_list


# def calculateAge(birthDate):
#     today = date.today()
#     age = today.year - birthDate.year -((today.month, today.day) < (birthDate.month, birthDate.day))
#     age=pd.to_datetime('today').year - pd.to_datetime(birthDate).year
#     return age
def calculateAge(birthDate):
    days_in_year = 365.2425
    age = int((date.today() - birthDate).days / days_in_year)
    return age


def clean_csv(path):
    df = pd.read_csv(path)
    date_normalizer(df)
    age_list = []
    year_list = []

    for date in df['Date_of_Birth']:
        # date=str(date)
        # datee = datetime.datetime.strptime(date, "%Y-%m-%d")
        # yy = datee.year
        # m = datee.month
        # d = datee.day
        # age = calculateAge(date(yy,m,d))
        YOB = date.year
        # age_list.append(age)
        year_list.append(YOB)

    # df['Age'] = age_list
    df['year_of_Birth'] = year_list
    date_list = []
    # df['Date_of_Birth'].fillna(df['Date_of_Birth'].mode().values[0], inplace=True)
    df['Date_of_Birth'].fillna("0000-00-00", inplace=True)
    for val in df['Date_of_Birth']:
        val = pd.to_datetime(val, errors='coerce').date()
        date_list.append(val)
    df['Date_of_Birth'] = date_list

    # Name Normalizer and standardizer with removal of extra space and . in names
    name_list = []
    for name in df["Name"]:
        # name=re.sub(r'(?<!\w)([A-Z])\.*\s*(?<!\w)([A-Z])\.*\s*([A-Za-z]*)', r'\1\2 \3', name)
        # print(name)
        line = re.sub(r" +|\. *", " ", name)
        # line = re.sub(r"\b([a-zA-Z]) ([a-zA-Z])\b", "\g<1>\g<2>", line)
        name_list.append(line)
    df['Name'] = name_list

    # address normaliser by replacing (, . -) with space
    addr_list = []
    for addr in df["Home_Address"]:
        addr = addr.replace(",", " ").replace(".", " ").replace("-", " ")
        addr_list.append(addr)
    df["Home_Address"] = addr_list

    # adhar number after decimal removal:

    df["Aadhar_no"].fillna(0, inplace=True)
    df["BankAcDetails"].fillna(0, inplace=True)
    df["Mobile_No"].fillna(0, inplace=True)
    # df["PAN_no"].fillna('0', inplace=True)
    # df["Passport_no"].fillna('0', inplace=True)
    # df["BankAcDetails"].fillna('0', inplace=True)
    listAll1 = []
    for adhar in df["Aadhar_no"]:
        listAll1.append(int(adhar))
    df["Aadhar_no"] = listAll1
    listAll2 = []
    for mob in df["Mobile_No"]:
        if type(mob) == float:
            listAll2.append(round(mob))

        else:
            listAll2.append(mob)
    df["Mobile_No"] = listAll2
    listAll3 = []
    # for bank in df["BankAcDetails"]:
    #     listAll3.append(round(bank))
    #     df["BankAcDetails"] = listAll3

    df.to_csv(path, index=False)


##########################################################

def main():
    print("Loading dataset...")
    # number_of_docs =359
    client = connect_elasticsearch()
    print("Creating an index...")
    create_index(client)
    id = 1
    tot = 0
    filepath = '/home/tukaram/PycharmProjects/elasticSearch/All/'  # for example: './my_data/'
    all = list(filter(lambda x: '.csv' in x, os.listdir(filepath)))
    for file in all:
        path = filepath + '/' + file
        print("===============================================")
        print("The file path is...", path)
        # unhash below line on first run:----------
        # In csv: Change headers+in DL change DrivingLicense in KYC_attribute
        clean_csv(path)
        # ----------------------------------------
        input_file = open(path, "r+")
        reader_file = csv.reader(input_file)
        number_of_docs = len(list(reader_file)) - 1
        tot = tot + number_of_docs

        print("Indexing documents...")
        progress = tqdm.tqdm(unit="docs", total=number_of_docs)
        successes = 0

        # for ok, action in streaming_bulk(
        #         client=client, index="lpg", actions=generate_actions(), thread_count=4):
        for ok, action in parallel_bulk(
                client=client, index="kyc4", actions=generate_actions(path, id), thread_count=4):
            progress.update(1)
            successes += ok
            # Dup_Ingest_Check.main()
        id = tot
        print("Indexed parallel %d/%d documents" % (successes, number_of_docs))
    print("The total doc ingested", tot)


# ==================================================================================

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################
if __name__ == "__main__":
    main()
    # es=connect_elasticsearch()
    # res = es.search(index="kyc", body={"query": {"match": {"KYC_Attributes": "Passport"}}})
    # print(res['hits']['hits'])
    # print(f"Got {res['hits']['total']['value']} total match Hits")
