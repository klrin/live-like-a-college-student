
import json, pulp, pprint
import numpy as np
from convinience import *

colorlogs()

logging.notice("Starting...")
pprinter = pprint.PrettyPrinter()

with open("inventories/save-1682397599.3847358.json") as f:
    productdata = json.load(f)
with open("assets/constraints.json") as f:
    constraints = json.load(f)

upcs = [p[1] for p in productdata]

prob = pulp.LpProblem("Grocery_Minimizing", pulp.LpMinimize)

aspect_totals = {
    "cost":[]
}
ids = list(set([get_nutrient_id(str(c[0])) for c in constraints if len(c[0]) > 3] + [str(c[0]) for c in constraints if len(c[0]) == 3]))

for product in productdata: # for each product
    ingredientvar = pulp.LpVariable(product[1], 0, cat=pulp.LpInteger) # create a variable to represent it's quantity
    aspect_totals["cost"].append(ingredientvar*float(product[2])) # add it's cost to the totals
    for varid in ids: # for each nutrient in the constraints
        if varid in product[-1].keys(): # if there is data about this product
            if varid in aspect_totals.keys(): # if there is already a list for it
                aspect_totals[varid].append(ingredientvar*float(product[-1][varid]))
            else:
                aspect_totals[varid] = [ingredientvar*float(product[-1][varid])]

prob += pulp.lpSum(aspect_totals["cost"])
days = 360 # edit this value to change how many days you are optimizing for
for c in constraints:
    if len(c[0]) > 3:
        id = get_nutrient_id(str(c[0]))
    else:
        id = str(c[0])
    if c[1] == "max":
        logging.info(f"{get_nutrient_id(id, reverse=True)} must be less than {c[2]}")
        prob += pulp.lpSum(aspect_totals[id]) <= c[2]*days # edit this valu
    elif c[1] == "min":
        logging.info(f"{get_nutrient_id(id, reverse=True)} must be more than {c[2]}")
        prob += pulp.lpSum(aspect_totals[id]) >= c[2]*days
    else:
        logging.debug(c[1])
logging.notice("Solving...")
prob.solve(pulp.apis.PULP_CBC_CMD(msg=False))
logging.success(f"Solved! Status is {pulp.LpStatus[prob.status]}.")
for v in prob.variables():
    if v.varValue > 0:
        p = productdata[upcs.index(str(v.name))]
        logging.notice(f"{p[0]} ({p[1]}) ${p[2]} x{v.varValue} {p[-2]} serv/pack")
        for k in p[-1].keys():
            if k in ids:
                logging.info(f"{get_nutrient_id(k, reverse=True)}: {p[-1][k]}")

logging.section("DONE")









