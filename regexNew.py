import re, json, os
import sys
from datetime import date  ##changed18aug
import lexnlp
import lexnlp.extract.en.dates
import lexnlp.extract.en.pii
import lexnlp.extract.en.constraints
import regex as re
import lexnlp.extract.en.amounts
import lexnlp.extract.en.durations
import lexnlp.nlp.en.tokens
import lexnlp.extract.en.geoentities
import lexnlp.extract.en.conditions
from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.en.geoentities import get_geoentities, load_entities_dict_by_path
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# from pattern.en import pluralize, singularize
from elasticsearch import Elasticsearch
import datetime

# from spacy.tokens.span import Span

###############################################################################
# download the libraries of nltk in your system by uncommenting the below two lines:
# nltk.download('stopwords')
# nltk.download('punkt')
###############################################################################

set(stopwords.words('english'))
import string
import datetime

# fields=dict()
global fields, unidentifiedDict, regexRemoveList,ageList_over,ageList_below,addresslist, dateList_fn, nation_list, loc_list, loc_list_set, age_complex, age_range, age_mid_list, token_index, ageList, bloodgroupList, genderList, not_list, age_approx, age_to, ageList_normal, email, mobile, dropdown_dict
# global HA_Check, Pn_Check, MN_Check, AN_Check

# unidentifiedDict = dict()
Nationality = ['Afghan', 'Albanian', 'Algerian', 'Argentine Argentinian', 'Australian', \
               'Austrian', 'Bangladeshi', 'Belgian', 'Bolivian', 'Batswana', 'Brazilian', 'Bulgarian', \
               'Cambodian', 'Cameroonian', 'Canadian', 'Chilean', 'Chinese', 'Colombian', 'Costa Rican' \
                                                                                          'Croatian', 'Cuban', 'Czech',
               'Danish', 'Dominican', 'Ecuadorian', 'Egyptian', 'Salvadorian', \
               'English', 'Estonian', 'Ethiopian', 'Fijian', 'Finnish', 'French', 'German', 'Ghanaian', 'Greek', \
               'Guatemalan', 'Haitian', 'Honduran', 'Hungarian', 'Icelandic', 'Indian', 'Indonesian', 'Iranian', \
               'Iraqi', 'Irish', 'Israeli', 'Italian', 'Jamaican', 'Japanese', 'Jordanian', 'Kenyan', 'Kuwaiti', \
               'Lao', 'Latvian', 'Lebanese', 'Libyan', 'Lithuanian', 'Malaysian', 'Malian', 'Maltese', 'Mexican', \
               'Mongolian', 'Moroccan', 'Mozambican', 'Namibian', 'Nepalese', 'Dutch', 'New Zealand', 'Nicaraguan', \
               'Nigerian', 'Norwegian', 'Pakistani', 'Panamanian', 'Paraguayan', 'Peruvian', 'Philippine', 'Polish', \
               'Portuguese', 'Romanian', 'Russian', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Singaporean', \
               'Slovak', 'South African', 'Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Swedish', 'Swiss', \
               'Syrian', 'Taiwanese', 'Tajikistani', 'Thai', 'Tongan', 'Tunisian', 'Turkish', 'Ukrainian', 'Emirati', \
               'British', 'American', 'Uruguayan', 'Venezuelan', 'Vietnamese', 'Welsh', 'Zambian', 'Zimbabwean']

choice = 0
test_list = []
monthList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
             'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug',
             'Sept', 'Nov', 'Dec', 'Sep', 'Oct']


def dateExtractor(query):
    test_list_date = []
    # print("In query : ",query)
    dateList11 = list(lexnlp.extract.en.dates.get_dates_list(query, strict=False, base_date=None, return_source=False,
                                                             threshold=0.5))
    if len(dateList11) != 0:
        dateVal = dateList11[0]
        # print(dateVal)
        # print(type(dateVal))

        dateVal1 = dateVal.strftime('%Y-%m-%d')
        # print(dateVal1)
        # print(type(dateVal1))

        fields['Date_of_Birth'] = dateVal1

        y = list(lexnlp.extract.en.dates.get_date_annotations(query))
        # print(y)
        lst11 = str(y)
        lst12 = queryTypeChecker(lst11)

        s1 = re.findall(r"(\d{1,}..\d{1,})", lst12)
        # print(s1)
        lst1 = [x.replace("..", ",") for x in s1]
        # print(lst1)

        lstSplit = []
        dltLocn = []
        for i in lst1:

            lstSplit = i.split(",")
            s1 = lstSplit[0]
            e = lstSplit[1]
            s1 = int(s1)
            e1 = int(e)

            # print("Start locn : ",s1,"End locn : ",e1)
            l_query = len(query)
            # print("Length of query is : ",l_query)

            if s1 == 0 and l_query == e1:
                e1 = e1 - 1
                test_list_date = posnCalc(s1, e1)
            elif s1 == 0 and l_query != e1:
                e1 = e1 - 2
                test_list_date = posnCalc(s1, e1)
            elif s1 != 0 and l_query == e1:
                s1 = s1 + 1
                e1 = e1 - 1
                test_list_date = posnCalc(s1, e1)
            elif s1 != 0 and l_query != e1:
                s1 = s1 + 1
                e1 = e1 - 2
                test_list_date = posnCalc(s1, e1)
            # print("test_list_date : ",test_list_date)
    return test_list_date


def posnCalc(s1, e1):
    posn_date_list = []
    for i in range(s1, e1 + 1):
        posn_date_list.append(i)
    # print("Inner : ",posn_date_list )
    return posn_date_list


# location lexnlp:-

def load_entities_dict():
    base_path = os.path.join(lexnlp_test_path, 'lexnlp/extract/en/tests/test_geoentities')
    entities_fn = os.path.join(base_path, '/home/sunbeam/Desktop/kyc_data_sir/geoentitiesCity.csv')
    aliases_fn = os.path.join(base_path, '/home/sunbeam/Desktop/kyc_data_sir/geoaliasesCity.csv')
    return load_entities_dict_by_path(entities_fn, aliases_fn)

'''
# Prajakta file path
def load_entities_dict():
    base_path = os.path.join(lexnlp_test_path, 'lexnlp/extract/en/tests/test_geoentities')
    entities_fn = os.path.join(base_path, '/home/aai/PrajaktaMemaneAai/lexnlpdata/geoentitiesCity.csv')
    aliases_fn = os.path.join(base_path, '/home/aai/PrajaktaMemaneAai/lexnlpdata/geoaliasesCity.csv')
    return load_entities_dict_by_path(entities_fn, aliases_fn)
'''

_CONFIG = list(load_entities_dict())


def addrExtractor(text):
    test_list = []
    text = strQuotesChecker_reverse(text)  ##changed19aug
    # print("aftr dlt _ text " ,text)
    text = text.title()

    #
    print("text from addr: ",text)
    x = list(lexnlp.extract.en.geoentities.get_geoentities(text, geo_config_list=_CONFIG))

    print("x from addr: ",x)
    print("loc list : ",loc_list)
    for val in x:
        print("val ",val[1])
        loc_list.append(val[0][1].lower())  # entities

    y = list(lexnlp.extract.en.geoentities.get_geoentity_annotations(text, geo_config_list=_CONFIG))
    # print("y : ",y)
    lst11 = str(y)
    lst12 = queryTypeChecker(lst11)
    s1 = re.findall(r"(\d{1,}..\d{1,})", lst12)
    # print(s1)
    lst1 = [x.replace("..", ",") for x in s1]
    # print("lst1 : ",lst1)
    # print("In addr len q :::",len(query))
    for i in lst1:
        lstSplit = i.split(",")
        s1 = lstSplit[0]
        e = lstSplit[1]
        s1 = int(s1)
        e = int(e)
        e1 = e - 2

        # print("Start locn : ",s1,"End locn : ",e1)
        for i in range(s1, e1 + 1):
            # print("i :: ",i)
            test_list.append(i)

        # print("test_list : ",test_list)
        # print("s1 : ",s1)
        # print("s1 : ", text[s1])
        # print("e1 : ",e1)
        # print("s1 : ", text[e1])
        o1 = [''.join(text[s1: e1 + 1]).lower()]
        # print("o1 : ", o1)
        if '_' not in o1:
            loc_list.extend(o1)
        # print(test_list)

    return test_list


def addrExtractorRemover(query, addrList):
    # if addrList is not None and ',' not in query:
    if addrList is not None:

        repl_char = ""
        query = list(query)
        # print("query :  ",query)
        # print("addrList ",addrList)
        try:
            for idx in addrList:
                # print("idx : ",idx)
                query[idx] = repl_char
        except:
            IndexError
        res = ''.join(query)
        # print(res)
        return res
    else:
        return query


def dateExtractorRemover(query, dateList):
    if dateList is not None:
        # print("in extractor dateList : ",dateList)
        repl_char = ""
        # print("Query :: ",query)
        query = list(query)
        # print("Query 2 :: ",query)
        # print(query)
        # print("strt : ",query[0])
        # print("dateList : ",dateList)
        for idx in dateList:
            query[idx] = repl_char
        res = ''.join(query)
        # print(res)
        return res
    else:
        return query


def remove_stop_word(query):
    # query = query.lower()
    # stop_words = set(stopwords.words('english'))
    # print(stop_words) #removing up from stopwords
    stop_words = {'email','emailid','id','com','whose', 'their', 'was', 'had', 'them', 'any', 'why', 'haven', 'shouldn', 'which', 'all',
                  "that'll", 'him', 'not',
                  'ourselves', 'this', 'am', 'than', 'were', "needn't", 'because', 'here', 'when', 'such', 'his',
                  "she's", 'through',
                  'by', 'very', 'can', 'having', 'have', "you're", 'being', "mustn't", 'or', 'about',
                  "isn't", 'ma',
                  'll', 'if', "mightn't", 'same', 'and', 'weren', 'more', "don't", 'will', "doesn't", 'you',
                  'during',
                  "it's", 'against', 'shan', 'who', 'doing', 'aren', 'does', 'once', 'own', 'yourself', 'itself',
                  'some', 'as',
                  'mightn', 'with', 'but', 'been', "you'll", 'hers', 'theirs', 'both', 'yours', 'he', 'be',
                  'wouldn', 'most',
                  'after', 'the', "haven't", 'too', 'hadn',  'has', "won't", "weren't", 'then', 'hasn',
                  'don', 'we',
                  'it', 'on', 'now', 'off', 'didn', 'myself', 'her', 'won', "hasn't", 'i', "didn't", 'under', 've',
                  'again',
                  'there', "hadn't", 'yourselves', 'each', "aren't", 'other', 'did', 'how', "you've", 'are',
                  "wasn't",
                  "shouldn't", 'that', 'further', 'above', 'me', 'they', 'nor', 'couldn', 'isn', 'just',
                  'what', 'down',
                  'our', 'herself', 'out', 'over', 'its', 'below', 'doesn', 'your', 'between', 'into', 'so', 'do',
                  'wasn', 'before',
                  'is', 're', 'these', "couldn't", 'no', 'few', 'an', 'until', 'while', 'himself', 'she', "wouldn't",
                  'needn',
                  'only', 'my', 'those', "should've", 'ours', 'for', "shan't", 'whom', 'themselves', 'ain',
                  'mustn', 'should', 'equals',
                  "you'd", 'where', 'lives', 'living', 'residential', 'residing', 'permanent', 'native', 'born',
                  'raised', 'name'}
    #                 of ==> removed from stopword ##changed19aug
    # 'location', 'city', 'address', 'place', 'in', 'at', ==> removed from stopword ##changed20aug
    stop_words.update(('age', 'yrs', 'years', 'having', 'as', 'id', 'Id', 'ID', 'no', 'no.', 'number', 'Number',
                       'number.', 'I', 'A', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so', 'cant',
                       'yes', 'No', 'these', 'card',  'pincode', 'pin', 'code', 'code:', 'code-', 'pincode:',
                       'pincode-'))
    word_tokens = word_tokenize(query)
    # word_tokens = re.split(r'[;,\s]\s*', query) ##changed14aug
    word_tokens = list(query.split(" "))
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []

    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    # print(word_tokens)
    # print(filtered_sentence)
    return filtered_sentence


