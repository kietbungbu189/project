import pandas as pd
import functools
import numpy as np
import math

#1 check if stock levels are above threshold
#required_stocklevel = 20 
#2.1.1 Method 1
#print(f"\nCHECK IF STOCK LEVELS ARE ABOVE THRESHOLD")
#stock_to_check = []
#for cell in df_data['Stock levels']:
#    if pd.notna(cell):
#        if int(float(cell)) < required_stocklevel:
#            print(f"Stock of {cell} is low, please reorder")
#            stock_to_check.append(cell)
#    else: 
#        print(f"data for {cell} is blank, please check database")

#2.1.2 Method 2
#low_stock = df_data[df_data['Stock levels']<required_stocklevel]
#print(low_stock.head())

def check_low_stock(table, stock_column, required_stocklevel = 20):
    low_stock = table[stock_column]<=required_stocklevel
    return table[low_stock]

#2 define priority stocks that need assessment first
#for cell2 in df_data['Number of products sold']:
#    for cell3 in stock_to_check:
#        if cell2 == cell3 and cell3>500:
#            print(f"Stock of {cell2} is to check in high priority")
# Or use Pandas condition:
#priority = df_data[(df_data['Stock levels']<required_stocklevel) & (df_data['Number of products sold']>500)]
#print(priority[['SKU', 'Stock levels', 'Number of products sold']].head())

def priority_stock(table, stock_column, productsold_column, required_stocklevel = 20):
    priority = table[(table[stock_column]<required_stocklevel) & (table[productsold_column] > 500)]
    return priority

#3 classify stock into categories depending on the Stock levels
#def classify_stock(stock):
#    if pd.notna(stock):
#        if stock<5:
#            return "critical"
#        elif stock>40:
#            return "overstock"
#        else:
#            return "normal"
#classify_stock(df_data[(df_data['SKU'] == 'SKU5')])
#status = classify_stock(3) 
#print(status)

#df_data['Stock status'] = df_data['Stock levels'].apply(classify_stock)
#print(df_data[['SKU', 'Stock levels', 'Stock status']])

def classify_stock(stock):
    if pd.notna(stock):
        if stock<5:
            return "critical"
        elif stock>40:
            return "overstock"
        else:
            return "normal"
    else:
#        print("Missing stock/unknown")
#"unknown" is a string (str)—a piece of text
        return unknown

#4 Combine revenue into one total
#print(f"\nCombine revenue into one total".upper())
#revenue_values = df_data['Revenue generated'].dropna().tolist()
#total = functools.reduce(lambda a, x:a+x, revenue_values, 0)
#print(total)

def total_revenue(table, revenue_column):
#Method 1 - using sum()
#    total = table[revenue_column].dropna().sum()
#Method 2 - using reduce()
    revenue_value = table[revenue_column].dropna().tolist()
    total = functools.reduce(lambda x, a: x+a, revenue_value, 0)
    return total

#5 Broadcast in Numpy
#5.1 Method 1
#df_data_array = np.arange(len(df_data['Stock levels'])).reshape(len(df_data['Stock levels']), 1)

#5.2 Method 2
#selected_columns = ['Revenue generated', 'Shipping costs', 'Defect rates']

#numeric_data = df_data[selected_columns].apply(pd.to_numeric)
#numeric_numpy_data = numeric_data.to_numpy()
#print(f"Shape: {np.shape(numeric_numpy_data)}")
#print(f"Dimentions: {numeric_numpy_data.ndim}")
#print(f"Data type: {numeric_numpy_data.dtype}")
#print(f"print 5 rows: {numeric_numpy_data[0:5]}")

#for example caluculating profit = revenue-(no. sold * manufacture costs)
def broadcast(table):
# Method 1
#    a = np.arange(len(table['Revenue generated'])).reshape(len(table['Revenue generated']), 1)

#do the same for the other columns
#    b = np.arange(len(table['Number of products sold'])).reshape(len(table['Number of products sold']), 1)
#    c = np.arange(len(table['Manufacturing costs'])).reshape(len(table['Manufacturing costs']), 1)
#calculate using operators
#    d_profit = table['profit'] = a - b*c
#    return d_profit 

# Method 2
#Broadcasting e.g mean etc.
#for now do the same broadcast as Method 1
#check finite
    selected_columns = ['Revenue generated', 'Number of products sold', 'Manufacturing costs']
    a3 = table[selected_columns].to_numpy()
    finite_across = np.isfinite(a3).all(axis=1)
    finite_across_data = a3[finite_across]
    d_profit = finite_across_data[:,0] - (finite_across_data[:,1]*finite_across_data[:,2])
    return d_profit
    
#6 Calculate shipping costs
def shipping_costs(table):
    selected_columns = ['SKU', 'Shipping costs']
    a = table[selected_columns].groupby('SKU').mean()
    return a

#7 Warehouse scenario, suppose 1 box holds 12 units
def boxes_required(table, quantity_column, box_unit=12):
    table['Boxes required'] = table[quantity_column].apply(lambda x:math.ceil(x/box_unit))
    return table['Boxes required']

#8 Find products with stocks below 20
def below_20_stock(table, stock_column):
    below_20 = table[table[stock_column]<20]
    return below_20

#9 Define restock condition
def restock(below_20, quantity_column, restock_to=50):
    below_20_copy = below_20.copy()
    below_20_copy['Quantity to order'] = below_20_copy[quantity_column].apply(lambda x: restock_to-x)
    return below_20_copy[['SKU', 'Quantity to order']]

def check_material_balance(unified_monthly):
#3.5 check if open, received, issued and closing quantity balance
#3.5.1 target the numeric data (to perform vector addition/subtract)
    columns_to_check = ['Opening quantity', 'Received quantity', 'Issued quantity', 'Closing quantity']
    df_cols = unified_monthly[columns_to_check]
    df_cols = df_cols.to_numpy()
    df_cols = df_cols.astype(float)
    finite = np.isfinite(df_cols)
    finite_across = finite.all(axis=1)
    sliced_finite_df = unified_monthly[finite_across]

#3.5.2 perform vector addition
    sliced_finite_df['Variance'] = sliced_finite_df['Opening quantity'] + sliced_finite_df['Received quantity'] - sliced_finite_df['Issued quantity'] - sliced_finite_df['Closing quantity']
    print(sliced_finite_df['Variance'].head())
    sliced_finite_df['Expected closing'] = sliced_finite_df['Opening quantity'] + sliced_finite_df['Received quantity'] - sliced_finite_df['Issued quantity']
    print(sliced_finite_df['Expected closing'].head())

#3.5.3 identify the 0's in stocks' sliced_finitedf['Variance'] using vectorize boolean
    required_variance = 0
    matched_balance = sliced_finite_df[sliced_finite_df['Variance'] == required_variance]

#3.5.4 percentage of unmatched balance material records
    unmatched_balance = sliced_finite_df[sliced_finite_df['Variance'] != required_variance]
    unmatched_percentage = len(unmatched_balance)/len(sliced_finite_df)
    print(f"Percentage of unmatched balance: {unmatched_percentage}")
    print(f"Percentage of zero-issue stock: {1-unmatched_percentage}")

    return matched_balance


