import pulp
import pandas as pd

def optimize(dim_supplier_withSKU, restock_table, budget):
#both systems take an explicitly defined model and use algorithms to...
#... determine what satisfies its rules
#OWL and description logics are closely related, but not interchangeable names: OWL is an ontology...
#... language; description logics provide the logical foundations for important OWL variants
#Here a ValueError establishes only that the status was not "Optimal". It does not...
#... establish that it was "Infeasible"
#An ontology reasoner asks whether its definitions and axioms permit something to...
#... exist—for example, whether a class could have any members. Our purchasing model asks...
#... whether quantities and supplier choices can satisfy all our constraints, and then seeks...
#... the cheapest valid plan. Both depend on explicit representations and systematic reasoning, ...
#... but they use different mathematical formalisms. The ontology reasoner checks logical...
#... consequences and satisfiability; the optimization solver searches for a feasible plan and...
# proves its optimality when possible
#For our project, feasibility is the closest parallel to the book’s satisfiability;...
#... minimizing cost is the additional task
#Direct costs: Purchasing materials and paying for their delivery
#Variable costs: 	Purchase costs increase with the quantity ordered. Your holding-cost...
#... term also increases with quantity
#Fixed costs: Your shipping term models a fixed charge whenever a particular supplier option...
#... is selected, regardless of quantity
#Opportunity costs: Money committed to one SKU cannot be used for another purchase or...
#... activity. Your current model does not explicitly value that forgone alternative
#direct, indirect, tangible, and intangible benefits: 
#   Avoiding lost sales from stockouts.
#   Avoiding production stoppages caused by missing materials.
#   Reducing emergency purchasing and delivery charges.
#   Improving customer service and delivery reliability.
#P1
    restock_dict = {}
    for SKU, qty in zip(restock_table['SKU'], restock_table['Quantity to order']):
        restock_dict[SKU] = qty
    restock_dict2 = pd.DataFrame([restock_dict])
    restock_dict2 = restock_dict2.T
    restock_dict2.columns = ['Quantity to order']
    restock_dict2.index.rename = 'SKU'
#matching/filtering step
# Method 1
#    to_order = []
#    for SKU in restock_table['SKU']:
#print(my_series.values)
#        if SKU in dim_supplier_withSKU['SKU'].values
#            to_order.append(SKU)
#To transition from your earlier set intersection (&) pattern to filtering your...
#...supplier table with .isin(demand_map.keys()), you shift from comparing... 
#...matching rows inside a single table to checking whether each... 
#...supplier row's SKU exists in your external restock dictionary
# Method 2
    to_order = set(restock_dict) & set(dim_supplier_withSKU['SKU'])
#this is the same as the step converting DataFrame into dictionary above
#    id_movie=average_rating.loc[average_rating.rating==5.0].index
#dim_supplier_withSKU.isin(to_order) checks every cell, producing a two-dimensional Boolean...
#... DataFrame. .loc[...] needs a one-dimensional Boolean mask to select rows
#SKU and isin in the wrong order
#    a2 = dim_supplier_withSKU.isin.SKU(to_order)
    a2 = dim_supplier_withSKU['SKU'].isin(to_order)
    dim_supplier_withSKU = dim_supplier_withSKU[a2]
#    dim_supplier_withSKU.loc[dim_supplier_withSKU.SKU.isin(to_order)].head()
#save to a variable
#    filtered_supplier = dim_supplier_withSKU.loc[dim_supplier_withSKU.SKU.isin(to_order)]
    filtered_supplier = dim_supplier_withSKU

#The next step is P2: create the optimization problem that will choose among your...
#... filtered supplier options.
#P2 
#    minimize_order_problem = pulp.problem()
#After the comma on line 70, put pulp.LpMinimize (or pulp.LpMaximize, depending on your goal)
#    minimize_order_problem = pulp.LpProblem("Order", pulp.Lp.Maximize)
#Change it to pulp.LpMinimize (no dot between Lp and Minimize):
#    minimize_order_problem = pulp.LpProblem("Order", pulp.LpMaximize)
#On line 73, change LpMaximize to LpMinimize, because your objective is to minimize...
#... purchasing cost
    minimize_order_problem = pulp.LpProblem("Order", pulp.LpMinimize)
    
#P3 
#Step 2 creates the model. Step 3 defines the decisions that model can make
    order_qty_choices = {}
    user_supply_switches = {}
    for index, row_ in filtered_supplier.iterrows():
