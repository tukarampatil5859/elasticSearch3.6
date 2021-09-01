import pandas as pd
import numpy as np
#rm -rf ~/.local/lib/python3.6/site-packages/numpy  : if numpy creating problem for uninstalling numpy
#pip3 install numpy : for installing numpy
import recordlinkage
from recordlinkage.preprocessing import clean, phonetic
from recordlinkage.index import SortedNeighbourhood
global temp_list_dup

#function for finding transitive closure i.e getting all similiar records in a set of list
def transitive_cloure(array):
    new_list = [set(array.pop(0))]  # initialize first set with value of index `0`
    for item in array:
        for i, s in enumerate(new_list):
            if any(x in s for x in item):
                new_list[i] = new_list[i].union(item)
                break
        else:
            new_list.append(set(item))
    return new_list

def record_linkage(dfB):
    # Indexation step
    indexer = recordlinkage.Index()
    indexer.add(SortedNeighbourhood('full_name', window=9))
    indexer.add(SortedNeighbourhood('Home_Address', window=9))
    # indexer.add(SortedNeighbourhood('Date_of_Birth', window=9))
    # indexer.add(SortedNeighbourhood('Gender', window=9))
                #or
    # indexer.block(['Aadhar_no','Date_of_Birth','PAN_no'])
    candidate_links = indexer.index(dfB)
    # Comparison step
    compare_cl = recordlinkage.Compare()
    compare_cl.string('full_name', 'full_name', method='jarowinkler', threshold=0.80, label='full_name')
    compare_cl.string('Father_Name', 'Father_Name', method='jarowinkler', threshold=0.70, label='Father_Name')
    # compare_cl.string('Mother_Name', 'Mother_Name', method='jarowinkler', threshold=0.70, label='Mother_Name')
    compare_cl.exact('Date_of_Birth', 'Date_of_Birth', label='Date_of_Birth')
    compare_cl.exact('Aadhar_no', 'Aadhar_no', label='Aadhar_no')
    # compare_cl.exact('Pasport_no', 'Passport_no', label='Passport_no')
    compare_cl.exact('PAN_no', 'PAN_no', label='PAN_no')
    compare_cl.exact('Home_Address', 'Home_Address', label='Home_Address')
    # compare_cl.exact('Gender', 'Gender', label='Gender')
    # compare_cl.string('Home_Address', 'Home_Address',  method='jarowinkler',threshold=0.85, label='Home_Address')
    features = compare_cl.compute(candidate_links, dfB)
    # print(features.describe())
    # Classification step: if it matches more than 3 things then it is linked into 1
    matches = features[features.sum(axis=1) > 3]
    print(matches.index.values,'\n')
    #-----------------------------------------------------------------------
    # matches.index.values returns list of tuples of similar rows starting from 0(row number)
    list_tuples=[]
    list_empty=[]
    if len(matches.index.values)!=0:
        for val in matches.index.values:
            list_tuples.append(val)
        list_transtive_closure=transitive_cloure(list_tuples)
        return list_transtive_closure
    else:
        return list_empty

def add_cluster(df,list_new_dup):
    print(list_new_dup)
    list_rows = list(range(0, len(df)))
    print(list_rows)
    df = df.replace(np.nan, '', regex=True)  # to replace Nan value with nothing
    df = df.applymap(str)  # as below function works on string
    dict_clusterId = dict()
    df["ClusterId"] = ""
    clusterId = 0
    list_id = []  # to get Unique Id of similar records
    for val in list_new_dup:
        set_Uniq = set()
        set_id = val.pop()
        # id = df['Uniq_Id'][set_id]
        val.add(set_id)
        for index in val:
            # print("index:",index)
            list_rows.remove(index)
            dict_clusterId[index] = int(clusterId)
            set_Uniq.add(df['Uniq_Id'][index])
        list_id.append(set_Uniq)
        clusterId = clusterId + 1
    if len(list_rows) != 0:
        for indices in list_rows:
            dict_clusterId[indices] = int(clusterId)
            clusterId += 1
    for key, value in dict_clusterId.items():
        df["ClusterId"][key]=value
    # print(df.head())
    print(list_id)
    # gk = df.groupby('ClusterId')
    # TotClust = df.ClusterId.unique()
    # Let's print all the entries in Cluster
    # in all the groups formed.
    # for i in TotClust:
    #     print(gk.get_group(i))

    return df,list_id

#Function to add Unique ClusterId if no similar records were found by record linkage:
def add_UniqCluster(df):
    list_rows = list(range(0, len(df)))
    df = df.replace(np.nan, '', regex=True)  # to replace Nan value with nothing
    df = df.applymap(str)  # as below function works on string
    dict_clusterId = dict()
    df["ClusterId"] = ""
    clusterId = 0
    if len(list_rows) != 0:
        for indices in list_rows:
            dict_clusterId[indices] = int(clusterId)
            clusterId += 1
    for key, value in dict_clusterId.items():
        df["ClusterId"][key]=value
    # print(df.head())
    return df

