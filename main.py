from src.config import RAW_CSV
from src.extract import read_fact_csv
from src.transform import build_dim_supplier
from src.transform import build_dim_logistics
from src.transform import build_dim_product
from src.transform import attach_keys
from src.config import DB
from src.load import create_db
from src.validate import check_relationship
from src.validate import validate_warehouse
from src.analytics import check_low_stock
from src.analytics import priority_stock
from src.analytics import classify_stock
from src.analytics import total_revenue
from src.analytics import broadcast
from src.analytics import shipping_costs
from src.analytics import boxes_required
from src.log import log_analysis
from src.analytics import below_20_stock
from src.transform import options
from src.analytics import restock
from src.optimize import optimize
from src.config import MATERIAL_AUGUST, MATERIAL_OCTOBER
from src.extract import extract_materials
from src.analytics import check_material_balance
from src.analytics import reorder_basedon_targetstock

#Which materials are likely to run short, which vendor can cover the gap,...
# and how much cash and extra stock would that order create?

def main():
    print(f"Printing the first 5 rows of {RAW_CSV}")

    raw = read_fact_csv(RAW_CSV)
    suppliers = build_dim_supplier(raw)
    print(f"Raw rows: {len(raw)}")
    print(f"Supplier-location combinations: {len(suppliers)}")
    print(suppliers.head())

    logistics = build_dim_logistics(raw)
    print(f"Raw rows: {len(raw)}")
    print(f"Shipping carriers-Transportation modes-Routes combinations: {len(logistics)}")
    print(logistics.head())

    products = build_dim_product(raw)
    print(f"Raw rows: {len(raw)}")
    print(f"SKU records: {len(products)}")
    print(products.head())

    merge1 = attach_keys(raw, suppliers, ['Supplier name', 'Location'])
    merge2 = attach_keys(merge1, logistics, ['Shipping carriers', 'Transportation modes', 'Routes'])
    merge2 = merge2.drop(columns=['Supplier name', 'Location', 'Shipping carriers', 'Transportation modes', 'Routes', 'Product type', 'Price'])

    unified_monthly_main = extract_materials(MATERIAL_AUGUST, MATERIAL_OCTOBER)
    print(unified_monthly_main.head())

    matched_balance_main = check_material_balance(unified_monthly_main)

#keepingg going here

    create_db(products, logistics, suppliers, merge2)
    
    validate_warehouse(DB)

    low_stock = check_low_stock(merge2, 'Stock levels')
    print(low_stock.head())

    priority = priority_stock(merge2, 'Stock levels', 'Number of products sold')
    print(priority.head())

    classify = merge2['Stock levels'].apply(classify_stock)
    print(classify.head())

    total = total_revenue(merge2, 'Revenue generated')
    print(total)

    profit = broadcast(merge2)
    print(profit)

    shipping = shipping_costs(merge2)
    print(shipping.head())

    boxes = boxes_required(merge2, 'Number of products sold')
    print(boxes.head())

    low_20 = below_20_stock(merge2, 'Stock levels')
    print(low_20.head())
    
    log_analysis(merge2, total, low_stock)

    options_to_choose = options(products, suppliers, logistics)
    print(options_to_choose.head())

    rstk = restock(low_20, 'Stock levels')
    print(rstk.head()) 

    optiz = optimize(options_to_choose, rstk, budget=10000)
    print(optiz)

    added_reord = reorder_basedon_targetstock(merge2)
    print(added_reord.head())

if __name__ == "__main__":
    main()

