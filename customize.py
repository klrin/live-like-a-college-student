"""
Run the userscript in the browser to output a parseable list of your daily requirements. Run it after going to this site and paste the results into custom.json
https://www.nal.usda.gov/human-nutrition-and-food-safety/dri-calculator

// ==UserScript==
// @name        Extract Nutrients - usda.gov
// @namespace   Violentmonkey Scripts
// @match       https://www.nal.usda.gov/human-nutrition-and-food-safety/dri-calculator/results
// @grant       none
// @version     1.0
// @author      klrin
// @description 4/23/2023, 8:18:39 PM
// ==/UserScript==

nutritions = {}
rows = Array.from(document.querySelectorAll("tr *"))
for (i=0;i<rows.length; i++) {
  h = rows[i].headers
  if (h && h.length > 0) { // the header is good
    if (h == "eer") {
      nutritions["energy"] = rows[i].innerText
    } else if (h.split(" ").includes("macro-recommended-intake")) {
      nutritions[h.split(" ")[0]] = rows[i].innerText
    } else if (h.split(" ").includes("mineral-recommended-intake") || h.split(" ").includes("vitamin-recommended-intake")) {
      nutritions[h.split(" ")[0] + " min"] = rows[i].innerText
    } else if (h.split(" ").includes("mineral-tolerable-intake") || h.split(" ").includes("vitamin-tolerable-intake")) {
      nutritions[h.split(" ")[0] + " max"] = rows[i].innerText
    } else {
      console.log(h)
    }
  }
}
console.log(nutritions)
"""

import json, re, pprint
from convinience import *

pprinter = pprint.PrettyPrinter()

template = [
  ["saturated fat", "max", 20],
  ["trans fat", "max", 0],
  ["cholesterol", "max", 300],
  ["sodium", "max", 2300],
  ["added sugar", "max", 50],
  ["sodium", "max", 2300]

]

with open("assets/custom.json") as f:
    custom = json.load(f)

def appendminmax(id, mmax, quantitystr):

    q = get_num(quantitystr)
    if q:
        template.append([id, mmax, q, get_nutrient_id(id, reverse=True)])

for key in custom.keys():
    nutrient_id = get_nutrient_id(key)
    if nutrient_id:
        if (mmax := key.split(" ")[-1]) in ["min", "max"]:
            appendminmax(nutrient_id, mmax, custom[key])
            continue
        elif len(spl := custom[key].split("-")) == 2:
            appendminmax(nutrient_id, "min", spl[0])
            appendminmax(nutrient_id, "max", spl[1])
            continue
        else:
          appendminmax(nutrient_id, "min", custom[key])
          continue

with open("assets/constraints.json", 'r+') as f:
    text = f.read()
    text = json.dumps(template, indent=3)
    f.seek(0)
    f.write(text)
    f.truncate()




















