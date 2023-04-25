import ijson, pprint, time # searches 10K items per second
import json

print("running...")
pprinter = pprint.PrettyPrinter()
filename = "archive/FoodData_Central_branded_food_json_2022-10-28.json"

tocode = {
    'fat':204,
    'saturatedFat':606,
    'transFat':605,
    'cholesterol':601,
    'sodium':307,
    'carbohydrates':205,
    'fiber':291,
    'sugars':269,
    'protein':203,
    'calcium':301,
    'iron':303,
    'calories':208,
    'potassium':306,
    'addedSugar':539,
    'vitaminD':324
}

notot = 0
noserv = 0
products = []
with open(filename, 'r') as f:
    objects = ijson.items(f, 'BrandedFoods.item')
    for i in objects: 
        nutridict = {}
        for key in i["labelNutrients"].keys():
            nutridict[tocode[key]] = str(i["labelNutrients"][key]["value"])
        pl = [i['gtinUpc'], nutridict]
        if "packageWeight" in i.keys():
            pl.append(i["packageWeight"])
        else:
            notot += 1
            pl.append(0)
        if "servingSize" in i.keys() and 'servingSizeUnit' in i.keys():
            pl.append(str(i['servingSize']) + i['servingSizeUnit'])
        else:
            noserv += 1
            pl.append(0)
        products.append(pl)

with open("nutrition-min-4.22-good.json", "w") as f:
    json.dump(products, f)

print(f"{notot} without any package weight, and {noserv} without a serving size")