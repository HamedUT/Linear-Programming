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

exp_demand = [sum(data["Probability"][s]*data["Demand%i"%n][s] for s in scenarios) for n in newsvendors]

# Create a new model
model = gp.Model("NewsVendor")

# Create variables
x = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x")  #Ordering quantity
y = model.addVars(newsvendors, vtype=gp.GRB.CONTINUOUS, name="y")  #Selling quantity


# Set objective
model.setObjective(-1.0*ordering_cost*x + (sum(selling_price*y[n] for n in newsvendors) +scrap_value*(x-sum(y[n] for n in newsvendors))), gp.GRB.MAXIMIZE)

for n in newsvendors:
    model.addConstr(sum(y[n] for n in newsvendors) <= x, "LimitByOrderedAmount%s")
    model.addConstr(y[n] <= exp_demand[n], "LimitByDemand%s" )


# Optimize model
model.optimize()

model.write("model.lp")

status = model.Status
if status == gp.GRB.OPTIMAL:
    print("Optimal solution found")
    print('Objective value: %g' % model.ObjVal)
    
    print("X %0.4f" % x.X)
    
    

    
    
    

elif status == gp.GRB.INFEASIBLE:
    #If model is infeasible calculate and print irreducible inconsistent subsystem (IIS) to find out which constraint lead to infeasibility
    model.computeIIS()
    model.write("iis.ilp")

    


