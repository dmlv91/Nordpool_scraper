from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import os
import plivo
from datetime import datetime

class NORD:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')

    def scrape_tab(self, tab):
        times = []
        prices = [[],[]]
        nordpool_data = {
        }
        driver = webdriver.Chrome(options=self.chrome_options,service_log_path=os.path.devnull)
        driver.get(tab)
        for _ in range(1500):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        soup = BeautifulSoup(driver.page_source.encode("utf-8"),'html.parser')
        driver.close()
        datatable = soup.find('table', id="datatable")
        titles = datatable.select('thead tr')
        rows = datatable.select('tbody tr')
        for k in [row.find_all('th')[0:3] for row in titles]:
            for i in k[1:3]:
                pattern = re.compile('<.*?>')  
                date = re.sub(pattern, "",str(i))
                if not date in nordpool_data:
                    nordpool_data.update({date:{}})
        for col in range(0,3):
            i = 0
            for k in [row.find_all('td')[col].get_text(strip=True) for row in rows[0:25]]:
                    if col == 0:
                        ts = k.replace("\xa0","")
                        if not ts in times:
                            times.append(ts)
                    else:
                        if col == 2:
                            i = 1
                        if k == "":
                            break
                        if not k in prices:
                            prices[i].append(k)
        prices[0].insert(0,prices[1][-1])
        prices[0].pop(-1)
        j = 0
        for date in nordpool_data: 
            for i in range(0,24):
                if not times[i] in nordpool_data[date]:
                    print(date,"----->",times[i],"------>",prices[j][i])
                    if not prices[j][i] == '-':
                        price = float(prices[j][i].replace(",","."))/1000
                        price = round(price*1.21,4)
                        nordpool_data[date].update({times[i]:price})
            j = 1
        return self.get_cheap_hours(nordpool_data)
    
    def get_cheap_hours(self,nordpool_data):
        cheap = []
        # date = datetime.now().strftime('%d-%m-%Y')
        for date in nordpool_data:
            for time in nordpool_data[date]:
                if type(nordpool_data[date][time]) == float:
                    if nordpool_data[date][time] <= 0.05:
                        cheap.append(True)
                        print(date + " @ " + time + " -----> BURN ELECTRICITY!!!! PRICE FOR ONE KW---> " + str(nordpool_data[date][time]))
        if len(cheap) == 0:
            print("NO CHEAP HOURS TODAY!")
        print(nordpool_data)
                        
        return

    def get_daily_prices_info(self):
        return self.scrape_tab("https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/LV/Hourly/?view=table")
    


scrape = NORD()
data = scrape.get_daily_prices_info()