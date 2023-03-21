from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import pycountry
from fuzzywuzzy import fuzz

class Scraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)
        
        self.rawDirectory = '../data/wunderground-com/raw'
        if not os.path.exists(self.rawDirectory):
            os.makedirs(self.rawDirectory)

        #function that loads reference data
        self.reference_df = pd.read_csv('../data/wine-com/processed/1678665697.3855994.txt', sep = '|')
    
    #technically preprocessing - should be moved to 2_preprocessing.ipynb
    def location_match(self, target_region, autocomplete_options):
        #score holders
        highest_score = 0
        best_match = None
        
        #reconciling wine-com naming schemas
        wine_com_state_ids = ['California', 'Washington', 'Oregon']
        wine_com_generic_id = 'Other U.S. States'
        
        #prep target country - convert to iso 3166
        target_region_list = target_region.split(',')
        pycountry_search = pycountry.countries.search_fuzzy(target_region_list[-1])
        pycountry_top_name = pycountry_search[0].name
        if target_region_list[-1] == pycountry_top_name:
            target_region_list[-1] = pycountry_search[0].alpha_2
        elif target_region_list[-1] in wine_com_state_ids:
            target_region_list[-1] = target_region_list[-1] + ', US'
        elif target_region_list[-1] == wine_com_generic_id:
            target_region_list[-1] = 'US'
        else:
            target_region_list[-1] = pycountry_search[0].alpha_2
            
        #join target list
        target_region = ', '.join(target_region_list)
        
        for option in autocomplete_options:
            option_text = option.text.split(',', 1)[1]
            score = fuzz.ratio(target_region, option_text)
            if score > highest_score:
                highest_score = score
                best_match = option.text
        return best_match
    
    #main scrape function
    def scrape(self):
        ### iterate through listing corpus to retrieve associated weather daat
        for idx, row in self.reference_df.iterrows():
            # assign search year
            self.year = row['Product_Vintage']
            # assign search region
            self.full_region = row['Product_Origin']
            
            ### checks if region/year has already exists
            if f'{self.full_region}_{self.year}_12*' not in os.listdir(self.rawDirectory):
            
                ### request wunderground historical search page
                self.driver.get('https://www.wunderground.com/history')
                self.driver.implicitly_wait(3)
                
                ### data input for initial search
                # location selection
                location_select = self.driver.find_element(By.NAME, 'historySearch')
                location_select.send_keys(self.full_region)
                autocomplete_elements = self.driver.find_elements(By.XPATH, "//li[@class='needsclick needsfocus defcon- is-city ng-star-inserted']")
                best_option_text = self.location_match(self.full_region, autocomplete_elements)
                for option in autocomplete_elements:
                    if best_option_text in option.text:
                        option.click()
                        break
        
                # month selection
                month_select = self.driver.find_element(By.ID, 'monthSelection')
                month_select.send_keys('January')
                
                # day selection
                day_select = self.driver.find_element(By.ID, 'daySelection')
                day_select.send_keys('1')
                
                # year selection
                year_select = self.driver.find_element(By.ID, 'yearSelection')
                year_select.send_keys(self.year)
                
                # submit search
                submit_button = self.driver.find_element(By.XPATH, "//input[@class='submit-btn button radius ng-star-inserted']")
                submit_button.click()
                time.sleep(2)
                
                ### navigate to monthly aggregation data
                monthly_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Monthly")))
                monthly_link.click()
                
                ### retrieve actual weather location
                change_button = self.wait.until(EC.element_to_be_clickable((By.ID, "station-select-button")))
                change_button.click()
                
                actual_location_data = self.wait.until(EC.presence_of_element_located((By.XPATH, "//strong[@class = 'location-data']")))
                self.location_actual = actual_location_data.text
                print(self.location_actual)
                
                ### monthly data retrieval - index starts as 1
                for index in range(1, 13):
                    #determine appropriate page load
                    if index != 1:
                        # select next month
                        select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "monthSelection"))))
                        select.select_by_index(index)
                        
                        # submit
                        view_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='submit-btn button radius ng-star-inserted']")))
                        view_button.click()
                    
                    #search and load monthly data to dataframe
                    table = self.wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class = 'days ng-star-inserted']")))
                    df = pd.read_html(table.get_attribute('outerHTML'))
                    df[0].to_csv(self.rawDirectory + '/' + self.full_region + '_' + str(self.year) + '_' + str(index) + '_' + self.location_actual + '.csv', 
                                 index = False, 
                                 header=1)
                    
        
if __name__ == "__main__":
    wunderground_scraper = Scraper()
    wunderground_scraper.scrape()