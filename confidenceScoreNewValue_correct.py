import pandas as pd
import re
import regexNew
from fuzzywuzzy import fuzz,process
from autocorrect import Speller
from spellchecker import SpellChecker
from datetime import date

global recogTokenclass1, recogTokenclass2, recogTokenclass3, recogTokenclass4, conf_score_new,score
global cnt1,cnt2,cnt3,cnt4,Name_match

def category(dict_identified):
    dict1=dict_identified
    print("Category class------------------------------------------")
    cat_class=list(dict_identified.keys())
    # print(dict1)
    print(cat_class)
    recog_class1=[]
    recog_class2=[]
    recog_class3=[]
    class_dict=dict()
    return dict1

def classChecker(cnt1, cnt2, cnt3,cnt4):
    # All Four Classes are Present(Class 1 , Class 2 , Class 3 , Class 4)
    if (cnt1 != 0 and cnt2 != 0 and cnt3 != 0 and cnt4 != 0):
        print("All 4 are Present")
        score = all1234Calc(cnt1, cnt2, cnt3, cnt4,recogTokenclass1,recogTokenclass2,recogTokenclass3,recogTokenclass4)

    # Any Three classes are Present(Class 1 , Class 2 , Class 3)
    elif (cnt1 != 0 and cnt2 != 0 and cnt3 != 0 and cnt4 == 0):
        print("Class 1 , 2, 3 are Present")
        if recogTokenclass1!=0:
            score = all123Calc(cnt1, cnt2, cnt3,recogTokenclass1,recogTokenclass2,recogTokenclass3)
        else:
            score = nameCalc123(cnt1, cnt2, cnt3,recogTokenclass1,recogTokenclass2,recogTokenclass3)
    elif (cnt1 != 0 and cnt2 == 0 and cnt3 != 0 and cnt4 != 0):
        print("Class 1 , 3 , 4 are Present")
        if recogTokenclass1!=0:
            score = all123Calc(cnt1, cnt3, cnt4,recogTokenclass1,recogTokenclass3,recogTokenclass4)
        else:
            score = nameCalc123(cnt1, cnt3, cnt4,recogTokenclass1,recogTokenclass3,recogTokenclass4)
    elif (cnt1 == 0 and cnt2 != 0 and cnt3 != 0 and cnt4 != 0):
        print("Class 2 , 3 , 4 are Present")
        # score = all123Calc(cnt2, cnt3, cnt4,recogTokenclass2,recogTokenclass3,recogTokenclass4)
        score = nameCalc123(cnt2, cnt3, cnt4,recogTokenclass2,recogTokenclass3,recogTokenclass4)
    elif (cnt1 != 0 and cnt2 != 0 and cnt3 == 0 and cnt4 != 0):
        print("Class 1 , 2 , 4 are Present")
        if recogTokenclass1!=0:
            score=all123Calc(cnt1, cnt2, cnt4,recogTokenclass1,recogTokenclass2,recogTokenclass4)
        else:
            score = nameCalc123(cnt1, cnt2, cnt4,recogTokenclass1,recogTokenclass2,recogTokenclass4)


    # Any Two classes are Present(Class 1 , Class 2 )
    elif (cnt1 != 0 and cnt2 != 0 and cnt3 == 0 and cnt4 == 0):
        print("Class 1 ,2 are Present")
        if recogTokenclass1!=0:
            score=all12Calc(cnt1,cnt2,recogTokenclass1,recogTokenclass2)
        else:
            score=nameCalc2(cnt1,cnt2,recogTokenclass1,recogTokenclass2)
    elif (cnt1 == 0 and cnt2 != 0 and cnt3 != 0 and cnt4 == 0):
        print("Class 2 ,3 are Present")
        # score=all12Calc(cnt2,cnt3,recogTokenclass2,recogTokenclass3)
        score=nameCalc2(cnt2,cnt3,recogTokenclass2,recogTokenclass3)
    elif (cnt1 != 0 and cnt2 == 0 and cnt3 != 0 and cnt4 == 0):
        print("Class 1 ,3 are Present")
        score=all12Calc(cnt1, cnt3,recogTokenclass1,recogTokenclass3)
    elif (cnt1 != 0 and cnt2 == 0 and cnt3 == 0 and cnt4 != 0):
        print("Class 1 ,4 are Present")
        score=all12Calc(cnt1, cnt4,recogTokenclass1,recogTokenclass4)
    elif (cnt1 == 0 and cnt2 != 0 and cnt3 == 0 and cnt4 != 0):
        print("Class 2 ,4 are Present")
        # score=all12Calc(cnt2, cnt4,recogTokenclass2,recogTokenclass4)
        score = nameCalc2(cnt2, cnt4,recogTokenclass2,recogTokenclass4)
    elif (cnt1 == 0 and cnt2 == 0 and cnt3 != 0 and cnt4 != 0):
        print("Class 3 ,4 are Present")
        score=all12Calc(cnt3, cnt4,recogTokenclass3,recogTokenclass4)

    # Any One classes are Present(Class 1 , Class 2 )
    elif (cnt1 != 0 and cnt2 == 0 and cnt3 == 0 and cnt4==0):
        print("Only Class 1 is Present")
        score=all1Calc(cnt1,recogTokenclass1)
    elif (cnt1 == 0 and cnt2 != 0 and cnt3 == 0 and cnt4==0):
        print("Only Class 2 is are Present")
        sc=all1Calc(cnt2,recogTokenclass2)
        if sc>0:
            score=Name_match
        else:
            score=sc
    elif (cnt1 == 0 and cnt2 == 0 and cnt3 != 0 and cnt4==0):
        print("Only Class 3 is are Present")
        score=all1Calc(cnt3,recogTokenclass3)
    elif (cnt1 == 0 and cnt2 == 0 and cnt3 == 0 and cnt4 != 0):
        print("Only Class 4 is Present")
        score = all1Calc(cnt4, recogTokenclass4)
    return score

