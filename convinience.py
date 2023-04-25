
import re, logging, time, json, os, subprocess, random, requests, coloredlogs

def get_nutrient_id(inp, reverse=False):
    if type(inp) != str:
        return False
    key = {
        "204": ["total fat", 'fat'],
        "606": ["saturated fat", 'saturatedFat', "saturated-fatty-acids"], # bad
        "605": ["trans fat", 'transFat', "<em>trans</em>-fatty-acids"], # bad
        "601": ["cholesterol", 'cholesterol', 'dietary-cholesterol'], # bad
        "307": ['sodium'],
        "205": ['carbohydrates', "carbohydrate"],
        "291": ['fiber', "total-fiber"],
        "269": ['sugars'],
        "203": ['protein'],
        "301": ['calcium'],
        "303": ['iron'],
        "208": ['calories', "energy"],
        "306": ['potassium'],
        "539": ["added sugar", 'addedSugar']
    }
    if reverse:
      return key[inp][0]
    cinp = re.sub(r"\(.*\)", "", inp)
    cinp = cinp.strip('0123456789. ').lower().replace(".", "")
    matches = []
    for k in key.keys():
        for p in key[k]:
            regex = f"^{p}|\s{p}"
            if re.search(regex, cinp):
                matches.append([p, k])
    for k in matches:
        if len(k[0]) == max([len(p[0]) for p in matches]):
            return k[1]
    return False

def getip():
        return requests.get('https://ipinfo.io/json').json()["ip"]

def change_ip():
        tooverwrite = False
        with open("assets/protonservers.json") as f:
            protonservers = json.load(f)
        ip1 = getip()
        os.system("protonvpn-cli d")
        tries = 0
        while True:
            line = subprocess.check_output(['nmcli', 'con']).decode("utf-8")
            matches = re.search(r"\s[\w-]{25,}\s+vpn+.*", line)
            if matches != None:
                id = matches[0].strip().split(" ")
                device = id[-1].strip()
                id = id[0]
                if device in ["--"]:
                    break
                else:
                    os.system(f"nmcli con down {id}")
                    tries += 1
                    time.sleep(.1)
            else: break
            if tries > 4: break
        homeip = [] # insert home ip addresses here
        while True:
            server = random.choice(protonservers)
            os.system(f"protonvpn-cli c {server}")
            time.sleep(5)
            ip2 = getip()
            if ip2 != ip1 and ip2 not in homeip:
                break
            else:
                logging.warn("IP unchanged, retrying...")
                protonservers.remove(server)
                tooverwrite = True
        if tooverwrite:
            with open("assets/protonservers.json", "w") as f:
                json.dump(protonservers, f)

def add_check_digit(upc_str):  
        """
        Calculates a final check digit and appends it to a given upc
        """
        # https://www.gs1.org/services/how-calculate-check-digit-manually
        multipliers = "31313131313131313"
        sum = 0
        for i in range(len(upc_str)):
            inx = -(i+1)
            sum += int(upc_str[inx])*int(multipliers[inx])
        sum = sum % 10
        if sum != 0: sum = 10-sum
        upc_str = upc_str + str(sum)
        return upc_str[2:]

def get_units(inp):
    if type(inp) != str:
        return False
    key = {"fluid_ounces":["fl oz", "floz", "fz"],
        "quarts": ["qt", "quart"],
        "mL":["ml"],
        "ounces":["oz", "ounce"],
        "pounds":["lbs", "lb", "pound"],
        "grams":["g"],
        "L":["l", "liter", "litre"],
        "kg":["kg"],
        "pints":["pt"],
        "gallons":["gallon"]
    }
    cinp = re.sub(r"\(.*\)", "", inp)
    cinp = cinp.strip('0123456789. ').lower().replace(".", "")
    for k in key.keys():
        for p in key[k]:
            regex = f"^{p}|\s{p}"
            if re.search(regex, cinp):
                return k
    return False

def get_num(blurb):
    if type(blurb) != str:
        return False
    blurb = blurb.replace(",", "")
    regex = r"\d+\.{0,1}\d*"
    m = re.search(regex, blurb)
    if m:
        return float(m.group(0))
    else:
        return False

def all_same(items):
    return all(x == items[0] for x in items)

def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()
    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))
    # http://stackoverflow.com/q/2183233/2988730
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)
    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

def colorlogs():
    addLoggingLevel('spam', logging.DEBUG - 5)
    addLoggingLevel('verbose', logging.INFO - 1)
    addLoggingLevel('notice', logging.INFO + 1)
    addLoggingLevel('success', logging.INFO + 5)
    addLoggingLevel('section', logging.WARNING + 5)
    addLoggingLevel('end', logging.WARNING + 8)

    coloredlogs.DEFAULT_FIELD_STYLES = {}
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'critical': {'inverse': True, 'color': 'red'}, 
        'debug': {'color': 'green'}, 
        'error': {'color': 'red'}, 
        'info': {"color": 240}, 
        'notice': {'color': 'magenta'}, 
        'spam': {'color': "green", 'faint': True}, 
        'success': {'bold': True, 'color': 'green'}, 
        'verbose': {'color': 'blue'}, 
        'warning': {'color': 'yellow'},
        'section': {'color':'black','background':'white'},
        'end': {'color':'red','background':"yellow"}}

    coloredlogs.install(level="INFO", fmt="%(message)s")