def gadLocnChecker(query):
    sub_strLocation1 = ["gad", "pur", "bad", "nagar"]
    len_sub_strLocation1 = len(sub_strLocation1)
    for i in range(len_sub_strLocation1):
        for val in query:
            if sub_strLocation1[i] in val:
                ans_sub_strLocations = sub_strLocation1[i]
                # print("ans_sub_strLocations : ", ans_sub_strLocations)
                AnsLocationRegex = locationRegex(val, ans_sub_strLocations)  # ==>giving output as a list

                # print("AnsLocationRegex 11 : ", AnsLocationRegex)
                loc_list.extend(AnsLocationRegex)
                # Convert list to string
                AnsLocationRegex = ''.join(AnsLocationRegex)
                # print("AnsLocationRegex 22 : ",AnsLocationRegex)
                if len(AnsLocationRegex) != 0:
                    query.remove(AnsLocationRegex)
                # query = removeFetchedTokens(AnsLocationRegex, query)
        # print("YOOOOO ::: ",loc_list)
    return query


# 'location','city','address','place','in','at','from'
def pincodeChecker(query):
    for val in query:
        # ##changed20aug commented
        # if val not in query[-1]:
        # if val == 'location' or val == 'city' or val == 'address' or val == 'place' or val == 'in' or val == 'at' or val == 'from':
        #     # val == of ##changed17aug
        #     loc_index = query.index(val)
        #     # print("loc_index : ",query[loc_index])
        #     # print("ohk query : ",query)
        #     loc_in_at = query[loc_index + 1]
        #     # print("From in at : ",loc_in_at)
        #     if loc_in_at not in string.punctuation:
        #         loc_list.append(loc_in_at)
        #         regexRemoveList.append(loc_in_at)  ##changed17aug
        #         query.remove(val)
        if isValidPin(val):
            flag = True

    # print("Query in pin : ",query)
    return query


# PAN_no','Aadhar_no','Passport_no','Voter_Card_ID','Email_Id','BankAcDetails','CreditCard
def kyc_attri_manual(query):
    # query.remove(" ")
    print("in kyc attri : ", query)
    for val in query:
        if val not in query[-1]:
            # if val == 'pan':
            #     pan_index = query.index(val)
            #     a = isValidP(query[pan_index + 1])
            #     if a == True:
            #         query.remove(val)
            if val == 'pan':
                if not dropdown_dict['Pn_Check']:  # Pn_Check == False:
                    pan_index = query.index(val)
                    a = isValidP(query[pan_index + 1])
                    if a == True:
                        # print("Remove")
                        query.remove(val)
                elif dropdown_dict['Pn_Check']:  # Pn_Check == True:
                    query.remove(val)
            ##Bank account no
            elif val == 'BankAcDetails':
                credit_index = query.index(val)
                a = fields['BankAcDetails'] = query[credit_index + 1]
                if a == True:
                    # print("Remove")
                    query.remove(val)
            elif val == 'passport':
                passport_index = query.index(val)
                # fields['Passport_no'] = query[passport_index + 1]
                a = isValidPass(query[passport_index + 1])
                if a == True:
                    # print("Remove")
                    query.remove(val)
            elif val == 'mobile' or val == 'cell' or val == 'phone':
                mobile_index = query.index(val)
                # fields['Mobile_No'] = query[mobile_index + 1]
                a = isValidM(query[mobile_index + 1])
                if a == True:
                    # print("Remove")
                    query.remove(val)
            elif val == 'voter' or val == 'voterid':
                voter_index = query.index(val)
                # fields['Voter_id'] = query[voter_index + 1]
                a = isValidV(query[voter_index + 1])
                if a == True:
                    # print("Remove")
                    query.remove(val)
            elif val == 'credit' or val == 'creditcard':
                credit_index = query.index(val)
                a = isValidCCNo(query[credit_index + 1])
                if a == True:
                    # print("Remove")
                    query.remove(val)
            elif val == 'aadhar' or val == 'adhar':
                if not dropdown_dict['AN_Check']:
                    # if not AN_Check:  # AN_Check == False: without dict
                    aadhar_index = query.index(val)
                    a = isValidA(query[aadhar_index + 1])
                    if a == True:
                        # print("Remove")
                        query.remove(val)
                # elif AN_Check:  # AN_Check == True: without dict
                elif dropdown_dict['AN_Check']:
                    query.remove(val)

            # elif val == 'pincode' or val == '-':
            #     pin_index = query.index(val)
            #     a= isValidPin(query[pin_index + 1])
            #     if a== True:
            #         #print("Remove")
            #         query.remove(val)

            elif val == 'mid':
                mid_index = query.index(val)
                isValidMid(query[mid_index + 1])
                if 'ageOther' in fields:
                    query.remove(val)

            elif val == 'to':
                if 'ageOther' not in fields and val not in query[-1]:
                    # print("in to loop")
                    to_index = query.index(val)
                    t_1 = (query[to_index + 1])
                    t_2 = (query[to_index - 1])
                    age_returned = isValidTo(t_1, t_2)

                    if len(age_returned) == 2:
                        regexRemoveList.append(t_1)
                        regexRemoveList.append(t_2)
                        query.remove(val)

            elif val == 'between':
                if 'ageOther' not in fields and val not in query[-2]:
                    between_index = query.index(val)
                    b_1 = (query[between_index + 1])
                    b_2 = (query[between_index + 2])
                    age_returned = isValidBetween(b_1, b_2)

                    if len(age_returned) == 2:
                        regexRemoveList.append(b_1)
                        regexRemoveList.append(b_2)
                        query.remove(val)

            elif val == 'likes' or val == 'like':
                if 'Name' not in fields and 'likeName' not in fields and not dropdown_dict['Name_Check']:
                    # print("In like :: ")
                    likes_index = query.index(val)
                    ans_like = (query[likes_index + 1])
                    if ans_like.isalpha() or checkName(ans_like) is True:
                        fields['likeName'] = ans_like
                        regexRemoveList.append(ans_like)
                        query.remove(val)


            elif val == 'approx' or val == 'approx.' or val == 'approximately' or val == 'approximately.':
                if 'ageOther' not in fields and val not in query[-1]:
                    approx_index = query.index(val)
                    print("zxcvbnm",approx_index)
                    a_1 = (query[approx_index + 1])
                    if a_1.isdigit():
                        i_a_1 = int(a_1)
                        birthYear1 = calculateyearOfBirth(i_a_1 - 5)
                        birthYear2 = calculateyearOfBirth(i_a_1 + 5)
                        age_approx.append(str(birthYear1))  ##changed18aug
                        age_approx.append(str(birthYear2))  ##changed18aug
                        print("dfghjk",age_approx)
                        fields['ageOther'] = age_approx
                        if len(age_approx) == 2:
                            regexRemoveList.append(a_1)

                            query.remove(val)
                            print("heeeeeeeeeeeeeeee", val, query)


            # elif val == 'location' or val == 'city' or val == 'address' or val == 'place' or val == 'in' or val == 'at':
            #     loc_index = query.index(val)
            #     loc_in_at = query[loc_index + 1]
            #     print("From in at : ",loc_in_at)
            #     loc_list.append(loc_in_at)
            #     regexRemoveList.append(loc_in_at)
            #     query.remove(val)

            elif val == 'surname':
                sur_index = query.index(val)
                sur_add = query[sur_index + 1]
                fields['Surname'] = sur_add
                regexRemoveList.append(sur_add)
                query.remove(val)

            elif val == 'over' or val == 'greater' or val == 'more' or val == 'above' or val == '>':
                age_over = query.index(val)
                age_check = query[age_over + 1]
                chk = 1
                a = isValidAgeOver(age_check, chk)
                if a:
                    query.remove(val)

            elif val == 'below' or val == 'lesser' or val == 'lower' or val == 'less' or val == '<':
                # print("In query ::: ", query)
                age_below = query.index(val)
                age_check = query[age_below + 1]
                chk = 2
                a = isValidAgeOver(age_check, chk)
                if a:
                    query.remove(val)
    return query


# Validation check for KYC and other arttributes:--------------------------------------


def isValidPinCode(pin):
    PatternPinCode = re.compile("^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$")
    return PatternPinCode.match(pin)


def isValidPin(element):
    if isValidPinCode(element):
        # pinNo.append(element)
        # fields['Pin_Code'] = element
        loc_list.append(element)
        # print("loc_list : ",loc_list)
        # fields['Home_Address'] = loc_list  ######added
        # addrExtractor(element)
        # print(fields)
        regexRemoveList.append(element)
        return True


def isValidMobileNo(mob):
    PatternMobileNo = re.compile("(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}$")
    return PatternMobileNo.match(mob)


def isValidM(element):
    if isValidMobileNo(element):
        # ##changed20aug normalizing +91 mobile no into normal
        # # 918080808080 , 91-8080808080 , +91-8080808080 , +918080808080 , 9090909090
        if '+91-' or '+91' or '91-' in element:
            element1 = element.replace("+91-", "").replace("+91", "").replace("91-", "")
            mobile.append(element1)

        else:
            mobile.append(element)  ##changed20aug commented

        fields['Mobile_No'] = mobile
        regexRemoveList.append(element)
        return True


def isValidPanNo(pan):
    PatternPanNo = re.compile("^([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}?$")
    return PatternPanNo.match(pan)


def isValidP(element):
    if isValidPanNo(element):
        fields['PAN_no'] = element
        regexRemoveList.append(element)
        return True


def isValidAadharNo(aadhar):
    PatternAadharNo = re.compile("^\d{4}_\d{4}_\d{4}|^\d{4}-\d{4}-\d{4}|^\d{12}$")  # with _-nothing
    return PatternAadharNo.match(aadhar)


def isValidA(element):
    element = element.upper()
    if isValidAadharNo(element):
        fields['Aadhar_no'] = element
        regexRemoveList.append(element)
        return True


def isValidPassportNo(passport):
    PatternPassportNo = re.compile("^[a-zA-Z]{1}-[0-9]{7}$|^[a-zA-Z]{1}[0-9]{7}$")  # with dashes
    return PatternPassportNo.match(passport)


def isValidPass(element):
    if isValidPassportNo(element):
        fields['Passport_no'] = element
        regexRemoveList.append(element)
        return True


def isValidEmailId(email):
    PatternEmailId = re.compile(
        "[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?")
    return PatternEmailId.match(email)


def isValidEmail(element):
    if isValidEmailId(element):
        email.append(element)
        fields['Email_Id'] = email
        regexRemoveList.append(element)
        return True


def isValidVoterId(voter):
    PatternVoterId = re.compile("^([a-zA-Z]){3}([0-9]){7}?$")
    return PatternVoterId.match(voter)


def isValidV(element):
    if isValidVoterId(element):
        fields['Voter_Card_ID'] = element
        regexRemoveList.append(element)
        return True


def isValidCreditCardNo(element):
    # (?:[0-9]{4}-){3}[0-9]{4}|[0-9]{16}

    PatterCreditCardNo = re.compile(
        "^ (?:4[0-9]{12}(?:[0-9]{3})?| (?:5[1-5][0-9]{2} | 222[1-9] | 22[3-9][0-9] | 2[3-6][0-9]{2} | 27[01][0-9] | 2720)[0 - 9]{12}| 3[47][0 - 9]{13}| 3(?:0[0 - 5] | [68][0 - 9])[0 - 9]{11} | 6(?:011 | 5[0 - 9]{2})[0 - 9]{12} | (?:2131 | 1800 | 35\d{3})\d{11})$")
    # PatterCreditCardNo = re.compile("^(?:\d{4}-?){3}d{4}$")
    return PatterCreditCardNo.match(element)


def isValidCCNo(element):
    if isValidCreditCardNo(element):
        fields['BankAcDetails'] = element
        regexRemoveList.append(element)
        # print(fields)
        return True


def isValidDrivingLicense(element):
    StringregexDL = re.compile(
        "^(([A-Z]{2}[0-9]{2})" + "( )|([A-Z]{2}-[0-9]" + "{2}))((19|20)[0-9]" + "[0-9])[0-9]{7}$")
    return StringregexDL.match(element)


def isValidDL(element):
    if isValidDrivingLicense(element):
        fields['DL'] = element
        regexRemoveList.append(element)
        return True


def isValidDate(element):
    stringRegexDate = re.compile(
        "^((0?[13578]|10|12)(-|\/)(([1-9])|(0[1-9])|([12])([0-9]?)|(3[01]?))(-|\/)((19)([2-9])(\d{1})|(20)([01])(\d{1})|([8901])(\d{1}))|(0?[2469]|11)(-|\/)(([1-9])|(0[1-9])|([12])([0-9]?)|(3[0]?))(-|\/)((19)([2-9])(\d{1})|(20)([01])(\d{1})|([8901])(\d{1})))$"
    )
    return stringRegexDate.match(element)