# def merge(dfB,list_new_dup):
def merge(response_clust):
    # print("List of similar records after record linkages: ", list_new_dup)
    # dfB,list_id=add_cluster(dfB,list_new_dup)
    dfB = pd.DataFrame(response_clust)
    dfB = dfB.replace(np.nan, '', regex=True)  # to replace Nan value with nothing
    dfB = dfB.applymap(str)  # as below function works on string
    fval = lambda a: " , ".join(set(a))
    dfB = dfB.groupby(["ClusterId"], as_index=False).agg(
        {"KYC_Attributes": fval,"full_name": fval,"Father_Name": fval,"Date_of_Birth":fval,"Mother_Name": fval,
         "Gender":fval,"Nationality":fval,"Name":fval,"Office_Address":fval,"Communication_Address":fval,
         "PAN_no":fval, "Aadhar_no":fval,"Home_Address":fval,"Passport_no":fval,"DL":fval,"Surname":fval,
         "Spouse_Name":fval,"Blood_Group":fval,'Voter_Card_ID':fval,"Mobile_No":fval,
         "CreditCard":fval,"BankAcDetails":fval, 'Email_Id':fval,"ConfidenceScore":fval,"Uniq_Id":fval}).reset_index()
    # print(dfB)
    # dfA = dfB["full_name"].groupby([dfB.Aadhar_no]).apply(list).reset_index()

    dfB = dfB.reindex(columns=["ClusterId","Uniq_Id","ConfidenceScore","full_name",
     "KYC_Attributes", "Father_Name", "Mother_Name", "Spouse_Name", "Date_of_Birth",
    "Gender", "Blood_Group", "Home_Address", "Office_Address", "Communication_Address", "PAN_no",
     "Aadhar_no","Passport_no","DL", "BankAcDetails", "CreditCard", "Mobile_No", "Email_Id",
    "Nationality", "Voter_Card_ID", "Surname", "Name"])

    # dfB.to_csv('/home/sunbeam/Desktop/Agency22/myproject/data/Record_linkage.csv')
    return temp_list_dup, dfB

def main(response_list):
    global temp_list_dup
    print(response_list)
    dfB = pd.DataFrame(response_list)
    # =================================
    #temporary changes for column name mistakes:
    # print("column list of response")
    # print(dfB.columns.values)

    if "DL" not in dfB.columns:
        dfB["DL"] = np.nan
    if "Spouse_Name" not in dfB.columns:
        dfB["Spouse_Name"] = np.nan
    if "Voter_Card_ID" not in dfB.columns:
        dfB["Voter_Card_ID"] = np.nan
    if "CreditCard" not in dfB.columns:
        dfB["CreditCard"]=np.nan
    if " Home_Address" in dfB.columns:
        dfB["Home_Address"]=dfB[" Home_Address"]
        del dfB[" Home_Address"]
    if " PSK POPSK Address" in dfB.columns:
        del dfB[" PSK POPSK Address"]
    if ' Passport Issue City' in dfB.columns:
        del dfB[' Passport Issue City']
    if 'Bank_Name' in dfB.columns:
        del dfB['Bank_Name']
    if 'PostOffice_Name' in dfB.columns:
        del dfB['PostOffice_Name']
    if 'Passport_Expiry' in dfB.columns:
        del dfB['Passport_Expiry']
    if 'Mother_Surname' in dfB.columns:
        del dfB['Mother_Surname']
    if 'Father_Surname' in dfB.columns:
        del dfB['Father_Surname']
    if 'Mother_Surname' in dfB.columns:
        del dfB['Mother_Surname']
    dfB=dfB.rename(columns={' Office_Address': 'Office_Address',' Communication_Address':'Communication_Address'})

    # print(dfB.columns.values)
    # print(dfB["Home_Address"].head())
    # ===================================
    # dfB=pd.read_csv('/home/sunbeam/Desktop/Agency22/myproject/data/Result.csv')
    # cleaning process:
    s = pd.Series(dfB['full_name'])
    clean(s)
    phonetic(s, method="metaphone", concat=True, encoding='utf-8', decode_error='strict')
    list_new_dup=[]
    # Do Record Linkage if it has more than 1 record to find similar for:
    if len(dfB)>1:
        list_new_dup=record_linkage(dfB)
        temp_list_dup = list_new_dup
    if len(list_new_dup) != 0:
        df_cluster,list_id=add_cluster(dfB,list_new_dup)
        temp_list_dup = list_id
        return list_id, df_cluster
    else:
        df_UniqCluster=add_UniqCluster(dfB)
        print("No Similar records")
        return list_new_dup,df_UniqCluster
