import pandas as pd


def read_fact_csv(path):
#    if csv[3]isna():
#        return spent money not entered for this transaction
    return pd.read_csv(path)

def extract_materials(month1, month2):
#august
    df_data = pd.read_excel(month1, sheet_name="NXT NVL", header=3)
#october
    df_data2 = pd.read_excel(month2, sheet_name="FORM NXT Tháng", header=1)
    print(df_data.head())
    
    columns_names = ['Material code', 'Material name', 'Pack size', 'Unit', 'Opening quantity', 'Received quantity', 'Issued quantity', 'Closing quantity']
    columns_names2 = ['Material code', 'Material name', 'Pack size', 'Unit', 'Opening quantity', 'Received quantity', 'Issued quantity', 'Closing quantity']
    columns = {}
    columns2 = {}
    target_column_position = [1, 2, 4, 5, 7, 10, 13, 15]
    target_column_position2 = [1, 2, 4, 5, 7, 10, 13, 15]
    df_cols = df_data.iloc[0].index
#extract Aug 2025
    for column, index in zip(columns_names, target_column_position):
        columns[column] = df_data.iloc[:,index]
#extract Oct 2026
    for column2, index2 in zip(columns_names2, target_column_position2):
        columns2[column2] = df_data2.iloc[:,index2]
#unified monthly
    df_data3 = pd.DataFrame(columns)
    df_data4 = pd.DataFrame(columns2)
#insert month tag
    df_data3.insert(0, 'month', 'aug 2025')
    df_data4.insert(0, 'month', 'oct 2026')
    unified_monthly = pd.concat([df_data3]+[df_data4], ignore_index=True)
#    print(unified_monthly)
#check which row belongs in the analy
#    filter_2 = unified_monthly.iloc[row].isnull().sum
#    unified_monthly = unified_monthly[filter_2]
    print(unified_monthly.shape)
    columns_to_handle = ['Opening quantity', 'Received quantity', 'Issued quantity', 'Closing quantity']
    unified_monthly[columns_to_handle] = unified_monthly[columns_to_handle].apply(pd.to_numeric, errors="coerce")
    print(unified_monthly.shape)
    print(unified_monthly.isnull().sum())

#    unified_monthly = unified_monthly.dropna(axis=0, thresh=7)
#    print(unified_monthly.head())
#take a detour a explore other ways to check for valid values in columns_to_handle 
#3.4.1 Method 1 (worked)
#    oq_num = pd.to_numeric(unified_monthly['Opening quantity'], errors="coerce").notna()
#    oq = unified_monthly[oq_num]
#    oq_set_index = oq.index
#    oq_set = set(oq_set_index)

#    rq_num = pd.to_numeric(unified_monthly['Received quantity'], errors="coerce").notna()
#    rq = unified_monthly[rq_num]
#    rq_set_index = rq.index
#    rq_set = set(rq_set_index)

#    iq_num = pd.to_numeric(unified_monthly['Issued quantity'], errors="coerce").notna()
#    iq = unified_monthly[iq_num]
#    iq_set_index = iq.index
#    iq_set = set(iq_set_index)

#    cq_num = pd.to_numeric(unified_monthly['Closing quantity'], errors="coerce").notna()
#    cq = unified_monthly[cq_num]
#    cq_set_index = cq.index
#    cq_set = set(cq_set_index)

#    check = oq_set & rq_set & iq_set & cq_set

#    unified_monthly = unified_monthly.loc[list(check)]

#3.4.2 Method 2
#Step 1 check notna for 4 audited columns
#    columns_to_handle = ['Opening quantity', 'Received quantity', 'Issued quantity', 'Closing quantity']
#    check_columns = unified_monthly[columns_to_handle].notna()
#    print(check_columns.head())
#Step 2: The Inspector Walks Horizontally (axis=1) and Demands Perfection (.all())
#Now, the inspector walks down your table row-by-row, looking from left to right across those 4 checkmarks [INDEX].
#    check2 = check_columns.all(axis=1)
#    unified_monthly = unified_monthly[check2]
#    print(unified_monthly.head())

#3.4.3 Method 3
#    string_lengths = map(len, ["dog", "cat", "zebra", "turtle"])
#For your database cleanup, we want the worker to look at your inventory rows one by one, 
#check if your 4 critical columns contain valid numbers, and give you back a list of True or False decisions
#Step 1:  Tell the worker what columns to look at
    mask_unified_monthly = map(lambda x, y, z, u: pd.notna(x) and pd.notna(y) and pd.notna(z) and pd.notna(u), unified_monthly["Opening quantity"],
                                    unified_monthly["Received quantity"], unified_monthly["Issued quantity"], unified_monthly["Closing quantity"])
#Step 2: How the lambda worker makes the decision
    mask_unified_monthly_list = list(mask_unified_monthly)
#Step3: Output
    unified_monthly = unified_monthly[mask_unified_monthly_list]
    unified_monthly2 = unified_monthly.copy()
    return unified_monthly2