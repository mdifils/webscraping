import streamlit as st
import os, csv
import pandas as pd
from time import sleep
from pyquery import PyQuery
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ImmoWeb:
    Type_of_property_not_checked = ["Garage", "Office", "Business", "Industry", "land", "Tenement", "Other",
                   "New real estate project - Houses", "New real estate project - Apartments"]
    Building_condition_lst = ["Good", "To restore", "To be done up", "As new", "Just renovated", "To renovate"]
    Type_of_sale_lst = ["Include new build", "Include public sales", "Include life annuity sales", "Investment property"]
    Subtype_of_house = ["House", "Apartment block", "Bungalow", "Chalet", "Castle", "Farmhouse", "Country house", "Exceptional property", "Mixed-use building", 
            "Town-house", "Mansion","Villa", "Other properties", "Manor house", "Pavilion"]
    Subtype_of_Apartments = ["Apartment", "Ground floor", "Triplex", "Penthouse", "Kot", "Duplex", "Studio", "Loft", "Service flat"]
    columns = ["Locality", "Type_of_property", "Subtype_of_property", "Price", "Type_of_sale", "Number_of_rooms", "Area", "Kitchen_type",
            "Furnished", "Open_fire", "Terasse", "Garden", "Surface_of_land", "Surface_plot_land", "Number_of_facades", "Swimming_pool",
            "Building_condition"]
    def __init__(self, property_type) -> None:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36 Edg/91.0.864.37"
        self.property_type = property_type
        self.properties_links = []
        # self.properties_info = []
        self.options = webdriver.ChromeOptions()
        self.options.headless = True
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(
            executable_path="chromedriver.exe", 
            options=self.options)

    def property_info_to_csv(self, cls, property_info):
        with open('immoweb.csv', 'a', newline='', encoding='UTF8') as f:
            writer = csv.DictWriter(f, fieldnames=cls.columns)
            if os.stat("immoweb.csv").st_size == 0:
                writer.writeheader()
            writer.writerow(property_info)

    def get_properties_info(self, cls, pages):
        df = pd.DataFrame(columns=cls.columns)
        for page in range(1, pages+1):
            url = f"https://www.immoweb.be/en/search/{self.property_type}/for-sale?countries=BE&page={page}&orderBy=relevance"
            self.driver.get(url)
            html = PyQuery(self.driver.page_source)
            for item in html('a.card__title-link'):
                link = item.get('href')
                print(link)
                self.properties_links.append(link)
                property_info = self.get_property_info(cls, link)
                sleep(2)
                if property_info:
                    print(property_info)
                    df = df.append([property_info], ignore_index=True)
                    self.property_info_to_csv(cls, property_info)
                    sleep(1)
                    print("Done")
                else:
                    print("Skipped")
        return df

    def get_property_info(self, cls, link):
        
        # request the link
        self.driver.get(link)
        # grab the html content
        html = PyQuery(self.driver.page_source)
        
        # grab the locality
        locality = list(html('title'))[0].text[:-10].split(' in')[1].strip()
        # grab the type
        property_type = self.property_type.capitalize()
        # grab the subtype
        subtype = list(html('h1.classified__title'))[0].text.strip().split('for')[0].strip()
        
        # let's focus only on House and Apartment properties
        if (subtype in cls.Subtype_of_house) or (subtype in cls.Subtype_of_Apartments):
            result = {}
            property_details = {}
            result['Locality'] = locality
            result['Type_of_property'] = property_type
            result['Subtype_of_property'] = subtype
            # Standart or default type of sale is None (nothing)
            type_of_sale = None
            # check for type of sale
            for item in html('div.flag-list__item--secondary span'):
                if item.text:
                    type_of_sale = item.text
            result['Type_of_sale'] = type_of_sale
            
            # grab the price
            for item in html('p.classified__price span'):
                price = None
                if item.text and item.text[-1] == '€':
                    price = item.text[:-1]
                result['Price'] = price
            
            # grab the rest of information
            for item in html.items('tr.classified-table__row'):
                item_list = item.text().split('\n')
                name = None
                value = None
                if item_list[0]:
                    name = item_list[0]
                    value = item_list[1]
                    result[name] = value

            if 'Living area' in result:
                result['Area'] = result.pop('Living area')
                result['Area'] = result['Area'].split()[0]
            else:
                result['Area'] = None
            if 'Building condition' in result:
                result['Building_condition'] = result.pop('Building condition')
            else:
                result['Building_condition'] = None
            if 'Number of frontages' in result:
                result['Number_of_facades'] = result.pop('Number of frontages')
            else:
                result['Number_of_facades'] = None
            if 'Kitchen type' in result:
                result['Kitchen_type'] = result.pop('Kitchen type')
            else:
                result['Kitchen_type'] = None

            if 'How many fireplaces?' in result:
                result['Open_fire'] = result.pop('How many fireplaces?')
            else:
                result['Open_fire'] = '0'
            if 'Terasse surface' in result:
                result['Terasse'] = result.pop('Terasse surface')
                result['Terasse'] = result['Terasse'].split()[0]
            else:
                result['Terasse'] = '0'
            if 'Garden surface' in result:
                result['Garden'] = result.pop('Garden surface')
                result['Garden'] = result['Garden'].split()[0]
            else:
                result['Garden'] = '0'
            if 'Swimming pool' in result:
                result['Swimming_pool'] = result.pop('Swimming pool')
                result['Swimming_pool'] = '1'
            else:
                result['Swimming_pool'] = '0'
            if 'Surface of the plot' in result:
                result['Surface_of_land'] = result.pop('Surface of the plot')
                result['Surface_of_land'] = result['Surface_of_land'].split()[0]
            else:
                result['Surface_of_land'] = None
            if 'Total ground floor buildable' in result:
                result['Surface_plot_land'] = result.pop('Total ground floor buildable')
                result['Surface_plot_land'] = result['Surface_plot_land'].split()[0]
            else:
                result['Surface_plot_land'] = None
            if 'Furnished' not in result:
                result['Furnished'] = 'No'
            if 'Bedrooms' in result:
                result['Number_of_rooms'] = result.pop('Bedrooms')
            else:
                result['Number_of_rooms'] = '0'
            for key in cls.columns:
                property_details[key] = result[key]

            return property_details