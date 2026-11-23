import sqlite3
import pandas as pd

#2.4.1 Method 1
#print(f"\nprint SKU of products sold that is not in dim table product list".upper())
#df_data_set = set(df_data['SKU'])
#df_data2_set = set(df_data2['SKU'])
#mismatch = df_data_set-df_data2_set
#print(mismatch)

#2.4.2 Method 2
#def check_relationship(fact, dimention, key):
#    df_data_set = set(fact[key])
#    df_data2_set = set(dimention[key])
#    mismatch = df_data_set-df_data2_set
#    return mismatch

def check_relationship(fact, dimension, key):
    fact_set = set(fact[key])
    dim_set = set(dimension[key])
    mismatch = fact_set-dim_set
    return mismatch

#2.4.2.1 Define your list of validation tuples based on your assignment prompt
#print(f"\nDefine your list of validation tuples based on your assignment prompt".upper())
# Structure: (table_name, target_row_count, description_or_key_column)
#validation_tuples = [('supply_chain_datas', 'products', 'SKU'), ('supply_chain_datas', 'suppliers', 'Supplier index'), ('supply_chain_datas', 'logistics', 'Logistics index')]
#validation_results = []
#for supplychaindatas, dim, key2 in validation_tuples:
#    results = check_relationship(tables[supplychaindatas], tables[dim], key2)
#    print(results)
#    validation_results.append(results)
#print(validation_results)
def validate_warehouse(db):
    connection = sqlite3.connect(db)
    tables = {}
    tables['products'] = pd.read_sql("SELECT * FROM products", connection)
    tables['suppliers'] = pd.read_sql("SELECT * FROM suppliers", connection)
    tables['logistics'] = pd.read_sql("SELECT * FROM logistics", connection)
    tables['supply_chain_datas'] = pd.read_sql("SELECT * FROM supply_chain_datas", connection)
    connection.close()
    validation_tuples = [('supply_chain_datas', 'products', 'SKU'), ('supply_chain_datas', 'suppliers', 'Supplier index'), ('supply_chain_datas', 'logistics', 'Logistics index')]
    for fact_table, dim, key2 in validation_tuples:
        results = check_relationship(tables[fact_table], tables[dim], key2)
        if results:
            raise ValueError(f"Main data table '{fact_table}' references this/these {key2} that does not/do not exist in '{dim}' lookup table: {results}")