def nameCalc123(cnt2, cnt3, cnt4,recogTokenclass2,recogTokenclass3,recogTokenclass4):
    global conf_score
    print("NameCalc123 called")
    if recogTokenclass2 == 1 and Name_match < 91:
        conf_score1 = Name_match
    else:
        conf_score1 =91*(recogTokenclass2/cnt2)
    conf_score2 = 8 * (recogTokenclass3 / cnt3)
    conf_score3 = 1 * (recogTokenclass4 / cnt4)
    conf_score = conf_score1 + conf_score2 + conf_score3
    return conf_score

def nameCalc2(cnt2,cnt3,recogTokenclass2,recogTokenclass3):
    global conf_score
    if recogTokenclass2==1 and Name_match<90:
        conf_score1 = Name_match
    else:
        conf_score1=90 * ( recogTokenclass2 / cnt2)
    conf_score2 = 10 * (recogTokenclass3 / cnt3)
    conf_score = conf_score1 + conf_score2
    return conf_score

def all1234Calc(cnt1, cnt2, cnt3,cnt4,r1,r2,r3,r4):
    conf_score1 = 82 * ( r1/ cnt1)
    conf_score2 = 10 * ( r2/ cnt2)
    conf_score3 = 7 * ( r3/ cnt3)
    conf_score4 = 1 * ( r4/ cnt4)
    conf_score = conf_score1 + conf_score2 + conf_score3 + conf_score4
    # print('confidence score from fun', conf_score)
    return conf_score

def all123Calc(cnt1, cnt2, cnt3,r1,r2,r3):
    conf_score1 =  91 * ( r1/ cnt1)
    conf_score2 = 8* ( r2/ cnt2)
    conf_score3 =  1 * ( r3 / cnt3)
    conf_score = conf_score1 + conf_score2 + conf_score3
    # print('confidence score from fun', conf_score)
    return conf_score