# #
# response=[{'KYC_Attributes': 'Voter ID Card', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,263002,Nainital,Uttarakhand', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 263002 Nainital Uttarakhand', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '0', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': 'DZJ0001380', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '0', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc22'}, {'KYC_Attributes': 'Driving License', 'DL': 'DL12200502222123', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Dehradun,248003,Uttarakhand', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Dehradun 248003 Uttarakhand', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '63655225234', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': '', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '0', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc337'}, {'KYC_Attributes': 'Telecom', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Grater Noida,201301,Uttar Pradesh', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Grater Noida 201301 Uttar Pradesh', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '63655225238', 'Father_Name': '', 'Voter_Card_ID': '', 'Mother_Name': '', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '601020405027', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc208'}, {'KYC_Attributes': 'Passport', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Gurgan-122001,Haryana', 'Gender': 'Female', 'Name': 'Seema', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Gurgan 122001 Haryana', 'BankAcDetails': '0', 'Blood_Group': 'B+', 'Mobile_No': '63655225239', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': 'sy@gmail.com', 'Aadhar_no': '221020405022', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav', 'Spouse_Name': 'Sita Yadav', 'Surname': 'Yadav', 'PAN_no': 'YBRQP7011C', 'Passport_no': 'J8369854', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc985'}, {'KYC_Attributes': 'NCRB', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Allahabad, 211002,Uttar Pradesh', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Allahabad  211002 Uttar Pradesh', 'BankAcDetails': '24242323252526', 'Blood_Group': '', 'Mobile_No': '0', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': '', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '0', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': 'J8369845', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc1293'}, {'KYC_Attributes': 'Pan', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Gurgan-122001,Haryana', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Gurgan 122001 Haryana', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '0', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '221020405022', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': 'Sita Yadav', 'Surname': '', 'PAN_no': 'YBRQP7011C', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc1701'}, {'KYC_Attributes': 'Pan', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Rohini, 110042,Delhi', 'Gender': 'Female', 'Name': 'Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Rohini  110042 Delhi', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '0', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': '', 'Aadhar_no': '601020405026', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': 'YBRQP4012D', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc1702'}, {'KYC_Attributes': 'Bank KYC', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32 Lucknow,226002,Uttar Pradesh', 'Gender': 'Female', 'Name': 'Yadav Seema Rampal ', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Lucknow 226002 Uttar Pradesh', 'BankAcDetails': '24242323252528', 'Blood_Group': '', 'Mobile_No': '63655225235', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': 'ysr@gmail.com', 'Aadhar_no': '0', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Yadav Seema Rampal  ', 'Spouse_Name': 'Sita Yadav', 'Surname': '', 'PAN_no': 'YBRQP4015D', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc1114'}, {'KYC_Attributes': 'Airline', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Mohali,160062, Punjab', 'Gender': 'Female', 'Name': 'Rampal Seema Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Mohali 160062  Punjab', 'BankAcDetails': '24242323252525', 'Blood_Group': '', 'Mobile_No': '63655225237', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': '', 'Date_of_Birth': '1979-09-23', 'Email_Id': 'rsy@gmail.com', 'Aadhar_no': '0', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Rampal Seema Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc524'}, {'KYC_Attributes': 'Company KYC', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Kanpur, 208002,Uttar Pradesh', 'Gender': 'Female', 'Name': 'Seema Rampal Renu Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Kanpur  208002 Uttar Pradesh', 'BankAcDetails': '24242323252529', 'Blood_Group': 'O+', 'Mobile_No': '6365522523', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': 'srry@gmail.com', 'Aadhar_no': '6010204051279', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': 'HCL IT City Block no 3,Mastemau Sultanpur Road, Lucknow,226002,Uttar Prades', 'full_name': 'Seema Rampal Renu Yadav ', 'Spouse_Name': 'Sita Yadav', 'Surname': '', 'PAN_no': 'YRBQP4015D', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc784'}, {'KYC_Attributes': 'Aadhar', 'DL': '', 'Communication_Address': 'Plot No.25,Echelon Square, Sector,32,Aroli Navi Mumabi,400708, Maharashtra', 'Gender': 'Female', 'Name': 'Seema R R Yadav', 'Home_Address': 'Plot No 25 Echelon Square  Sector 32 Aroli Navi Mumabi 400708  Maharashtra', 'BankAcDetails': '0', 'Blood_Group': '', 'Mobile_No': '63655225236', 'Father_Name': 'Rampal Yadav', 'Voter_Card_ID': '', 'Mother_Name': 'Renu Yadav', 'Date_of_Birth': '1979-09-23', 'Email_Id': 'srr@gmail.com', 'Aadhar_no': '6010204051278', 'CreditCard': '', 'Nationality': 'Indian', 'Office_Address': '', 'full_name': 'Seema R R Yadav ', 'Spouse_Name': '', 'Surname': '', 'PAN_no': '', 'Passport_no': '', 'ConfidenceScore': 100, 'Uniq_Id': 'kyc654'}]
# main(response)
# dfB = pd.DataFrame(response)
# df_merged,list_id=merge(dfB,temp_list_dup)