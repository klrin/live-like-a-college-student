

import asyncio, pprint, json, time, logging
from safeway import Products
from pint import UnitRegistry
from convinience import *
import numpy as np

colorlogs()
sproducts = Products()
ureg = UnitRegistry(system='cgs')
Q_ = ureg.Quantity
pprinter = pprint.PrettyPrinter()

with open("assets/nutrition-min-4.22-good.json") as f:
    nutritions = json.load(f)
upcs = [row[0] for row in nutritions]
gooditems = []
faileditems = []

async def main():
    logging.info("loaded; starting downloads")
    async for p in sproducts.main():
        if p[1] in upcs:
            nrow = nutritions[upcs.index(p[1])]


            servnum = get_num(nrow[-1])
            servunit = get_units(nrow[-1])
            if servnum and servunit:
                servnum = float(servnum)
                serv = Q_(servnum, servunit).to_base_units()
                if serv.m < 10:
                    faileditems.append(p)
                    continue
            else:
                faileditems.append(p)
                continue

            tests = []

            if type(nrow[-2]) == str and len(nrow[-2]) > 3:
                tests.append(nrow[-2].split("/")[-1])
            if len(p[0].split("-")) > 1:
                tests.append(p[0].split("-")[-1])
            if len(tests) < 2: # backup thing from prices
                tests.append(f"{float(p[-3])/float(p[-2])} {p[-1]}")
            
            nums = []
            log = []

            for i in range(len(tests)):
                blurb = tests[i]
                unit = get_units(blurb)
                num = get_num(blurb)
                if unit and num:
                    num = float(num)
                    log.append([num, unit])
                    q = Q_(num, unit).to_base_units()
                    if q.u == serv.u:
                        nums.append(q.m)

            if len(nums) == 0 or np.std(nums)/np.mean(nums)>.2:
                faileditems.append(p)
                continue

            scale = nums[0]/serv.m
            p.append(str(round(scale)))
            for key in nrow[1]:
                nval = round(float(nrow[1][key])*scale, 1)
                if nval > 20000:
                    continue
                nrow[1][key] = nval
            p.append(nrow[1])

            gooditems.append(p)
            print(f"done with {len(gooditems)} total, just now: {p[0][0:60]}", end=" "*(100-len(p[0]))+"\r")
    print()

asyncio.run(main())

logging.notice(f"{len(gooditems)} successfully calculated, {len(faileditems)} failed; {round(len(gooditems)/(len(gooditems)+len(faileditems))*100)}% successfull")

with open("inventories/save-"+str(time.time())+".json", "w") as f:
    json.dump(gooditems, f)

logging.success("Saved!")

        