def all12Calc(cnt1, cnt2,r1,r2):
    # print("-------------------------",cnt1,cnt2,r1,r2)
    global conf_score
    conf_score1 = 90 * ( r1 / cnt1)
    conf_score2 =  10* ( r2 / cnt2)
    conf_score = conf_score1 + conf_score2
    return conf_score

def all1Calc(cnt1,r1):
    conf_score = 100 *(r1  / cnt1)
    # print('confidence score from fun', conf_score)
    return conf_score
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++==
def adharno(key,val,input_dict):
    global recogTokenclass1
    # print(val[key])
    if input_dict[key] == val[key]:
        recogTokenclass1 += 1
# def UnidentifiedAadhar(key,val,input_dict):
#     global recogTokenclass1
#     if input_dict["Aadhar_no"] == val["Aadhar_no"]:
#         recogTokenclass1 += 1
def pan(key,val,input_dict):
    global recogTokenclass1
    if input_dict[key].lower()==val[key].lower():
        recogTokenclass1+=1

# def UnidentifiedPan(key,val,input_dict):
#     global recogTokenclass1
#     if input_dict["PAN_no"] == val["PAN_no"]:
#         recogTokenclass1 += 1

#to match for all permuatations of match
def name(key, val,input_dict):
    global recogTokenclass2,Name_match
    # for naam in list_name():
    regex = re.compile('[*?]')
    if regex.search(input_dict[key]) == None:
        Name_match=0
        for value in val["permuted_name"]:
            ESvalue=" ".join(value.split()) # for removing extra spaces anywhere in data
            dict_val=" ".join(input_dict[key].split())
            # print("permuted name", ESvalue, ",", dict_val)
            Name_match_new = fuzz.partial_ratio(dict_val.lower(), ESvalue.lower())
            if Name_match_new>Name_match:
                Name_match=Name_match_new
            # print(Name_match,";",ESvalue, ",", dict_val)
        if Name_match >=70:  #for 50:In sita ->seeta true but for ramesh ->rakesh,rajesh comes
            recogTokenclass2 += 1;
            # Name_match = 100 #put later for soundex analyser
            Name_match = Name_match #put later for soundex analyser
        elif Name_match >= 30 and Name_match < 70:
            recogTokenclass2 += 1;
            Name_match = Name_match
    else:
        Name_match = fuzz.partial_ratio(input_dict[key].lower(), val["full_name"].lower())
        if Name_match >=50:  #for wildcard if ratio  isgreater than 70 % then we are giving it 100% match
            recogTokenclass2 += 1;
            Name_match=100
        elif Name_match<40 and Name_match<50:
            recogTokenclass2 += 1;
            Name_match = Name_match


def likename(key,val,input_dict):
    global recogTokenclass2, Name_match
    Name_match = 0
    for value in val["permuted_name"]:
        ESvalue = " ".join(value.split())
        dict_val = " ".join(input_dict[key].split())
        # print("permuted name", ESvalue, ",", dict_val)
        # Name_match_new = fuzz.ratio(dict_val.lower(), ESvalue.lower())
        Name_match_new = fuzz.partial_ratio(dict_val.lower(), ESvalue.lower())
        if Name_match_new > Name_match:
            print("permuted name", value, ",", input_dict[key],":",Name_match_new)
            Name_match = Name_match_new
    if Name_match >= 50:  # for 50:In sita ->seeta true but for ramesh ->rakesh,rajesh comes
        recogTokenclass2 += 1;
        Name_match=100
        # Name_match=Name_match
    elif Name_match >= 30 and Name_match < 45:
        recogTokenclass2 += 1;
        Name_match=Name_match
        print("30 and 45",Name_match)