#Pulp 2.0
#        order_qty_choices[index] = pulp.LpVariable(f"order_qty{index}", lowBound=0, cat="Integer")
#Pulp 4.0
        order_qty_choices[index] = to_minimize_prob.add_variable(f"order_qty{index}", lowBound=0, cat="Integer")
#Pulp 2.0        
#        user_supply_switches[index] = pulp.LpVariable(f"supply_switch{index}", lowBound=0, cat="Binary")
#Pulp 4.0
        user_supply_switches[index] = to_minimize_prob.add_variable(f"supply_switch{index}", lowBound=0, cat="Binary")

#P4
    per_item_cost = {}
    for index, row_ in filtered_supplier.iterrows():
        per_item_cost[index] = (row_['Per-unit purchase cost'] + row_.get('Holding cost', 0))*order_qty_choices[index] + user_supply_switches[index]*row_['Shipping cost']    
#    print(my_series.values)
    per_item = pulp.lpSum(per_item_cost.values())
#Keeping the cost objective active
    to_minimize_prob += per_item
    
#P5
#for key, value in person.items():
#    print(key, "→", value)
    for key, value in restock_dict.items():
#        if filtered_supplier['SKU'] == key
#if statement is the right logic, just not used appropriately structure-wise -> fixed:
        if key not in list(filtered_supplier['SKU']):
            continue
        else:
#In #P3, you named your solver variables after row numbers (0, 1, 2), not SKU
            filtered_for_restock = filtered_supplier[filtered_supplier['SKU']==key].index
# Method 2
#        filtered_for_restock = filtered_supplier['SKU'] == key
#if write the folliwng line of code it would be error because filtered_for_restock...
#... is already a DataFrame
#        filtered_for_restock = filtered_supplier[filtered_for_restock]
#instead
#        filtered_for_restock = filtered_supplier['SKU'].index 
#this 1 next line is done by exactly the sum() statement below 
#        to_minimize_prob += 'to order' = restock_dict[value]
#        sum(scores.values())
            to_minimize_prob += value <= sum(
        order_qty_choices[idx_to_reorder]
        for idx_to_reorder in filtered_for_restock
#            revenue = product[sales_id] * quantity
        )
#connect sum(...) directly to <= value inside to_minimize_prob +=
    to_minimize_prob += per_item <=budget
    for index, row_ in filtered_supplier.iterrows():
#use row_['Max capacity'] instead of just the reorder qty topup        
#        max_to_order = restock_dict[row_['SKU']]
        max_to_order = row_['Max capacity']  
        to_minimize_prob += max_to_order*user_supply_switches[index] >= order_qty_choices[index]          
        min_to_order = row_['Minimum order quantity']
        to_minimize_prob += min_to_order*user_supply_switches[index] <= order_qty_choices[index]     
    
#P6
    solve_stats = to_minimize_prob.solve()

#In PuLP, solve() updates the .status attribute on your problem variable (to_minimize_prob),...
#... and pulp.LpStatus[...] translates that number into a readable word like "Optimal" or...
#... "Infeasible"
#following line needs .status after to_minimize_prob
#PuLP 4.0+ removed prob.status from LpProblem and moved it to the LpSolveStats object...
#... returned by prob.solve()
    print(f"Status code for our problem.solve() is {solve_stats.status}, which means ")
    stts =solve_stats.status.name
    print(stts)

    if stts != "Optimal":
#        print("No optimum buying option available")
        raise ValueError(f"No optimum buying option available, refer to issue: {stts}")

    rsult = {}
    for index2, value2 in order_qty_choices.items():
        rsult[index2] = value2.varValue
    filtered_supplier2 = filtered_supplier.copy()
#string_lengths = map(len, ["dog", "cat", "zebra", "turtle"])
#    mask_unified_monthly = map(lambda x, y, z, u: pd.notna(x) and pd.notna(y) and pd.notna(z) and pd.notna(u), unified_monthly["Opening quantity"],
#                                    unified_monthly["Received quantity"], unified_monthly["Issued quantity"], unified_monthly["Closing quantity"])
# Step 1: Grab the row labels (NO parentheses here)
#    a = filtered_supplier2.index
#index is an attribute just like varValue
# Step 2: Run the .map() action on 'a' using a dot
#    b = a.map(rsult)
    a = filtered_supplier2.index
    filtered_supplier2['Optimized order'] = a.map(rsult)
#    filtered_supplier2['Optimized order'] = filtered_supplier2.map(rsult)
    return filtered_supplier2
