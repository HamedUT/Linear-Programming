import gurobipy as gp
import pandas as pd


#Parameters
ordering_cost = 3 
selling_price = 10
scrap_value = 1


#Read time serie data. Access data with column name and time period. Example: data["Heat demand"][10] --> heat demand in period 10
data = pd.read_csv("small_case.csv", sep=";",index_col=0, header=0)

scenarios = range(data.shape[0])


# Create a new model
model = gp.Model("NewsVendor")

# Create variables
x = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x")  #Ordering quantity
y = model.addVars(scenarios, vtype=gp.GRB.CONTINUOUS, name="y")  #Selling quantity


# Set objective
model.setObjective(-1.0*ordering_cost*x + sum(data["Probability"][s]*(selling_price*y[s]+scrap_value*(x-y[s])) for s in scenarios), gp.GRB.MAXIMIZE)

for s in scenarios:
    model.addConstr(y[s] <= x, "LimitByOrderedAmount%s"%s)
    model.addConstr(y[s] <= data["Demand"][s], "LimitByDemand%s" %s)


# Optimize model
model.optimize()

model.write("model.lp")

status = model.Status
if status == gp.GRB.OPTIMAL:
    print("Optimal solution found")
    print('Objective value: %g' % model.ObjVal)
    
    for s in scenarios:
        print('X %0.4f Y %0.4f Scrap %0.4f' % (x.X, y[s].X, (x.X - y[s].X)))

    

    
    
    

elif status == gp.GRB.INFEASIBLE:
    #If model is infeasible calculate and print irreducible inconsistent subsystem (IIS) to find out which constraint lead to infeasibility
    model.computeIIS()
    model.write("iis.ilp")

    