#
# def likename(key,val,input_dict):
#     global recogTokenclass2, Name_match
#     Name_match = 0
#     for value in val["permuted_name"]:
#         ESvalue = " ".join(value.split())
#         dict_val = " ".join(input_dict[key].split())
#         # print("permuted name", ESvalue, ",", dict_val)
#         # Name_match_new = fuzz.ratio(dict_val.lower(), ESvalue.lower())
#         Name_match_new = fuzz.partial_ratio(dict_val.lower(), ESvalue.lower())
#         if Name_match_new > Name_match:
#             # print("permuted name", value, ",", input_dict[key],":",Name_match_new)
#             Name_match = Name_match_new
#     if Name_match >= 50:  # for 50:In sita ->seeta true but for ramesh ->rakesh,rajesh comes
#         recogTokenclass2 += 1;
#         Name_match=100
#         # Name_match=Name_match
#     elif Name_match >= 30 and Name_match < 45:
#         recogTokenclass2 += 1;
#         Name_match=Name_match
#         print("30 and 45",Name_match)

def nameother(key, val,input_dict):
    global recogTokenclass2,Name_match
    # for naam in list_name():
    regex = re.compile('[*?]')
    if regex.search(input_dict[key]) == None:
        Name_match=0
        for value in val["permuted_name"]:
            ESvalue=" ".join(value.split()) # for removing extra spaces anywhere in data
            dict_val=" ".join(input_dict[key].split())
            # print("permuted name", ESvalue, ",", dict_val)
            Name_match_new = fuzz.partial_ratio(dict_val.lower(), ESvalue.lower())
            if Name_match_new>Name_match:
                Name_match=Name_match_new
            # print(Name_match,";",ESvalue, ",", dict_val)
        if Name_match >=70:  #for 50:In sita ->seeta true but for ramesh ->rakesh,rajesh comes
            recogTokenclass2 += 1;
            # Name_match = 100 #put later for soundex analyser
    else:
        Name_match = fuzz.partial_ratio(input_dict[key].lower(), val[key].lower())
        if Name_match >=70:  #for wildcard if ratio  isgreater than 70 % then we are giving it 100% match
            recogTokenclass2 += 1;
            Name_match=100

def surname(key,val,input_dict):
    global recogTokenclass2
    fr = fuzz.WRatio(input_dict[key], val[key])
    if fr > 75:
        recogTokenclass2 += 1;

def father(key,val,input_dict):
    global recogTokenclass3
    fr = fuzz.WRatio(input_dict[key], val[key])
    if fr > 90:
        recogTokenclass3 += 1;

def mother(key,val,input_dict):
    global recogTokenclass3
    fr = fuzz.WRatio(input_dict[key], val[key])
    if fr > 90:
        recogTokenclass3 += 1;

def spouse(key,val,input_dict):
    global recogTokenclass3
    fr = fuzz.partial_ratio(input_dict[key], val[key])
    # print("spouse match ratio",fr,val[key])
    if fr > 85:
        recogTokenclass3 += 1;

def dob(key,val,input_dict):
    global recogTokenclass3
    print(type(input_dict[key]),type(val[key]))
    if str(input_dict[key]) == val[key]:
        print("date matched")
        recogTokenclass3 += 1

    # pass#adhar 123456789101,ABCDE1234F a male and an indian having B+ blood group

def gender(key,val,input_dict):
    global recogTokenclass4
    if input_dict[key].title() == val[key].title():
        recogTokenclass4 += 1

def bloodgroup(key,val,input_dict):
    global recogTokenclass4
    for bg in input_dict[key]:
        if bg == val[key].lower():
            # print("match blood group",bg)
            recogTokenclass4 += 1

def contains_word(s, w):
    if (' ' + w + ' ') in (' ' + s + ' '):
        return (' ' + w + ' ') in (' ' + s + ' ')