def isValidDOB(element):
    if isValidDate(element):
        dateVal2 = element.replace("/", "-")
        # datetime_str = datetime.datetime.strptime(dateVal2, '%d-%m-%Y') ##changed18aug
        datetime_str = datetime.datetime.strptime(dateVal2, '%d-%m-%Y').strftime('%Y-%m-%d')
        # print("datetime_str : ",datetime_str)
        # fields['Date_of_Birth'] = datetime_str.date()  ##changed18aug
        fields['Date_of_Birth'] = datetime_str
        regexRemoveList.append(element)
        return True


def gender(element):
    element1 = element.lower()
    if element1 == 'male' or element1 == 'boy' or element1 == 'man':
        genderList.append('male')
        fields['Gender'] = genderList
        # fields['Gender'] = 'Male'
        regexRemoveList.append(element)
        return True
    elif element1 == 'female' or element1 == 'girl' or element1 == 'woman' or element1 == 'women' or element1 == 'lady':
        genderList.append('female')
        fields['Gender'] = genderList
        # fields['Gender'] = 'Female'
        regexRemoveList.append(element)
        return True
    elif element1 == 'person' or element1 == 'people':
        genderList.append('female')
        genderList.append('male')
        regexRemoveList.append(element)
        return True


def genderNormalizer(element):
    element1 = element.lower()
    if element1 == 'male' or element1 == 'boy' or element1 == 'man':
        person = 'male'
    elif element1 == 'female' or element1 == 'girl' or element1 == 'woman' or element1 == 'women' or element1 == 'lady':
        person = 'female'
    return person


def nationality(element):
    element1 = element.title()
    if element1 in Nationality:
        nation_list.append(element1)
        fields['Nationality'] = nation_list
        regexRemoveList.append(element)
        return True
    else:
        return False


# for finding bloodgroup:
def bloodgroup(element):
    element1 = element.lower()
    Blood_Group = ['o+', 'o-', 'a+', 'a-', 'b+', 'b-', 'ab+', 'ab-', 'o+ve', 'o-ve', 'a+ve', 'a-ve', 'b+ve', 'b-ve',
                   'ab+ve', 'ab-ve']
    # Blood_Group = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-',
    #                'O+VE', 'O-VE', 'A+VE', 'A-VE', 'B+VE', 'B-VE', 'AB+VE', 'AB-VE']
    if element1 in Blood_Group:
        element2 = element1.replace('ve', '')
        bloodgroupList.append(element2)
        # fields['Blood_Group'] = element2
        fields['Blood_Group'] = bloodgroupList
        regexRemoveList.append(element)
        return True
    else:
        return False


def bloodgroupNormalizer(element):
    print("ele ::: ", element)
    element1 = element.lower()
    Blood_Group = ['o+', 'o-', 'a+', 'a-', 'b+', 'b-', 'ab+', 'ab-', 'o+ve', 'o-ve', 'a+ve', 'a-ve', 'b+ve', 'b-ve',
                   'ab+ve', 'ab-ve']
    if element1 in Blood_Group:
        element2 = element1.replace('ve', '')
        return element2
    # else:
    #     return element


def calculateyearOfBirth(age):
    today = date.today()
    yr = today.year
    birthYear = yr - age
    # print(f"Having YearOfBirth:{birthYear}")

    # for admin range entry:
    # rangeLimit = int(input("Enter the number of years of above and below age limit "))
    # from_year = birthYear - rangeLimit
    # to_year = birthYear + rangeLimit
    # print(f"Having YearOfBirth:{birthYear} of {age} yrs in range: [ {from_year} - {to_year} ]")
    return birthYear


def isValidAge(ageNo):
    patternAge = re.compile('^[0-9]{1}$|^[0-9]{2}$')
    return patternAge.match(ageNo)


# ^[0-1]{1}-[0-2]{1}-[0-9]{1}$|^[0-9]{2}$
def age(element):
    if 'Date_of_Birth' not in fields:
        if isValidAge(element):
            # print("After isValidAge ::: ",element)
            # ageList.append(element)
            # fields['Age'] = ageList
            birthYear = calculateyearOfBirth(int(element))
            # print("birth year  : ",birthYear)
            # ageList_normal.append(str(birthYear - 1))
            ageList_normal.append(str(birthYear))  ##changed18aug


            fields["year_of_Birth"] = ageList_normal
            # fields["year_of_Birth"] = ageList_normal

            regexRemoveList.append(element)
            # Convert string '22' into into 22
            return True
        else:
            return False

def age_checker(query):
    for val in query:
        if val not in query[-1]:
            if val == 'age':
                age_index = query.index(val)
                a= age(query[age_index + 1])
                # a = isValidAge(query[age_index + 1])
                if a == True:
                    # print("Remove")
                    query.remove(val)
    return query

def isValidAgeOver(element, chk):
    if 'Date_of_Birth' not in fields:
        if isValidAge(element):
            if chk == 1:
                birthYear = calculateyearOfBirth(int(element))
                ageList_over.append(str(birthYear))  ##changed18aug
                print("In ageList Over :: ", ageList)
                fields['AgeOver'] = ageList_over
                regexRemoveList.append(element)
                return True
            elif chk == 2:
                birthYear = calculateyearOfBirth(int(element))
                ageList_below.append(str(birthYear))  ##changed18aug
                print("In ageList Below :: ", ageList)
                fields['AgeBelow'] = ageList_below
                regexRemoveList.append(element)
                return True
        else:
            return False


def isUnidentified(query):  # Adding only first name into 'Name' fields
    nlist = []
    dlist = []
    elist = []
    Ulist = []
    for element in query:
        if len(element) != 0:
            if element.isdigit():
                dlist.append(element)
            elif element.isalpha() or checkName(element) is True:
                nlist.append(element)
            else:
                elist.append(element)  # elist=extralist
    if len(nlist) != 0:
        # print("nlist : ",nlist)
        fields['Name'] = nlist[0]  # adding fst locn

    Ulist = nlist + elist + dlist
    if len(Ulist) != 0:
        fields['Unidentified'] = Ulist
        unidentifiedDict['Unidentified'] = Ulist


# ------------------------------------------------------------------------------------
# Extracting various Tokens:-
def data_received(data):
    # print("data 1 : ",data)
    # queryList = data.split(' ')
    # queryList=re.split(r'[;,\s]\s*', data)
    queryList = data
    for element in queryList:
        flag = False
        # if not dropdown_dict['MN_Check']:  # MN_Check == False
        if isValidM(element):
            flag = True
        elif isValidPass(element):
            flag = True
        # elif isValidEmail(element):
        #     flag = True
        elif isValidV(element):
            flag = True
        elif isValidCCNo(element):
            flag = True
        elif gender(element):
            flag = True
        elif nationality(element):
            flag = True
        elif bloodgroup(element):
            flag = True
        elif isValidDL(element):
            flag = True
        elif isValidDOB(element):
            flag = True
        # elif isValidPin(element):
        #     flag = True
        else:
            if not dropdown_dict['Pn_Check']:  # Pn_Check ==False
                if isValidP(element):
                    flag = True
            if not dropdown_dict['AN_Check']:  # AN_Check ==False
                if isValidA(element):
                    flag = True
    return fields


def data_received1(data):  # For age
    queryList = data
    for element in queryList:
        flag = False
        if age(element):
            flag = True
    return fields


###where R === For son of , daughter of , s/o , d/o ==> Mother_Name , Father_Name
def substringCheckerSDinner(sub_str, query):  # Son and Daughter ==> mother / father
    lenStr = len(sub_str)
    subStart_index = query.index(sub_str)
    tB = subStart_index + lenStr  # ending index of substring in query
    tA = subStart_index  # Word Before starting of substring
    nextWord = query[tB + 1:]
    beforeWord = query[: tA - 1]
    firstNextWord = nextWord.rsplit(' ')[0]
    query1 = remove_stop_word(beforeWord)
    firstBeforeWord = query1[-1]
    # assigning  X3 as firstBeforeWord  and Y1 as firstNextWord and R as a relation
    fields['Name'] = firstBeforeWord
    fields['Mother_Name'] = firstNextWord
    fields['Father_Name'] = firstNextWord
    # print("in d/o : ",fields)
    query = removeFetchedTokens(sub_str, query)
    # tokenizing query
    # query = re.split(r'[;,\s]\s*', query) ##changed14aug
    query = list(query.split(" "))
    query.remove(firstBeforeWord)
    query.remove(firstNextWord)
    return query


# remove all occureneces of substrings
def removeFetchedTokens(sub_str, query):
    query = query.replace(sub_str, "")
    return query


###For husband of , wife of , h/o , w/o ==> Spouse_Name
def substringCheckerHWinner(sub_str, query):  # Husband and wife ==> spouse
    lenStr = len(sub_str)
    subStart_index = query.index(sub_str)
    tB = subStart_index + lenStr  # ending index of substring in query
    tA = subStart_index  # Word Before starting of substring
    nextWord = query[tB + 1:]
    beforeWord = query[: tA - 1]
    firstNextWord = nextWord.rsplit(' ')[0]
    query1 = remove_stop_word(beforeWord)
    firstBeforeWord = query1[-1]
    fields['Name'] = firstBeforeWord
    fields['Spouse_Name'] = firstNextWord
    query = removeFetchedTokens(sub_str, query)
    # tokenizing query
    # query = re.split(r'[;,\s]\s*', query) ##changed14aug
    query = list(query.split(" "))
    query.remove(firstBeforeWord)
    query.remove(firstNextWord)
    return query


# mother name is , mother is , father name is , surname is , husband name is ,husband is , wife name is ,  wife is , name is , full name is, fullname is
# NOTE :::: not deleting the substring or value fetched
def substringCheckerNameinner(sub_str, query):
    lenStr = len(sub_str)
    subStart_index = query.index(sub_str)
    tB = subStart_index + lenStr  # ending index of substring in query
    tA = subStart_index  # Word Before starting of substring
    nextWord = query[tB + 1:]
    firstNextWord = nextWord.rsplit(' ')[0]
    return firstNextWord


def substringCheckerLocationinner(sub_str, query):
    lenStr = len(sub_str)
    subStart_index = query.index(sub_str)
    tB = subStart_index + lenStr  # ending index of substring in query
    tA = subStart_index  # Word Before starting of substring
    nextWord = query[tB + 1:]
    firstNextWord = nextWord.rsplit(' ')[0]
    # firstNextWord=firstNextWord.title()
    loc_list.append(firstNextWord)
    # fields['Home_Address'] = loc_list #####added
    return firstNextWord


def locationRegex(s, pat):
    # print("s : ",s)
    pat = r'(\w*%s$)' % pat
    return re.findall(pat, s)


# praj son of raju , praju daughter of jyo , sachin husband of sapna , sapna wife of sachin
# husband name ohk , wife name ooo , spouse name sss , mother name ggg , father name fff
# lmn s/o pqr , xyz d/o def , aaaa h/o bbbb , cccc w/o dddd
# son ss , daughter dd , husband hh , wife ww , spouse  ss , mother mm , father fff

