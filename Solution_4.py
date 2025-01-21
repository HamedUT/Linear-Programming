import gurobipy as gp
import pandas as pd


#Parameters
ordering_cost = 3 
selling_price = 10
scrap_value = 1


#Read input data
data = pd.read_csv("large_case_ext.csv", sep=";",index_col=0, header=0)

scenarios = range(data.shape[0])
newsvendors = range(5)

# Create a new model
model = gp.Model("NewsVendor")

# Create variables
x = model.addVars(newsvendors, vtype=gp.GRB.CONTINUOUS, name="x")  #Ordering quantity
y = model.addVars(newsvendors, scenarios, vtype=gp.GRB.CONTINUOUS, name="y")  #Selling quantity

# fixed = [9, 15, 11, 14, 10]
# for n in newsvendors:
#         model.addConstr(x[n]==fixed[n])

# Set objective
model.setObjective(sum(-1.0*ordering_cost*x[n] + sum(data["Probability"][s]*(selling_price*y[n,s]+scrap_value*(x[n]-y[n,s])) for s in scenarios) for n in newsvendors), gp.GRB.MAXIMIZE)

for n in newsvendors:
    for s in scenarios:
        model.addConstr(y[n,s] <= x[n], "LimitByOrderedAmount%s"%s)
        model.addConstr(y[n,s] <= data["Demand%i"%n][s], "LimitByDemand%s" %s)


# Optimize model
model.optimize()

model.write("model.lp")

status = model.Status
if status == gp.GRB.OPTIMAL:
    print("Optimal solution found")
    print('Objective value: %g' % model.ObjVal)
    
    for n in newsvendors:
      
        print('N%i: X %0.4f' % (n, x[n].X))

    

    
    
    

elif status == gp.GRB.INFEASIBLE:
    #If model is infeasible calculate and print irreducible inconsistent subsystem (IIS) to find out which constraint lead to infeasibility
    model.computeIIS()
    model.write("iis.ilp")

    