def home(key,val,input_dict):
    global recogTokenclass3
    ha=0
    for addr in input_dict[key]:
        if contains_word(val[key].lower(),addr.lower()):
            fr = fuzz.partial_ratio(addr.lower(), val[key].lower())
            # fr = fuzz.WRatio(input_dict[key], val[key])
            print("location fuzzy value", fr)
            if fr >= 40:
                ha=ha+1
    if ha!=0:
        recogTokenclass3 += 1;

def addressother(key,val,input_dict):
    global recogTokenclass3
    ha=0
    for addr in input_dict["Home_Address"]:
        if contains_word(val["Home_Address"].lower(),addr.lower()):
            fr = fuzz.partial_ratio(addr.lower(), val["Home_Address"].lower())
            # fr = fuzz.WRatio(input_dict[key], val[key])
            print("location fuzzy value", fr)
            if fr >= 90:
                ha=ha+1
    if ha!=0:
        recogTokenclass3 += 1;

def ofcaddress(key,val,input_dict):
    global recogTokenclass3
    fr = fuzz.WRatio(input_dict[key], val[key])
    if fr > 75:
        recogTokenclass3 += 1;

def comm(key,val,input_dict):
    global recogTokenclass3
    fr = fuzz.WRatio(input_dict[key], val[key])
    if fr > 75:
        recogTokenclass3 += 1;

def passport(key,val,input_dict):
    global recogTokenclass1
    if input_dict[key].lower() == val[key].lower():
        recogTokenclass1 += 1

def bank (key,val,input_dict):
    global recogTokenclass1
    if input_dict[key] == val[key]:
        recogTokenclass1 += 1

def credit (key,val,input_dict):
    global recogTokenclass1
    if input_dict[key] == val[key]:
        recogTokenclass1 += 1

def mobile(key,val,input_dict):
    global recogTokenclass1
    for mob in input_dict[key]:
        if float(mob) == float(val[key]):
            recogTokenclass1 += 1

def email(key,val,input_dict):
    global recogTokenclass1
    for mail in input_dict[key]:
        if mail.lower()== val[key].lower():
            recogTokenclass1 += 1

def nationality(key,val,input_dict):
    global recogTokenclass4
    for nat in input_dict[key]:
        if nat == val[key]:
            recogTokenclass4 += 1

def voter(key,val,input_dict):
    global recogTokenclass1
    if input_dict[key] == val[key].lower():
        recogTokenclass1 += 1
        print(recogTokenclass1)

def drivinglicence(key,val,input_dict):
    global recogTokenclass1
    if input_dict[key] == val[key].lower():
        recogTokenclass1 += 1
        print(recogTokenclass1)

def age(key,val,input_dict):
    global recogTokenclass3
    if int(input_dict[key][0]) == int(val[key]):
        recogTokenclass3 += 1
#
# def YOB(key,val,input_dict):
#     global recogTokenclass3
#     if int(input_dict[key][0]) == int(val[key]):
#         recogTokenclass3 += 1
#         print(input_dict[key][0],val[key])
def YOB(key,val,input_dict):
    global recogTokenclass3
    # for value in range(int(input_dict[key][0]),int(input_dict[key][1])+1):
    for value in range(int(input_dict[key][0]),int(input_dict[key][0])+1):
        # print("aman.........",value,val["year_of_Birth"])
        # if int(input_dict[key][0]) == int(val[key]):
        if int(value) == int(val["year_of_Birth"]):
            recogTokenclass3 += 1

def ageother(key,val,input_dict):
    global recogTokenclass3
    # print("hiiiiiiiiiiiii",input_dict[key][0],input_dict[key][1])
    # for value in range(int(input_dict[key][1]),int(input_dict[key][0])+1):
    for value in range(int(input_dict[key][1]),int(input_dict[key][0])):
        # print(value,val["year_of_Birth"])
        if int(value)==int(val["year_of_Birth"]):
            recogTokenclass3 += 1

def ageover(key,val,input_dict):
    global recogTokenclass3
    for value in range(1920,int(input_dict[key][0])):
        # print(value, val["year_of_Birth"])
        if int(value) == int(val["year_of_Birth"]):
            recogTokenclass3 += 1 # correct final