# son name abc , daughter name def ==>> XXXXXq
def tokenStringChecker(query):
    outer_l = ["son", "daughter", "husband", "wife", "spouse", "mother", "father", "s/o", "d/o", "h/o", "w/o"]
    inner_l = ["name", "of"]
    try:
        for index, first in enumerate(query):
            if query[1] != 0:
                second = query[index + 1]
                if first in outer_l and second in inner_l:
                    if second == 'of':
                        pre_index = (index - 1)
                        after = query[index + 2]
                        # print("after    : ",index + 2)
                        if 'likeName' in fields or 'Name' in fields or dropdown_dict[
                            'Name_Check'] is True:  ##changed24aug
                            pass
                        elif 'likeName' not in fields and 'Name' not in fields and not dropdown_dict[
                            'Name_Check']:  ##changed24aug
                            if pre_index == -1:
                                pass
                                # print("discard :: ", pre_index)
                            else:
                                previous = query[index - 1]
                                # print("added ", previous)
                                fields['Name'] = previous
                                token_index.append(index - 1)

                        if first == "son" or first == 'daughter':
                            fields['Mother_Name'] = after
                            fields['Father_Name'] = after
                            token_index.extend((index, index + 1, index + 2))
                            # print("token_index 11 ::: ", token_index)

                        elif first == "husband" or first == 'wife' or first == "spouse":
                            fields['Spouse_Name'] = after
                            token_index.extend((index, index + 1, index + 2))
                            # print("token_index 22 ::: ", token_index)
                        # .regexRemoveList.extend(first,second,previous,after)

                    elif second == 'name':
                        after = query[index + 2]
                        if first == "husband" or first == 'wife' or first == "spouse":
                            fields['Spouse_Name'] = after
                            token_index.extend((index, index + 1, index + 2))
                            # print("token_index 33 ::: ", token_index)
                        elif first == "mother":
                            fields['Mother_Name'] = after
                            token_index.extend((index, index + 1, index + 2))
                            # print("token_index 44 ::: ", token_index)
                        elif first == "father":
                            fields['Father_Name'] = after
                            token_index.extend((index, index + 1, index + 2))
                            # print("token_index 55 ::: ", token_index)

                        # regexRemoveList.extend(first, second, previous, after)
                elif first in outer_l and second not in inner_l:
                    pre_index = (index - 1)
                    after = query[index + 1]
                    # print("fields : ",fields)
                    if first == "s/o" or first == 'd/o':
                        if 'likeName' in fields or 'Name' in fields or dropdown_dict['Name_Check']:  ##changed24aug
                            pass
                        elif 'likeName' not in fields and 'Name' not in fields and not dropdown_dict[
                            'Name_Check']:  ##changed24aug
                            if pre_index == -1:
                                # print("discard :: ", pre_index)
                                pass
                            else:
                                previous = query[index - 1]
                                # print("added ", previous)
                                fields['Name'] = previous
                                token_index.append(index - 1)

                        fields['Mother_Name'] = after
                        fields['Father_Name'] = after
                        token_index.extend((index, index + 1))
                        # print("token_index 55 ::: ", token_index)
                    elif first == "h/o" or first == 'w/o':
                        if 'likeName' in fields or 'Name' in fields or dropdown_dict['Name_Check']:
                            pass
                        elif 'likeName' not in fields and 'Name' not in fields and not dropdown_dict['Name_Check']:
                            if pre_index == -1:
                                # print("discard :: ", pre_index)
                                pass
                            else:
                                previous = query[index - 1]
                                # print("added ", previous)
                                fields['Name'] = previous
                                token_index.append(index - 1)
                        fields['Spouse_Name'] = after
                        token_index.extend((index, index + 1))
                        # print("token_index 55 ::: ", token_index)
                    elif first == "husband" or first == 'wife' or first == "spouse":
                        fields['Spouse_Name'] = after
                        token_index.extend((index, index + 1))
                        # print("token_index 55 ::: ", token_index)
                    elif first == "mother":
                        fields['Mother_Name'] = after
                        token_index.extend((index, index + 1))
                        # print("token_index 55 ::: ", token_index)
                    elif first == "father":
                        fields['Father_Name'] = after
                        token_index.extend((index, index + 1))
                        # print("token_index 55 ::: ", token_index)

    except:
        IndexError, TypeError


def tokenStringCheckerName(query):
    # if 'Name' not in fields or 'likeName' not in fields or not dropdown_dict['Name_Check']:
    if 'Name' not in fields and 'likeName' not in fields and not dropdown_dict['Name_Check']:
        for index, first in enumerate(query):
            try:
                if query[1] != 0:
                    second = query[index + 1]
                    if first == "name":
                        after = query[index + 1]
                        fields['Name'] = after
                        del query[index:index + 2]
            except:
                IndexError

    return query


def tokenStringCheckerDelete(query):
    try:
        indexes = token_index
        # print(token_index)
        for index in sorted(indexes, reverse=True):
            del query[index]
        # print("query token str dlt :  ",query)
        # print("type del q : ",type(query))

    except:
        IndexError
    return query


# name like sheetal , mother name praaj and son of raju

def namePresentChecker(query):
    if 'Name' in fields or 'likeName' in fields or dropdown_dict['Name_Check']:
        if 'name' in query:
            query.remove('name')
    return query
    # if len(query) != 0:
    #     if 'Name' in fields or 'likeName' in fields:
    #         if 'name' in query:
    #             query.remove("name")
    #             print("Query in : ", query)
    #             print("TypeQuery in : ", type(query))
    #             return query
    # else:
    #     if type(query) is None or len(query) == 0:
    #         return query


# mother , father , surname , spouse , name , 1 ,  address
def substringChecker1(query):
    query = query.lower()
    '''
    sub_strSD = ["son of", "daughter of", "s/o", "d/o"]
    len_sub_strSD = len(sub_strSD)
    for i in range(len_sub_strSD):
        if sub_strSD[i] in query:
            lenSubstr_i = len(sub_strSD[i])
            ans_sub_strSD = sub_strSD[i]
            query = substringCheckerSDinner(ans_sub_strSD, query)
            query = queryTypeChecker(query)

    sub_strHW = ["husband of", "wife of", "h/o", "w/o"]
    len_sub_strHW = len(sub_strHW)
    for i in range(len_sub_strHW):
        if sub_strHW[i] in query:
            lenSubstr_i = len(sub_strHW[i])
            ans_sub_strHW = sub_strHW[i]
            query = substringCheckerHWinner(ans_sub_strHW, query)
            query = queryTypeChecker(query)

    sub_strMotherNames = ["mother name", "mother"]
    len_sub_strMotherNames = len(sub_strMotherNames)
    for i in range(len_sub_strMotherNames):
        if sub_strMotherNames[i] in query:
            lenSubstr_i = len(sub_strMotherNames[i])
            ans_sub_strNames = sub_strMotherNames[i]
            name = substringCheckerNameinner(ans_sub_strNames, query)
            fields['Mother_Name'] = name
            query = removeFetchedTokens(ans_sub_strNames, query)
            query = removeFetchedTokens(name, query)

    sub_strFatherNames = ["father name", "father"]
    len_sub_strFatherNames = len(sub_strFatherNames)
    for i in range(len_sub_strFatherNames):
        if sub_strFatherNames[i] in query:
            lenSubstr_i = len(sub_strFatherNames[i])
            ans_sub_strNames = sub_strFatherNames[i]
            name = substringCheckerNameinner(ans_sub_strNames, query)
            fields['Father_Name'] = name
            query = removeFetchedTokens(ans_sub_strNames, query)
            query = removeFetchedTokens(name, query)

    sub_strSpouseNames = ["husband name", "husband", "wife name", "wife", "spouse name", "spouse"]
    len_sub_strSpouseNames = len(sub_strSpouseNames)
    for i in range(len_sub_strSpouseNames):
        if sub_strSpouseNames[i] in query:
            lenSubstr_i = len(sub_strSpouseNames[i])
            ans_sub_strNames = sub_strSpouseNames[i]
            name = substringCheckerNameinner(ans_sub_strNames, query)
            fields['Spouse_Name'] = name
            query = removeFetchedTokens(ans_sub_strNames, query)
            query = removeFetchedTokens(name, query)

    # sub_strSurName = ["surname is", "full name", "fullname", "surname","sirname"]
    # len_sub_strSurName = len(sub_strSurName)
    # for i in range(len_sub_strSurName):
    #     if sub_strSurName[i] in query:
    #         lenSubstr_i = len(sub_strSurName[i])
    #         ans_sub_strNames = sub_strSurName[i]
    #         name = substringCheckerNameinner(ans_sub_strNames, query)
    #         fields['Surname'] = name
    #         query = removeFetchedTokens(ans_sub_strNames, query)
    #         query = removeFetchedTokens(name, query)

    # sub_strLocation = ["lives in", "residing at", "living in", "full address", "native place", "permanent address",
    #                    "residential address", "living in city", "born and raised in"]
    # len_sub_strLocation = len(sub_strLocation)
    # for i in range(len_sub_strLocation):
    #     if sub_strLocation[i] in query:
    #         lenSubstr_i = len(sub_strLocation[i])
    #         ans_sub_strNames = sub_strLocation[i]
    #         name = substringCheckerLocationinner(ans_sub_strNames, query)
    #         query = removeFetchedTokens(ans_sub_strNames, query)
    #         query = removeFetchedTokens(name, query)
    '''

    sub_strLocation1 = ["gad", "pur", "bad", "nagar"]
    len_sub_strLocation1 = len(sub_strLocation1)
    for i in range(len_sub_strLocation1):
        if sub_strLocation1[i] in query:
            lenSubstr_i = len(sub_strLocation1[i])
            ans_sub_strLocations = sub_strLocation1[i]
            # print("ans_sub_strLocations : ",ans_sub_strLocations)
            AnsLocationRegex = locationRegex(query, ans_sub_strLocations)  # ==>giving output as a list
            # fields['Home_Address'] = AnsLocationRegex ######added
            # print("AnsLocationRegex : ",AnsLocationRegex)
            loc_list.extend(AnsLocationRegex)
            # Convert list to string
            AnsLocationRegex = ''.join(AnsLocationRegex)
            query = removeFetchedTokens(AnsLocationRegex, query)

    # sub_strName = ["name is", "name"]
    # if 'likeName' not in fields:
    #     len_sub_strName = len(sub_strName)
    #     for i in range(len_sub_strName):
    #         if sub_strName[i] in query:
    #             ans_sub_strNames = sub_strName[i]
    #             name = substringCheckerNameinner(ans_sub_strNames, query)
    #             fields['Name'] = name
    #             # print(fields)
    #             query = removeFetchedTokens(ans_sub_strNames, query)
    #             query = removeFetchedTokens(name, query)
    return query


substringList = [""]


def queryTypeChecker(query):
    if isinstance(query, list):
        query = ' '.join(query)
    elif isinstance(query, str):
        # print() ###changed14july
        pass
    return query


def queryTypeCheckerStrtoList(query):

    if isinstance(query, list):
        # print() ###changed14july
        pass
    elif isinstance(query, str):
        query =re.sub("\s\s+"," ",query)
        # query = re.split(r'[;,\s]\s*', query)
        query = list(query.split(" "))  ## changed14aug
        # query = re.split(r'" "', query)
    return query


def removeTokensFromQuery(toeknsList, query):
    step1_filtered_sentence = []
    for w in query:
        if w not in toeknsList:
            step1_filtered_sentence.append(w)
    return step1_filtered_sentence


def step4(query):
    isUnidentified(query)  # For first name ele only
    # isUnidentified1(query) #For name string


