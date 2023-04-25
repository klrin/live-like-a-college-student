import json
from thefuzz import fuzz
from thefuzz import process

with open("blabla.json") as f:
    data = json.load(f)

allproducts = []

for key in data.keys():
    allproducts +=  [row for row in data[key][1:-1]]

names = [row[0] for row in allproducts]




while True:
    search = input("> ")
    results = process.extract(search, names, limit=25)
    found = False
    for i in results:
        price = allproducts[names.index(i[0])][2]
        if int(i[1])>=90:
            print(f"{i[1]}%, ${price}: {i[0]}")
            found = True
    if found == False:
        print("No close matches found.")