def agebelow(key,val,input_dict):
    global recogTokenclass3
    today = date.today()
    for value in range(int(input_dict[key][0])+1,today.year):
        # print(value, val["Age"])
        if int(value) == int(val["year_of_Birth"]):
            recogTokenclass3 += 1  # correct final

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=
def spell_corrector(query):
    spell = SpellChecker()
    # CONFIG_PATH = configs.spelling_correction.brillmoore_wikitypos_en
    # model = build_model(CONFIG_PATH, load_trained=True)
    # query = 'Ramcharan Yadav an Indian mlae wih age 78 and adhar 123456789101,ABCDE1234F or J1234567'
    # words = spell.split_words(query)
    # for word in query.split(' '):
        # res = [spell.correction(word) for word in words]
    sent = ''
    for word in spell.split_words(query):
        word=spell.correction(word)#for dictionary spelling correction
        # print("Before BERT...",word)
        sent = sent + word +' '
        # x = model([word])#for BERT name spelling correction
        # sent = sent + str(x[0]) + ' '

    print(sent)
    print("+++++++++++The corrected query is above and BERT below++++++++++++++++++++++++")
    # for Bert  name spelling corrector:
    # CONFIG_PATH = configs.spelling_correction.brillmoore_wikitypos_en
    # model = build_model(CONFIG_PATH, load_trained=True)
    # sent = ''
    # for word in query.split(' '):
    #     x = model([word])
    #     sent = sent + str(x[0]) + ' '
    # print(sent)
    return sent
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#dynamic switch to find confidence of input key searched
def dynamic_switch(arg):
    switcher = {
        "Aadhar_no": adharno,
        "PAN_no": pan,
        "Name":name,
        "Surname": surname,
        # "full_name": {"type": "string"},
        "Father_Name": father,
        "Mother_Name": mother,
        "Spouse_Name": spouse,
        "Date_of_Birth":dob,
        "Gender": gender,
        "Blood_Group": bloodgroup,
        "Home_Address": home,
        "Office_Address": ofcaddress,
        "Communication_Address": comm,
        "Passport_no": passport,
        "BankAcDetails": bank,
        "CreditCard": credit,
        "Mobile_No": mobile,
        "Email_Id": email,
        "Nationality": nationality,
        "Voter_Card_ID": voter,
        "DL": drivinglicence,
        "Age":age,
        "ageOther":ageother,
        "AgeOver": ageover,
        "AgeBelow": agebelow,
        "likeName":likename,
        "nameOther": nameother,
        "addressOther": addressother,
        "year_of_Birth":YOB
        # "notQuery": notquery
    }
    # get() method of dictionary data type returns value of passed argument if it is present in dictionary otherwise second argument will be assigned as default value of passed argument
    # return switcher.get(arg, lambda key,val : "invalid input")
    return switcher.get(arg, lambda key : "invalid input")

def search_input(input_dict,Uniq_Id,ESDict):
    global recogTokenclass1,recogTokenclass2,recogTokenclass3,recogTokenclass4,conf_score_new,score
    conf_score_new=0
    recogTokenclass1 = 0
    recogTokenclass2 = 0
    recogTokenclass3 = 0
    recogTokenclass4 = 0
    global cnt1,cnt2,cnt3,cnt4,Name_match
    Name_match=0
    for key in input_dict:
        method = dynamic_switch(key)
        method(key,ESDict,input_dict)
    # Pass Calculated Token Counts to classChecker function
    print("---------------------------------------------")
    print("Recognised token value per class",recogTokenclass1," ", recogTokenclass2," ",recogTokenclass3," ",recogTokenclass4)
    print(" Actual token value per class", cnt1, " ", cnt2, " ", cnt3," ",cnt4)
    conf_score_new = classChecker(cnt1, cnt2, cnt3,cnt4)

    ESDict.update({'ConfidenceScore': conf_score_new})
    ESDict.update({'Uniq_Id': Uniq_Id})
    print(ESDict)
    print(["Confidence score:-: ",conf_score_new,"Name match %:-",Name_match if Name_match!= 0 else conf_score_new])
    # recogTokenclass1 = recogTokenclass2 = recogTokenclass3 = recogTokenclass4=0
    print("+++++++++++++++++++++++++++++++++++++++++++++++++")
    return ESDict
    # df['confidenceScore']=conflist
    # df.to_csv('/home/sunbeam/Desktop/Agency22/elasticsearch_doc/ResultES_csv_conf.csv',index=False)
        # print("RESET recognised token value",recogTokenclass1," ", recogTokenclass2," ",recogTokenclass3)