def isUnidentified1(query):  # adding all alphabates into 'Name' fields
    # print("In isUnidenti query :: ",query)
    nlist = []
    dlist = []
    elist = []
    Ulist = []
    for element in query:
        if len(element) != 0:
            Ulist.append(element)
            if element.isdigit():
                dlist.append(element)
            elif element.isalpha() or checkName(element) is True:
                nlist.append(element)
                # print("nlist : ", nlist)
            else:
                elist.append(element)  # elist=extralist
    # print("nlist111 : ", nlist)
    # nstring = queryTypeChecker(nlist) # convert all remaining ele into str
    # if len(nlist) != 0: ##changed17aug
    #     # fields['Name'] = nstring
    #     fields['Name'] = nlist

    # Ulist = nlist + elist + dlist ##changed14aug
    fields['Unidentified'] = Ulist
    # print("Ulist ",Ulist)
    unidentifiedDict['Unidentified'] = Ulist
    uni_str = ' '.join(Ulist)
    if ',' in query or ';' in query or 'of' in query or 'location' in query or 'city' in query or 'address' in query or 'place' in query or 'in' in query or 'at' in query or 'from' in query or 'addr' in query :
        # name_other and address_other
        # print(", is Present")
        break_list = [',', ';', '.']

        # ans_fst = uni_str.split(',')[0].strip() ##changed19aug
        # ans_second = uni_str.split(',')[1:] ##changed19aug

        # split using ',' ,';' ,'of'
        # ans_fst = re.split(';|,|of', uni_str)[0].strip()  ##changed19aug
        # ans_second = re.split(';|,|of', uni_str)[1:]  ##changed19aug

        # split using ',' ,';' ,'of' ,'location', 'city', 'address', 'place', 'in', 'at', 'from'
        # ';|,|of|location|city|address|place|in|at|from'
        # ';|,|of|from|in|at|location|city|address|place'

        # ans_fst = re.split(';|,|of|from|in|at|location|city|address|place', uni_str)[0].strip()  ##changed19aug
        # ans_second = re.split(';|,|of|from|in|at|location|city|address|place', uni_str)[1:]  ##changed19aug

        ans_main = re.split(r";|,|\bof\b|\bfrom\b|\bin\b|\bat\b|\blocation\b|\bcity\b|\baddress\b|\bplace\b|\baddr\b", uni_str)
        ans_fst = ans_main[0].strip()
        ans_second = ans_main[1:]

        # # \b means word boundaries.
        # trails = (',', ';', 'of', 'location', 'city', 'address', 'place', 'in', 'at', 'from')
        # # regex_fst = r"\b(?:{}).*".format("|".join(trails))
        # regex_fst = r"\b".format("|".join(trails))
        # # res_regex = [r.strip() for r in re.split(regex_fst, uni_str)]
        # res_regex = re.split(regex_fst, uni_str)
        # print("res_regex :: ",res_regex)
        # res_regex_fst = res_regex[0]
        # print("res_regex_fst :: ", res_regex_fst)
        # res_regex_second = res_regex[1:]
        # print("res_regex_second :: ", res_regex_second)

        # print("Fst before ,  :: ", ans_fst) # str of ans_fst
        # fields['Name'] = ans_fst
        # List of ans_fst
        # print("Fst before ,  :: ", ans_fst_list)
        # if 'Name' not in fields or 'likeName' not in fields or dropdown_dict['Name_Check']:
        if 'Name' not in fields and 'likeName' not in fields and not dropdown_dict['Name_Check'] and len(ans_fst)!=0:
            ans_fst_list = queryTypeCheckerStrtoList(ans_fst)
            print("In unidentified name :: ",ans_fst_list)
            fields['Name'] = ans_fst_list

        ans_second_str = queryTypeChecker(ans_second)
        # remove punctuations from string
        ans_second_str_1 = ans_second_str.translate(str.maketrans('', '', string.punctuation))
        # remove extra spaces from string
        ans_second_str_2 = re.sub(' +', ' ', ans_second_str_1).strip()
        # print("Fst after  ,  :: ", ans_second_str_2)

        if len(ans_second_str_2) != 0:
            loc_list.append(ans_second_str_2)
            # print("in unidentified addr : ",loc_list)

    else:
        # if 'Name' not in fields or 'likeName' not in fields or not dropdown_dict['Name_Check'] and len(nlist) != 0:
        if 'Name' not in fields and 'likeName' not in fields and not dropdown_dict['Name_Check'] and len(nlist) != 0:
            fields['Name'] = nlist
            # n_string = queryTypeChecker(nlist) ##changed17aug
            # fields['Name'] = n_string

            # nlist1 = addrExtractorRemover(nlist, addresslist)
            # print(nlist1)
            # nstring1 = queryTypeChecker(nlist1)
            # print("nstring : " ,nstring1)
            # fields['Name'] = nstring1


def complexQueryChecker(sub_str, query):
    query = re.sub(' +', ' ', query)  # Removing extra spaces if any
    lenStr = len(sub_str)
    subStart_index = query.index(sub_str)
    tB = subStart_index + lenStr  # ending index of substring in query
    tA = subStart_index  # Word Before starting of substring
    nextWord = query[tB + 1:]

    firstNextWord = nextWord.rsplit(' ')[0]
    a = int(firstNextWord)
    secondNextWord = nextWord.rsplit(' ')[1]
    b = int(secondNextWord)
    age_range.append(a)
    age_range.append(b)
    fields['Age_Range'] = age_range
    '''
    for i in range(a,b+1):
        age_complex.append(i)
    fields['Age_Complex'] = age_complex
    '''


def betweenQuery(query):
    # we need STRING type of query
    query = queryTypeChecker(query)
    '''
    complex_remove = ("and", "or")
    for i in complex_remove:
        if i in query:
            query = query.replace(i, "")
    '''
    # print("query : ",query)
    tokens = ["between", "likes", "like"]
    len_tokens = len(tokens)
    for i in range(len_tokens):
        if tokens[i] in query:
            ans_complex = tokens[i]
            complexQueryChecker(ans_complex, query)

            query = removeFetchedTokens(ans_complex, query)
            # query = removeFetchedTokens(name, query)


# for converting nos written in alphabates into digits
import word2number
from word2number import w2n


def word_to_dig_demo(element):
    try:
        dig = w2n.word_to_num(element)
        # print(element," : ",dig)
        return dig
    except ValueError:
        # print("Invalid wrd to dig conversion")
        pass
    #


def isValidBetween(ele_1, ele_2):
    if ele_1.isdigit() and ele_2.isdigit():
        ele_1i = calculateyearOfBirth(int(ele_1) + 1)
        ele_2i = calculateyearOfBirth(int(ele_2) - 1)

        age_range.append(str(ele_1i))
        age_range.append(str(ele_2i))
        fields['ageOther'] = age_range
        return age_range
    else:
        return age_range


def isValidTo(ele_1, ele_2):
    if ele_1.isdigit() and ele_2.isdigit():
        ele_1i = calculateyearOfBirth(int(ele_1))
        ele_2i = calculateyearOfBirth(int(ele_2))
        age_to.append(str(ele_2i))
        age_to.append(str(ele_1i))
        # print("age_to : ",age_to)
        fields['ageOther'] = age_to
        return age_to
    else:
        return age_to


def isValidMidChecker(element):
    ans_2 = calculateyearOfBirth(int(element) + 5)
    ans_1 = calculateyearOfBirth(int(element))
    age_mid_list.append(str(ans_1))
    age_mid_list.append(str(ans_2))
    fields['ageOther'] = age_mid_list
    return True


def isValidMid(ageNo):
    # if 'Date_of_Birth' not in fields:
    running = True
    if ageNo.isalpha():  # twenty convert it into 20
        # try:
        dig = word_to_dig_demo(ageNo)
        # dig will have either None(no digit found) or digit(digit found)
        # print("running : ",running)
        if len(str(dig)) != 0 and dig != None:
            returned_1 = isValidMidChecker(dig)
            if returned_1:  # ie. returned_1==True
                regexRemoveList.append(ageNo)  # remove original element


    elif ageNo.isdigit() or ageNo.isalnum():  # 20 or 20's
        ans = re.findall('[0-9]+', ageNo)
        if len(ans) != 0:
            ans_1 = int(ans[0])
            returned_2 = isValidMidChecker(ans_1)
            if returned_2:
                regexRemoveList.append(ageNo)  # remove original element


def replace_punct(query):
    clean = re.sub(r""" 
                   [!'~$"(){}:‘=|] + # Accept one or more copies of punctuation
                   \ *           # plus zero or more copies of a space,
                   """,
                   " ",  # and replace it with a single space
                   query, flags=re.VERBOSE)
    # ; removed from clean ##changed19aug
    # print("Clean :: ",clean)
    return clean


