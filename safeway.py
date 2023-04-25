
import json, asyncio, aiohttp, logging
from convinience import *


class Products:
    def __init__(self) -> None:
        with open("assets/catagory_ids.txt") as f:
            self.catagories = f.readlines()
                    # edit below store id to select your safeway store to index. see the safeway website to find your store id (which is a param in requests made by the web app)
    async def get_products_from_search(self, sess, storeid=1234, start=0, search_term="eggs",len=5): # only works in from US ip, it seems
        url = f"https://www.safeway.com/abs/pub/xapi/pgmsearch/v1/search/products?request-id=2601682197227490786&url=f&pageurl=f&pagename=search&rows={len}&start={start}&search-type=keyword&storeid={storeid}&search-uid=&q={search_term}&dvid=web-4.1search"
        async with sess.get(url, headers={"Ocp-Apim-Subscription-Key":"5e790236c84e46338f4290aa1050cdd4"}) as rsp:
            return rsp.status, await rsp.text()
                        # edit below store id to select your safeway store to index
    async def get_products_from_aisle(self, sess, storeid=1234, start=0, cat_id="1_1_1",len=5): # only works in from US ip, it seems
        url = f"https://www.safeway.com/abs/pub/xapi/v1/aisles/products?request-id=1&url=f&pageurl=f&pagename=aisles&rows={len}&start={start}&search-type=category&storeid={storeid}&category-id={cat_id}"
        async with sess.get(url, headers={"Ocp-Apim-Subscription-Key":"e914eec9448c4d5eb672debf5011cf8f"}) as rsp:
            return url, rsp.status, await rsp.text()

    async def getcat(self, cat, sess):
        goodinfo = []
        done = 0
        found = 999
        catname = ""
        while True:
            url, status, content = await self.get_products_from_aisle(sess, cat_id=cat, len=min(100, found-done), start=done)
            c = json.loads(content)
            if catname == "":
                catname = c["response"]["docs"][0]["aisleName"]
            if found == 999:
                found = c["response"]["numFound"]
            for p in c["response"]["docs"]:
                if bool(int(p["inventoryAvailable"])) and p["name"] not in [i[0] for i in goodinfo]:
                    goodinfo.append([p["name"], add_check_digit(p["upc"]), float(p["price"]), p["pricePer"], p["unitQuantity"]])
            done += len(c["response"]["docs"])
            
            if status not in [200, 206]:
                logging.warning(f"Recieved {status} for {url}")
            if done >= found:
                break
        return cat, catname, goodinfo
        
    async def main(self):
        connector = aiohttp.TCPConnector(limit=5)
        timeout = aiohttp.ClientTimeout(total=5)
        masterlist = []
        chunk = 5
        redo = False
        iterations = 0
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as sess:
            while len(self.catagories) > 0:
                if iterations > 10:
                    logging.warning(f"{self.catagories} were not completed, ending...")
                    break
                if len(self.catagories) < 10:
                    iterations += 1
                if len(self.catagories) < chunk:
                    tasks = [asyncio.create_task(self.getcat(i, sess)) for i in self.catagories]
                else:
                    tasks = [asyncio.create_task(self.getcat(i, sess)) for i in self.catagories[0:chunk-1]]
                responses = await asyncio.gather(*tasks[0:chunk], return_exceptions=True)
                for r in responses:
                    if type(r) == tuple:
                        self.catagories.remove(r[0])
                        for p in r[2]:
                            yield p
                    else:
                        redo = True
                if redo:
                    change_ip()
                    redo = False