def main(query):
    # global list_name
    # list_name=nameSuggestList1
    global cnt1,cnt2,cnt3,cnt4
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    cnt4 = 0
    # query = spell_corrector(query)
    dict_identified =regexNew.checker(query)
    # query1 = re.split(r'[;,\s]\s*', query)
    # filtered_query = regexJson.remove_stop_word(query)
    # dict_identified = regexJson.data_received(filtered_query)
    print(dict_identified)
    # dict1 = category(dict_identified)
    cat_class = list(dict_identified.keys())
    # Count No of Tokens Present in Respective Class
    for val in cat_class:
        if val in class1:
            cnt1 = cnt1 + 1
        elif val in class2:
            cnt2 = cnt2 + 1
        elif val in class3:
            cnt3 = cnt3 + 1
        elif val in class4:
            cnt4 = cnt4 + 1
    print("Total no of Tokens in Class 1 : ", cnt1, " , Class 2 : ", cnt2, " , Class 3 : ", cnt3," , Class 4 : ", cnt4,)
    return dict_identified

def mainName(query):
    global cnt1
    global cnt2
    global cnt3
    global cnt4

    # query = spell_corrector(query)
    # changed:
    dict_identified = {'Name' : query}
    #dict_identified =regexNew.checker(query)
    # query1 = re.split(r'[;,\s]\s*', query)
    # filtered_query = regexJson.remove_stop_word(query)
    # dict_identified = regexJson.data_received(filtered_query)
    print(dict_identified)
    # dict1 = category(dict_identified)
    cat_class = list(dict_identified.keys())
    # Count No of Tokens Present in Respective Class
    for val in cat_class:
        if val in class1:
            cnt1 = cnt1 + 1
        elif val in class2:
            cnt2 = cnt2 + 1
        elif val in class3:
            cnt3 = cnt3 + 1
        elif val in class4:
            cnt4 = cnt4 + 1
    # print("Total no of Tokens in Class 1 : ", cnt1, " , Class 2 : ", cnt2, " , Class 3 : ", cnt3)
    return dict_identified

class4 = ['Blood_Group', 'Nationality', 'Gender']
class3 = ['Surname', 'Father_Name', 'Mother_Name', 'Spouse_Name', 'Home_Address', 'Date_of_Birth', 'Age',"ageOther","AgeBelow","AgeOver","year_of_Birth"]
class2 = ['Name',"likeName","nameOther"]
class1 = ['PAN_no', 'Aadhar_no', 'Passport_no', 'Voter_Card_ID', 'Email_Id', 'BankAcDetails', 'CreditCard', 'Mobile_No','DL']

# class3 = ['Surname', 'Father_Name', 'Mother_Name', 'Spouse_Name', 'Blood_Group', 'Home_Address', 'Nationality',
#           'Gender', 'Date_of_Birth', 'Age']
# class2 = ['Name']
# class1 = ['PAN_no', 'Aadhar_no', 'Passport_no', 'Voter_Card_ID', 'Email_Id', 'BankAcDetails', 'CreditCard',
#           'Mobile_No']

# query=input("Enter query...:-")
# dict1=main(query)