# [!'~$%^&*+(){}.:;<>?,_=|]  #previous & ? present
def remove_special_words(query):
    step1_filtered_sentence = []
    query = re.sub(r'"([^"]*)"', lambda x: x.group().replace(" ", "_"), query)
    query = query.replace("<", " < ").replace(">", " > ").replace(",", " , ").replace(";", " ; ").replace("'s", " ")
    query = query.replace("twenties","20").replace("thirties","30").replace("forties","40").replace("fifties","50").replace("sixties","60").replace("seventies","70").replace("eighties","80").replace("nineties","90")

    # print("Query ::::: ",query)
    query = replace_punct(query)
    step1Remove = (
        'be', 'am', 'pin', 'code', 'code-', 'pincode', 'pincode-', 'and', 'or', 'is', 'are', 'was', 'were', 'been',
        'being', 'can', 'could', 'might', 'will', 'shall',
        'would', 'should', 'must', 'a', 'an', 'the', 'no', 'number', 'card', 'no.', 'id', 'id.',
        'age', 'than', 'nd', 'equals')
    step1_punct = ('!', '"', '$', '%', '&', "'", '(', ')', '*', '+',
                   '.', ':', ';', '=', '”', '“'
                                            '>', '?', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'")
    # !'~$%^&*+()[]{}.:;<>?,_=|
    # print("Beeforeee :: ", query)
    # query = re.split(r'[;,\s]\s*', query) ##changed14aug
    # query1 = query.strip()

    # query = re.split(r'(\W)', query)
    # query = re.split(r'" "', query) ##changed17aug
    query = queryTypeCheckerStrtoList(query)
    # print("Afterrrrr :: ", type(query))
    query = [x.strip(' ') for x in query]
    query = list(filter(None, query))
    # print("Strip :: ", query)
    step1_filtered_sentence = removeTokensFromQuery(step1Remove, query)
    return step1_filtered_sentence


def strQuotesChecker(query):
    # replace space written within double quotes with underscore
    query = re.sub(r'"([^"]*)"', lambda x: x.group().replace(" ", "_"), query)
    # print("In strQuotesChecker :: ", query)
    return query


def strQuotesChecker_reverse(query):
    # replace space written within double quotes with underscore

    query11 = query.replace("_", " ")
    # print("In strQuotesChecker R :: ", query11)
    return query11


def checkName(element):
    if re.match("^[a-z*?][a-z_*?]*$", element):
        return True
    else:
        return False


# in_list = [{'books author': 'bob', 'book title': 'three wolves'},{'books author': 'tim', 'book title': 'three apples'}]

# out_list = [{k.replace(' ', '_') : v for k, v in d.items()} for d in in_list]
# out_list = [{k : v.replace(' ', '_') for k, v in d.items()} for d in in_list]
# print(out_list)
def finalFields(fields):
    # print("in finalFields : ",fields)
    # Name key type changed into list
    key_n = ['Name']
    key_l = ['Mother_Name', 'Father_Name', 'Surname', 'Spouse_Name', 'likeName']
    # key_l = ['Name', 'Mother_Name', 'Father_Name', 'Surname', 'Spouse_Name', 'likeName']
    # out_list = [{k : v.replace('_', ' ') for k, v in d.items()} for d in in_list ]
    key_a = ['Aadhar_no', 'Passport_no']
    for k, v in fields.items():
        if k in key_l:
            ab = v.replace('_', ' ')
            fields[k] = ab
        elif k in key_a:
            if "_" in v:
                cd = v.replace('_', '')
                fields[k] = cd
            elif "-" in v:
                ef = v.replace('-', '')
                fields[k] = ef
        # elif k in key_n:
        #     for i in fields[k]:
        #         print("i :::: ",i)
        #         print("v :::: ", v)
        #         if "_" in v:
        #             # print("i :::: ",)
        #             res = v.replace("_", " ")
        #             fields[k] = res
        #             print("in final fields res : ",res)
        elif k in key_n:
            if type(v) is list:
                temp_lst = []
                for i in fields[k]:
                    # print("i :::: ", i)
                    if "_" in i:
                        res = i.replace("_", " ")
                        # fields[k] = res
                        temp_lst.append(res)
                    elif "_" not in i:
                        temp_lst.append(i)
                fields[k] = temp_lst
                # print("in final fields res not lst : ", fields[k])
            elif type(v) is not list:
                # print("v :::: ",v)
                res = v.replace("_", " ")
                fields[k] = res
                # print("in final fields res not lst : ", res)

    # print("In final fields : ",fields)
    return fields


def notListnormalizer(not_list):
    try:
        Blood_Group = ['o+', 'o-', 'a+', 'a-', 'b+', 'b-', 'ab+', 'ab-', 'o+ve', 'o-ve', 'a+ve', 'a-ve', 'b+ve', 'b-ve',
                       'ab+ve', 'ab-ve']
        for idx, val in enumerate(not_list):
            # element2 = not_list[idx + 1]
            element1 = val.lower()
            if element1 in Blood_Group:
                b1 = element1.replace('ve', '')
                not_list[idx] = b1
            elif element1 == 'male' or element1 == 'boy' or element1 == 'man':
                # m1 = 'male'
                not_list[idx] = 'male'
            elif element1 == 'female' or element1 == 'girl' or element1 == 'woman' or element1 == 'women' or element1 == 'lady':
                # f1 = 'female'
                not_list[idx] = 'female'
            elif element1 == 'uttar':
                element2 = not_list[idx + 1]
                if element2 == 'pradesh':
                    not_list[idx + 1] = ''
                    not_list[idx] = 'uttar pradesh'
                    not_list.append('up')
            elif element1 == 'madhya':
                element2 = not_list[idx + 1]
                if element2 == 'pradesh':
                    not_list[idx + 1] = ''
                    not_list[idx] = 'madhya pradesh'
                    not_list.append('mp')
            elif element1 == 'andhra':
                element2 = not_list[idx + 1]
                if element2 == 'pradesh':
                    not_list[idx + 1] = ''
                    not_list[idx] = 'andhra pradesh'
                    not_list.append('ap')
            elif element1 == 'up' or element1 == 'u.p.':
                # l4 = 'uttar pradesh'
                # not_list[idx] = 'uttar pradesh'
                not_list.append('uttar pradesh')
            elif element1 == 'mp' or element1 == 'm.p.':
                # l5 = 'madhya pradesh'
                # not_list[idx] = 'madhya pradesh'
                not_list.append('madhya pradesh')
            elif element1 == 'ap':
                # l6 = 'andhra pradesh'
                # not_list[idx] = 'andhra pradesh'
                not_list.append('andhra pradesh')
    except:
        IndexError

    # if 'pradesh' in not_list:
    #     not_list.remove('pradesh')
    not_list = list(set(not_list))
    return not_list


def notListChecker(query):
    if len(query) > 1:
        for i in range(len(query)):
            # print("i : ", i)
            if query[i] == 'not' and query[i] not in query[-1]:
                if query[i + 1] == 'of' or query[i + 1] == 'from':
                    if query[i + 1] not in query[-1]:
                        not_list.append(query[i + 2])

                    if query[i + 2] not in query[-1] and query[i + 3] == 'pradesh':
                        # print("in pradesh of")
                        not_list.append(query[i + 3])

                elif query[i + 1] != 'of' or query[i + 1] != 'from' and query[i + 1] not in query[-1]:
                    not_list.append(query[i + 1])
                    if query[i + 1] not in query[-1] and query[i + 2] == 'pradesh':
                        # print("in pradesh")
                        not_list.append(query[i + 2])
    not_list1 = notListnormalizer(not_list)

    # print("Not list ::: ", not_list1)
    return not_list1


def mpLocnAdd(loc_list):
    if len(loc_list) != 0:
        for val in range(len(loc_list)):
            if 'uttar pradesh' in loc_list and 'up' not in loc_list:
                loc_list.append('up')
            elif 'madhya pradesh' in loc_list and 'mp' not in loc_list:
                loc_list.append('mp')
            elif 'andhra pradesh' in loc_list and 'ap' not in loc_list:
                loc_list.append('ap')
            elif 'uttar pradesh' not in loc_list and 'up' in loc_list:
                loc_list.append('uttar pradesh')
            elif 'madhya pradesh' not in loc_list and 'mp' in loc_list:
                loc_list.append('madhya pradesh')
            elif 'andhra pradesh' not in loc_list and 'ap' in loc_list:
                loc_list.append('andhra pradesh')
            elif "new delhi" in loc_list and "delhi" not in loc_list:
                loc_list.append('delhi')
    return loc_list


def remove_nd(query):
    nd_list = []
    for val in query:
        if val.isalnum():
            abc = date_nd_regex(val)
            nd_list.extend(abc)
    # print("nd_list: ",nd_list)

    for i, val in enumerate(query):
        if val in nd_list:
            # print("val 1 : ",val)
            query[i] = val.replace("nd", "")
            # print("val 2 : ", val)

    # print("In remove_nd q ",query)
    return query


def date_nd_regex(val):
    pat = 'nd'
    pat = r'(\w*%s$)' % pat
    return re.findall(pat, val)


def not_list_undescore_dlt(lst):
    for idx, ele in enumerate(lst):
        if '_' in ele:
            lst[idx] = ele.replace('_', ' ')
            # print(ele)
    # print("Inside : ",lst)
    return lst


def print_query(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15):
    print("p1 : ", p1, "\np2 : ", p2, "p3 : ", p3, "\np4 : ", p4, "p5 : ", p5)
    print("p6 : ", p6, "\np7 : ", p7, "p8 : ", p8, "\np9 : ", p9, "p10 : ", p10)
    print("p11 : ", p11, "\np12 : ", p12, "p13 : ", p13, "\np14 : ", p14, "p15 : ", p15)


def print_fields(q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15):
    print("q1 : ", q1, "\nq2 : ", q2, "q3 : ", q3, "\nq4 : ", q4, "q5 : ", q5)
    print("q6 : ", q6, "\nq7 : ", q7, "q8 : ", q8, "\nq9 : ", q9, "q10 : ", q10)
    print("q11 : ", q11, "\nq12 : ", q12, "q13 : ", q13, "\nq14 : ", q14, "q15 : ", q15)


def dropdown(data,dropdown_dict):
    if data['Name'] != '' and data['Name'] in data["Other"]:
        fields["Name"] = data["Name"]
        dropdown_dict['Name_Check'] = True
        # data["Name"]=""
    if data['Home_Address'] != [] and  [val for val in data['Home_Address'] if val in data["Other"]]:
        fields["Home_Address"] = data["Home_Address"]
        dropdown_dict['HA_Check'] = True
        for val in fields["Home_Address"]:
            data["Other"] = data["Other"].replace(val, '')

        # data["Home_Address"]=""
    if data['PAN_no'] != '' and data['PAN_no'] in data["Other"]:
        fields["PAN_no"] = data["PAN_no"]
        # data["Other"] = data["Other"].replace(fields["PAN_no"], '')
        dropdown_dict['Pn_Check'] = True
        # data["PAN_no"]=""
    if data['Mobile_No'] != [] and [mob for mob in data['Mobile_No']  if mob in data["Other"]] :
         fields["Mobile_No"] = data["Mobile_No"]
        # data["Mobile_No"]=[]
    if data['Aadhar_no'] != '' and data["Aadhar_no"] in data["Other"]:
        fields["Aadhar_no"] = data["Aadhar_no"]
        dropdown_dict['AN_Check'] = True
        # data["Aadhar_no"]=[]
    print("dropdown_dict :: ", dropdown_dict)
    query = data["Other"]
    return fields,query

def MetroCities(loc):
    shouldOtherList=[]
    client = Elasticsearch(
        # Add your cluster configuration here!"sniff":To inspect the cluster state to get a list of nodes upon startup, periodically and/or on failure
        [{'host': 'localhost', 'port': 9200}], maxsize=25, sniff_on_start=True,
        # If your application is long-running consider turning on Sniffing to make sure the client is up to date on the cluster location.
        sniff_on_connection_fail=True,
        sniffer_timeout=60)
    response = client.search(
            index="nearby",
            body={
            "query": {
                "match" : {
                    "Place" : loc
                }
            }
        }
        )
    for hit in response['hits']['hits']:
        latitude=hit['_source']['Lat']
        longitude=hit['_source']['Lon']

    latterm = {"Lat": {
                       "gte": float(latitude)-0.20,
                        "lte": float(latitude)+0.20}}
    shouldOtherList.append({"range": latterm})  # correct final
    lonterm = {"Lon": {
        "gte": float(longitude) - 0.20,
        "lte": float(longitude)+ 0.20}}
    shouldOtherList.append({"range": lonterm})  # correct final
    Dict_nearbyCities = dict()
    if len(shouldOtherList) != 0:
        Dict_nearbyCities.update({"must": shouldOtherList})
    body = {"query": {"bool": Dict_nearbyCities}}
    print("This is the metro cities query:-", body)
    res = client.search(index="nearby", body=body, size=2000)
    for hit in res['hits']['hits']:
        loc_list.append(hit['_source']['Place'])
    fields["Home_Address"]=loc_list
    return fields
def email_checker(query):
    for val in query:
        flag=False
        if isValidEmail(val):
            flag = True
    return fields
def checker(query):
    # print("ddd :: ",type(query))
    global fields,ageList_over,ageList_below, unidentifiedDict, regexRemoveList, addresslist, dateList_fn, nation_list, loc_list, loc_list_set, age_complex, age_range, age_mid_list, token_index, ageList, bloodgroupList, genderList, not_list, age_approx, age_to, ageList_normal, email, mobile, dropdown_dict
    fields = dict()
    unidentifiedDict = dict()
    regexRemoveList = []
    addresslist = []
    dateList_fn = []
    nation_list = []
    loc_list = []
    age_complex = []
    age_range = []
    age_mid_list = []
    loc_list_set = set()
    token_index = []
    ageList = []
    bloodgroupList = []
    genderList = []
    not_list = []
    age_approx = []
    age_to = []
    ageList_normal = []
    email = []
    mobile = []
    ageList_over=[]
    ageList_below=[]

    notDict = dict()

    # global HA_Check, Pn_Check, MN_Check, AN_Check
    # HA_Check = False  # Home_Address
    # Pn_Check = False  # PanNo
    # MN_Check = False  # MobileNo
    # AN_Check = False  # AadharNo

    dropdown_dict = dict()
    dropdown_dict = {'HA_Check': False, 'Pn_Check': False, 'MN_Check': False, 'AN_Check': False, 'Name_Check': False}

    # if data coming from javascript dropdown select:
    data = query

    fields,query=dropdown(data,dropdown_dict)

    print("other",query)

    # fields['Name'] = 'prakash'
    # fields['Aadhar_no'] = '123412341234'  # remove dropdown var from original query
    # fields['PAN_no'] = 'abcde1234f'
    # # fields['Mobile_No'] = ['9090909090']
    # fields['Home_Address'] = ['305 Narayan peth , near Vijay Talkies , Pune - 411030 , Maharashtra']

    # without dictionary
    # if 'Aadhar_no' in fields:
    #     AN_Check = True
    # elif 'PAN_no' in fields:
    #     Pn_Check = True
    # elif 'Mobile_No' in fields:
    #     MN_Check = True
    # elif 'Home_Address' in fields:
    #     HA_Check = True
    # elif 'Name_Check' in fields:
    #     Name_Check =True
    # check not for name and home address , like for name

    # key_check = ['Name', 'Home_Address']
    # not done for Home_Address
    query=query.lower()
    # query=singularize(query)

    print("After dropdown fields ::: ",fields)
    try:
        if 'like' in query or 'likes' in query and 'Name' in fields:
                val = fields['Name']
                fields['likeName'] = val
                del fields['Name']
                subStart_index = query.index(val)
                beforeWord = query[: subStart_index - 1]
                query1 = remove_stop_word(beforeWord)
                firstBeforeWord = query1[-1]
                # if firstBeforeWord == 'like' or firstBeforeWord == 'likes':
                #     fields['likeName'] = val
                #     del fields['Name']
                # print("likeName fields",fields)
    except:
        AttributeError , ValueError

    print("After removing Name : ",fields)
    # key_check = ['Name']
    # for kyc_nm, kyc_val in fields.items():
    #     # print("kyc_val :: ", kyc_val)
    #     if kyc_val in query and kyc_nm in key_check:
    #         len_val = len(kyc_val)
    #         subStart_index = query.index(kyc_val)
    #         tA = subStart_index  # Word Before starting of substring
    #         beforeWord = query[: tA - 1]
    #         query1 = remove_stop_word(beforeWord)
    #         firstBeforeWord = query1[-1]
    #         if firstBeforeWord == 'like' or firstBeforeWord == 'likes':
    #             fields['likeName'] = kyc_val #RuntimeError: dictionary changed size during iteration
    #         # elif firstBeforeWord=='not':
    #         #     # fields['likeName'] = kyc_val
    #         #     notDict[kyc_nm] = kyc_val
    #         print("firstBeforeWord :: ", firstBeforeWord)

    print("Fields from dropdown dict :: ", fields)
    # with dictionary

    # split string and numbers e.g. 42yrs to 42:
    regex = re.compile('yrs|yr|years|YRS|YR|YEARS|“|”')
    query = regex.split(query)
    query = "".join(query).lower()
    # print("0 ::: ", query)
    # Step 1: Extract Kyc Attri
    query = remove_special_words(query)
    query=queryTypeCheckerStrtoList(query)
    #email handling because of .(dot) removal
    email_checker(query)
    query = removeTokensFromQuery(regexRemoveList, query)
    query=queryTypeChecker(query)
    query=query.replace("."," ")
    # query = query.strip()

    query = queryTypeCheckerStrtoList(query)
    # print("1 ::: ", query)
    p1 = query
    q1 = fields

    query = kyc_attri_manual(query)
    query = removeTokensFromQuery(regexRemoveList, query)
    # print("2 ::: ", fields)
    # 'age' keyword
    query = age_checker(query)
    query = removeTokensFromQuery(regexRemoveList, query)
    ## added15July
    # query = query.strip()
    p2 = query
    q2 = fields
    not_list = notListChecker(query)
    # print("not list returned :: ", not_list)
    # print("before stop word", query)
    p3 = query
    q3 = fields
    fields = data_received(query)  # requires List
    query = removeTokensFromQuery(regexRemoveList, query)
    # Convert List Query to String query
    # print("3 ::: ", fields)
    p4 = query
    q4 = fields
    query = queryTypeChecker(query)
    query = query.strip()
    # print("Query before removing : ", query)
    query = query.replace("-", " - ")
    # print("Query after removing : ", query)
    # print("4 ::: ", fields)
    p5 = query
    q5 = fields
    # query = substringChecker1(query)  ##changed 9 julyyy
    # Convert String query to List Query
    query = queryTypeCheckerStrtoList(query)
    # print("5.1 ::: ", query)
    ## added17July
    ## remove 123nd ==> nd from alnum word to extract date
    query = remove_nd(query)
    # print("5.2 ::: ", query)
    query = namePresentChecker(query)
    tokenStringChecker(query)
    query = tokenStringCheckerDelete(query)
    # print("5.3 ::: ", query)
    query = namePresentChecker(query)
    query = tokenStringCheckerName(query)
    # print("6 ::: ", query)
    p6 = query
    q6 = fields
    query = pincodeChecker(query)  # pincode,in,at,place..

    # Convert List Query to String query
    query = queryTypeChecker(query)
    # print("before remove_stop_word  :: ",query )
    query = remove_stop_word(query)  # removing 'between' keyword
    # print("after remove_stop_word  :: ", query)
    # print("regexRemoveList : ",regexRemoveList)
    query = removeTokensFromQuery(regexRemoveList, query)
    # print("after removeTokensFromQuery  :: ", query)
    # print("7 ::: ", query)
    p7 = query
    q7 = fields
    ## For gad , pur , nagar
    query = queryTypeCheckerStrtoList(query)
    query = gadLocnChecker(query)  # gad,pur,bad,nagar
    p8 = query
    q8 = fields
    query = queryTypeCheckerStrtoList(query)
    query = [x.strip(' ') for x in query]
    query = list(filter(None, query))
    # Convert List Query to String query
    query = queryTypeChecker(query)

    # print("query addr : ", query , fields)
    addresslist = addrExtractor(query)
    # print("before addresslist ::: ",query)
    # print("addresslist  :: ",addresslist)
    p9 = query
    q9 = fields
    query = addrExtractorRemover(query, addresslist)  ##changed17aug

    # print("zero.0 ::: ", query ,fields)
    dateList_fn = dateExtractor(query)  #### For birthdate
    # print("before remover dateList : ", dateList_fn)
    query = dateExtractorRemover(query, dateList_fn)
    # print("zero ::: ", query)
    p10 = query
    q10 = fields
    query = queryTypeCheckerStrtoList(query)
    # print("one ::: ", query)
    fields = data_received1(query)  ### For only Age Calculations
    query = removeTokensFromQuery(regexRemoveList, query)
    # print("after removeTokensFromQuery111 :: ",query)
    # print("7 ::: ", fields)
    # Convert List Query to String query
    query = queryTypeChecker(query)
    # print("two ::: ", query)
    ######
    query = queryTypeCheckerStrtoList(query)
    # print("three : ", query)
    p11 = query
    q11 = fields
    # ##changed24aug
    # if 'Name' not in fields and 'likeName' not in fields: ##changed24aug
    # isUnidentified1(query) ##changed24aug
    isUnidentified1(query)  ##changed24aug added
    loc_list = mpLocnAdd(loc_list)
    p12 = query
    q12 = fields
    # print("up mp : ",loc_list)
    # if not HA_Check: #HA_Check ==False
    if not dropdown_dict['HA_Check']:
        if len(loc_list) != 0:
            # remove duplicate elements from loc_list
            loc_list = list(set(loc_list))
            # loc_list=[value for value in loc_list if value != 'pincode'] #to remove cod,-,: from going to home_address
            fields['Home_Address'] = loc_list
    # print("8 ::: ", fields)
    p13 = query
    q13 = fields
    fields = finalFields(fields)
    if "AgeBelow" in fields and "AgeOver" in fields:
        print()
        fields["ageOther"]=ageList_below+ageList_over
        del fields["AgeBelow"],fields["AgeOver"]
    # print("=======================================================")
    # print("Identified Dictionary : ", fields)
    # print('NOT TYPE HANDLE+++++++++++++++++++++++++++++++++++++++++++++++++++')

    # remove _ if present  in NOT list
    # print("9 ::: ", fields)
    not_list = not_list_undescore_dlt(not_list)
    # print("not_list before : ",not_list)

    for index, val in enumerate(not_list):
        if val.isdigit():
            converted_year = calculateyearOfBirth(int(val))
            not_list[index] = str(converted_year)

    # print("not_list after : ",not_list)
    # print("not_list after type : ", type(not_list))
    # print("10 ::: ", fields)
    exclude_keys = ['Unidentified']
    # print("1 ::: ", fields)
    new_fields = {k: fields[k] for k in set(list(fields.keys())) - set(exclude_keys)}

    # print("old fields :: ", fields)
    # print("new fields :: ",new_fields)
    # print("not list :: ", not_list)
    for key, value in new_fields.items():
        for ntval in not_list:
            if ntval in value and len(ntval) != 0:
                if key in notDict:
                    notDict[key].append(ntval)
                else:
                    notDict[key] = [ntval]
                try:
                    # print(ntval," : ",type(ntval))
                    new_fields[key].remove(ntval)
                except:
                    AttributeError
        ##After traversing not_list

    if len(notDict) != 0:
        new_fields['notQuery'] = notDict
    # print("Last old fields :: ",fields)
    fields = new_fields

    p14 = query
    q14 = fields
    # print("2 ::: ", fields)
    fields = dict(x for x in fields.items() if all(x))
    # print("12 ::: ",fields)
    # if len(not_list)>0:
    list_dlt = ['Name', 'Gender']
    for k, v in fields.items():
        if k in list_dlt and type(v) is list:
            if k is 'Name':
                # print("fields[k][0] : ",fields[k][0])
                # print("fields.items() :: ",fields.items() , type(fields.items()))
                # print(' '.join(fields['Name']))
                fields['Name'] = ' '.join(fields['Name'])
            else:
                fields[k] = fields[k][0]
    # print("3 ::: ", fields)
    # fields['Name'] = fields['Name'][0]
    if "ageOther" in fields:
        fields["ageOther"].sort(reverse=True)
    p15 = query
    q15 = fields
    # print("Fields :::: ",fields)
    # Remove duplicates if present in any key's value
    # fields = {a: list(set(b)) for a, b in fields.items()}
    # print_query(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15)
    # print_fields(q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15)
    print("Identified with NOT and Unidentified Dictionary : ", fields)
    print("Unidentified Dictionary : ", unidentifiedDict)
    # try:
    #     del fields["Unidentified"]
    # except KeyError:
    #     print("Key 'Unidentified' not found")
    # if "Home_Address" in fields.keys():
    #     for loc in fields["Home_Address"]:
    #         if loc=="mumbai" or loc=="pune" or loc=="delhi" or loc=="kolkata" or loc=="hyderabad":
    #             fields=MetroCities(loc)

        # print("The metro cities added dictionary",fields)
    return fields

"""
ans = 'y'
# =================((((( 1)))
while choice != 2:
    print("1. Query Tokenizer")
    print("2. Exit")
    choice = int(input("Enter Your Choice : "))
    if choice == 1:
        query = input("Enter your query : ")
        checker(query)
    elif choice == 2:
        sys.exit()
        """

##From passport data
# surname Yadav , name  Ramcharan , Father name  Gopaldas Yadav , Mother Name Sundari Devi Yadav,
# spouse name Meenakshi Yadav , 21-Nov-78 ,Male	AB+	, Gaziyabad - 110093 Uttar Pradesh
# Pan no ABCDE1234F	, adhar no 123456789101 ,pasport J1234567
# "Ramcharan Yadav" h/o "Meenakshi Yadav",Gaziyabad-up,age between 40 and 45
# 1))
# Ramcharan , J1234567 , ABCDE1234F , 21-11-78 , Male	AB+ , Gaziyabad - 110093 Uttar Pradesh
# Identified Dictionary :  {'Passport_no': 'j1234567', 'PAN_no': 'abcde1234f', 'Gender': 'Male', 'Blood_Group': 'AB+', 'Date_of_Birth': '1978-11-21', 'Name': 'ramcharan', 'Unidentified': ['ramcharan'], 'Home_Address': ['uttar pradesh', 'gaziyabad', '110093']}
# Unidentified Dictionary :  {'Unidentified': ['ramcharan']}

# 2))
# Ramcharan son of Gopaldas, 123456789101 , 110093 , 21 nov 78 , J1234567
# Identified Dictionary :  {'Aadhar_no': '123456789101', 'Passport_no': 'J1234567', 'Name': 'ramcharan',
# 'Mother_Name': 'gopaldas', 'Father_Name': 'gopaldas', 'Date_of_Birth': '1978-11-21', 'Unidentified': [],
# 'Home_Address': ['110093']}

# 3))
# Ramcharan son of Gopaldas,123456789101,110093,21 nov 78,J1234567
# Identified Dictionary :  {'Aadhar_no': '123456789101', 'Passport_no': 'J1234567', 'Name': 'ramcharan',
# 'Mother_Name': 'gopaldas', 'Father_Name': 'gopaldas', 'Date_of_Birth': '1978-11-21', 'Unidentified': [],
# 'Home_Address': ['110093']}

# 4))
# surname Yadav , name  Ramcharan , Father name  Gopaldas Yadav , Mother Name Sundari Devi Yadav,spouse name Meenakshi Yadav , 21-Nov-78 ,Male	AB+
# , Gaziyabad - 110093 Uttar Pradesh Pan no ABCDE1234F	, adhar no 123456789101 ,passport J1234567
# Identified Dictionary :  {'PAN_no': 'abcde1234f', 'Aadhar_no': '123456789101', 'Passport_no': 'j1234567', 'Gender': 'Male', 'Blood_Group': 'AB+',
# 'Mother_Name': 'sundari', 'Father_Name': 'gopaldas', 'Spouse_Name': 'meenakshi', 'Surname': 'yadav',


# Surname Garade	, Name Sheetal , Father name Sudhri Garade, Mother name Sumati Garade, Spouse name Vishal More
# bdate 10-Apr-81,Female, B+ , Pune - 411005 Maharashtra  , Pan no ACEGI14321K , aadhar 101998754321
# passport J7654321	, 9810000000 , sheetal@gmail.com, Indian

# +++++++++++++++++++++++++++++
# Jadhav Bhushan , Father is Gangadhar Jadhav , mother name Subhadra Jadhav , wife is Ashwini Jadhav
# 20-Dec-76	, Male ,AB+	,177 Rajas Society, Katraj, Pune - 411046 Maharashtra,
# Pan AEMPJ5584L ,mobile 937257034246, Passport A1234567 ,9850068581 , bhushanj@cdac.in , Indian
# ================================================================
# name is praj and mother is jyoti,123412341234,father name raju
# name is "Prajakta Memane" and mother is "Jyoti Memane",123412341234,father name "raju memane"
# name like praj , praj w/o sann
# ================================================================
# Query +++++++++++++++++++++++++>>>>>>>>>>>>>>>>>>>>>>>>>

# Jadhav Bhushan,20-Dec-76,Male,Pune-411046,b-

# Sheetal w/o vishal,Pune,Maharashtra,B-,10-04-1981
# Sheetal w/o vishal,living in Pune-Maharashtra,B-,10-04-1981
# Sheetal Garade living in Pune,J7654321, 10/04/1981


# Ramcharan son of Gopaldas,123456789101,110093,21 nov 78,J1234567
# Ramcharan,J1234567,ABCDE1234F,21-11-78,Male AB+,Gaziyabad - 110093 ,Uttar Pradesh
# Ramcharan,J1234567,ABCDE1234F,21-11-78,Male AB+,Gaziyabad-110093,Uttar Pradesh
# name like Sheetal,Pune,between 35 and 40
# Ramcharan,Male,mid 40's
# Ramcharan,123456789101,Indian,mid forty,living in Gaziyabad-uttar pradesh
# Ramcharan,1234-5678-9101,Indian,mid forty,living in Gaziyabad-110093-up
# Bhushan,mid forty,Pune - 411046,AEMPJ5584L,Indian


# "Bhushan Jadhav",mid forty,Pune - 411046,AEMPJ5584L,Indian
# "Jadhav Bhushan",mother "Subhadra Jadhav",1976-12-20,poona,AEMPJ5584L
# "Jadhav Bhushan" son of "Gangadhar Jadhav",1976 dec 20,poona,AEMPJ5584L
# name like "Bhushan",poona
# "Ramcharan Yadav" h/o "Meenakshi Yadav",Gaziyabad-up,age between 40 and 45
# Sheetal,d/o Sudhri,411005,10 apr '81,adhar 101998754321
# "Sheetal Garade",d/o Sudhri,411005,10 apr '81, "1019 9875 4321",poona

# wrong adhar card ==> correct is 1091-1011-1112
# "Iqbal Anis R Mistry",s/o Raziya,living in Meerut-250001-UttarPradesh,109110111112
# name like "Iqbal Mistry" h/o Riyaa, Meerut-250001-up,"1091 1011 1112"
# "Aditya Hora",250001,5567-6644-2233,21st dec 1976

# son of saddam husain
# age over 50 , more than 50 , greater than 50 ,above 50 ==> ageOver
# age below , less than ,lesser ==> ageBelow

#################Not Query
# --- Any 1 ---
# Ram of up not from mp
# Ram of B+ve but not O+
# ram of 43 but not 40
# ram of age between 40 and 45 , not 42
# Ram of age between 40 and 45 but not of 42
# ram not of 33 but from mid 30's
# ram of male,not female
# ram,not female

# --- Any 2 ---
# Ram from up male ,not female
# Ram from up but not female
# Ram over 40 but not 30
# Ram from up of age 43 but not 40
# Ram of age mid 30 but not from mp
# Ram between 40 and 45 ,not from Gaziayabad but from mp
# Ram of mp,up but not B+
# Ram of mp , up , O+ ,not B+
# Ram female,not male , not of B+
# Ram between 30 and 34 but not A-ve ==> incorrect

### not_list :  ['a-ve']
# Ram male but not female of age between 38 and 42
# --- Any 3 ---
# Ram not of B+ , from mp,up of mid 40's
# Ram of A- mid 30's but not Female
# Ram of A- mid 30's but not male
# Ram of B+ mid 30's but not Male
# Ram of B+ mid 30's but not Female
# Ram from jodhpur mp but not from uttar pradesh , B+ not A-, Male
# Ram from jodhpur mp but not from up, B+ not A-, Male
# Ram from jodhpur mp but  not from up, B+ not A-, female
# Ram from up mp not Jodhpur , 42 but not 40 , Male not Female
# Ram from up mp not Jodhpur , Age between 30 and 45 not 40 , Male not Female
# Ram from up mp not Jodhpur , Age between 30 and 45 not 40 but not Female
# --- Any 4 --- (blood group remaining)
# Ram of up but not Kanpur , 42 not 43 , male
# Ram of up but not Kanpur , mid 40's not 43 , male
# Ram of up but not Kanpur , mid 40's not 43 , female
# Ram of age over 40 but not from Hyderabad
# All ram below 40 not female
# ram is not man but not b-ve but not from uttar pradesh
# ram not from uttar pradesh and not madhya pradesh
# ram not from uttar pradesh
# ram not from up not mp ====> wrong
# 22 nd mar 1998
# 2 nd july 1995
# 22nd mar 1998
# 2nd july 1995

### u.p. wrong !!!!
# ram not from u.p. poona ====> wrong

# Identified Dictionary :  {'Name': 'ram', 'Unidentified': ['ram', 'o'], 'Home_Address': ['pune', 'u.p. po', 'uttar pradesh', 'na', 'up']}
# Identified NOT Dictionary :  {'Name': 'ram', 'Unidentified': ['ram', 'o'], 'Home_Address': ['pune', 'u.p. po', 'uttar pradesh', 'na', 'up']}
# Unidentified Dictionary :  {'Unidentified': ['ram', 'o']}
# ram not from poona u.p. ====> correct
# ram not from u.p. not mp ====> wrong

# ram but not sita, up not from up
# "Ramdugle Sita" from uttar pradesh and not madhya pradesh
# "Ramdugle Sita" not "Ramdugle Seeta" from uttar pradesh and not madhya pradesh

# ram of mid 40's
# ram of mid 40's not 42
# ram of age between 40 and 45
# ram of age between 40 and 45 not 42
# ram over 40 but not 42  ==> wrong
# ram below 40 not 35 not female  not mumbai
#
# ram of b+ ==> wrong but a- and o+ done
# 21 Nov 78
# 21 Nov. 78
# 21 Nov '78
# boy ram of age 42
# ram of hyderabad
# ram of hyderabad not mumbai
# ram of hyderabad not up ==>wrong not up prblm karra
# ram of gaziyabad
# ram of gaziyabad not up
# ram of up
# ram of hyderabad


# ram from gaziyabad in mid 40's
# Ramcharan Y. from gaziyabad in mid 40's
# Y. Ramcharan from gaziyabad in mid forty

# ram , ABCDE1234F
# ram,uttar pradesh
# ram,42,up
# ram of mid 40's
# ram of mid 40's , not 42
# ram of between 40 and 45 , not 42
# ram of over 40 , not 42
# ram of below 40 , not 42
# ram of below 40 , not 42 , male
# ram of below 40 , not 42 , male , not female
# ram of below 40 , not 42 , not female
# ram of below 40 , not 42 , not female , not o+
# ram of below 40 , not 42 , not female , not o+ , not from hyderabad
# ramcharan yadav of below 40 , not 42 , not female , not o+ , not from hyderabad

# 21 Nov 78
# 21st Nov. 78
# 21 Nov '78
# 21-11-1978
# boy ram of age 42
# 22nd nov 77
# 22 nd nov 77
# ram not seeta

# Sheetal w/o vishal,Pune,Maharashtra,B-,10-04-1981
# "Ramcharan Yadav" from gaziyabad
# Ramcharan Yadav from gaziyabad

# Sita not Seeta
# "ram charan" not "ram seeta"
# ram charan not ram seeta   ======> wrong NOT query with 2 tokens without quote
# Identified with NOT and Unidentified Dictionary :  {'Name': 'charan ram seeta', 'notQuery': {'Name': ['ram']}}

# "ramcharan yadav" not seeta
# ram not "seeta ram"

# Ramcharan Yadav "2530 3545 5565"
# "Ramcharan Yadav"
# "Ramcharan Yadav" "2530 3545 5565"
# Ram "2530 3545 5565"
# Mohan Lal from Delhi in mid 20's
# Mohandas,Approx. 23 years,Address Mumbai
# "Mohan Das",Approx. 23 years,Address Mumbai
# Mohan Das,Approx. 23 years,Address Mumbai
# Mohandas from Mumbai in mid twenty
# Mohandas from Mumbai in mid 20

# Dinesh Ram Yadav
# "Yadav Dinesh Ram"
# "Yadav Dinesh"
# "Dinesh"
# (“Name” Like “amar”) And ( (“Age” Between “35” And “50”) Or (“City” Equals “Mumbai”))
# (Name Like “amar singh”) And ( (Age Between 35 And 50) Or (City Equals Mumbai))
# mid 30‘s
# ------- for name address sep by " , "
# Seema Yadav, from Plot No 25 Echelon Square  Sector 32 Rohini  110042 Delhi
# Lina R V Dugal ,10, Virar, Indore - 452003, Madhya Pradesh

# Indira Gagan , F-151, Main Road, Near Ambedkar Gate, Jagat Puri, Bulandshahar-203001,Uttar Pradesh
# Iqbal Anis R Mistry , Opp.luna High School, Raopura, Meerut-250001-UttarPradesh
# K D Jayendra Lad,701 Jupiter Bldg, Hiranandani(c), A 4th Cross Lane, Lokhandwala, Andheri (west) Mumbai 400053, Maharashtra

# sita of Hyderabad
# like sita of Hyderabad
# Seema “Age” Between “35” And “50”
# Seema “Age” Between “35” And “40”
# sita of hyderabad , indore
#  sita of hyderabad not indore
# prajakta of pune , maharashtra
# ram , not male
# ram , not male not bhopal
# Ram not yadav
# ramdugla sita of indore mp
# ramdugla sita of indore , mp          # check 1  'Home_Address': ['mp', 'indore', 'madhya pradesh']
# ramdugla sita , indore mp             # check 2 'Home_Address': ['mp', 'indore', 'madhya pradesh', 'indore mp']
# ramdugla sita , indore madhya pradesh # check 3 'Home_Address': ['mp', 'indore', 'indore madhya pradesh', 'madhya pradesh']
# ramdugla sita , indore , mp
#  data main up likha ho aise query .. so here H_A becomes indore madhya pradesh but in database it is indore mp

# praj below 22 not 20
# {'year_of_Birth': ['1998'], 'AgeBelow': ['1998'], 'Name': 'praj', 'notQuery': {'year_of_Birth': ['2000']}}

# praj above 22 not 24
# {'year_of_Birth': ['1998'], 'AgeOver': ['1998'], 'Name': 'praj', 'notQuery': {'year_of_Birth': ['1996']}}

#  praj of 22 not 21
# {'Name': 'praj', 'year_of_Birth': ['1998'], 'notQuery': {'year_of_Birth': ['1999']}}

# seema between 22 and 32 not 24
# {'Name': 'seema', 'ageOther': ['1997', '1989'], 'notQuery': {'year_of_Birth': ['1996']}}

# seema 22 to 32 not 24
# {'ageOther': ['1998', '1988'], 'Name': 'seema', 'notQuery': {'year_of_Birth': ['1996']}}

# seema approx. 25  not 24
# {'ageOther': ['2000', '1990'], 'Name': 'seema', 'notQuery': {'year_of_Birth': ['1996']}}

# age lesser 22 not 20
# {'year_of_Birth': ['1998'], 'AgeBelow': ['1998'], 'notQuery': {'year_of_Birth': ['2000']}}

# age below 22 not 20
# {'year_of_Birth': ['1998'], 'AgeBelow': ['1998'], 'notQuery': {'year_of_Birth': ['2000']}}

# ram gupta
# ram yadav
# r. gupta
# ram y.
# y. ram
# iqbal anis r*

# Kiran RR Mistrry
# wildcard only works on single tokens

# Ramcharan Yadav of neena building , uttar pradesh , gaziyabad and adhar is 123412341234
# ram ,up, neena nui of gaziyabad , age between 22 and 34
#  ram of 305 narayan  peth , near vijay talkies pune 411030.
# raam of 305 narayan peth;near vijay,talkies,pune
# raam , 305 narayan peth of vijay talikes , pune
# Ramcharan Yadav of neena building , "uttar pradesh" , gaziyabad and adhar is 123412341234

# Wild Card on unique KYC ::
# version handling
# search keyword list

# seema of mid 50's , baner pashan , having adhar card 123412341234
# seema of mid 50's , baner pashan , panchavati
# mlae , pashan , 11 digit

# 20 aug to do list :
# 1. normalized mobile no to normal form , check mobile no global list
# 918080808080 , 91-8080808080 , +91-8080808080 , +918080808080 , 9090909090
# mobile or adhar 12 digit ==> 918080808080 going in adhar not in mobile
# praj gini of narayan peth,vijay talkies;from laxmi road at pune

# pending :: remove extracted tokens from query or from regex code if selected from dropdown
# dropdown flags :: add into dictionary
# adhar mobile ==> normalization from

# pincode , date , age , flat number

# Normalized data ==> mobile number , adhar number


# Mobile , home_address ==> list
# praj mem of 305 narayan peth ,near vijay talkies pune-411030

# like 'praj' ==> praj selected from dropdown whether it will go into likename ??
# like not 'praj mem' ==>  previous location

# after dropdown den check for not , like name and den delete name
# home address ==> not only pick first
# like praj ==> like or likes , praj not removed from stopwords if name is selected from dropdown
# Prakash of 305 Narayan peth , near Vijay Talkies , Pune - 411030 , Maharashtra , 9090909090 , 8080808080 ,123412341234 , ABCDE1234f , b+ve ,male

# name list ==> +ve name and not name from dropdown sapna not kapoor ==> name['sapna] ==> actual name['sapna,'kapoor']