from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
import os
import pycountry
from fuzzywuzzy import fuzz

class Scraper:

    def __init__(self):
        self.rawDirectory = '../data/wunderground-com/raw'
        if not os.path.exists(self.rawDirectory):
            os.makedirs(self.rawDirectory)
        
        #determine if location-map exists, initialize if not
        try:
            with open(self.rawDirectory + '/1_location-map.json', 'r') as fileObj:
                self.location_map = json.load(fileObj)
        except:
            self.location_map = {}
        
        #function that loads reference data
        self.reference_df = pd.read_csv('../data/wine-com/processed/1678665697.3855994.txt', sep = '|')
        
    #
    def location_match(self, autocomplete_options):
        #score holders
        highest_score = -1
        best_match = None
        best_match_text = None
        ### preprocess autocomplete options
        for option in autocomplete_options:
            option_components = option.text.split(', ')
            if len(option_components[-1]) == 2:
                # test to check if us state
                try:
                    country = pycountry.subdivisions.get(code = f'US-{option_components[-1]}').country.name
                    state = pycountry.subdivisions.get(code = f'US-{option_components[-1]}').name
                except Exception:
                    country = None
                    state = None

                if option_components[-1] == 'US':
                  option_components[-1] = 'United States'
                  state_list = list(pycountry.subdivisions.get(country_code='US'))
                  for state in state_list:
                      if state.code == 'US-' + option_components[-2]:
                          state_name = state.name
                          break
                  option_components[-2] = state_name
                  del option_components[0]
                # checks if two digit code refers to US subdivision
                elif country == 'United States':
                    option_components[-1] = state
                    option_components.append('United States')
                # assumes remaining formats are international and pws locations
                else:
                    option_components[-1] = pycountry.countries.search_fuzzy(option_components[-1])[0].name
            
            # join components
            option_text = ', '.join(option_components)
            print(f'Option: {option_text}')
            # score string match
            score = fuzz.ratio(self.region, option_text)
            
            # match requirements for US locations requires exact state match instead of country match
            if self.region_components[-1] == 'United States':
                if score > highest_score and self.region_components[-2] == option_components[-2]:
                    highest_score = score
                    best_match = option
                    best_match_text = option_text
            else: 
                if score > highest_score and self.region_components[-1] == option_components[-1]:
                    highest_score = score
                    best_match = option
                    best_match_text = option_text
                
        if best_match is None:
            raise Exception('No match found at specified appellation level')
        print(f'Selected String: {best_match_text}, {highest_score}')
        return best_match
    
    #main scrape function
    def scrape(self):
        ### iterate through listing corpus to retrieve associated weather daat
        for idx, row in self.reference_df.iterrows():
            # assign search year
            self.year = row['Product_Vintage']
            # assign search region
            self.region = row['Product_Origin']
            self.region_components = self.region.split(', ')
            print(idx)
            print(f'Search Target: {self.region}-{self.year}')
            
            try:
                self.existing_map = self.location_map[self.region]
                print('Location Mapping Already Performed')
            except Exception:
                self.existing_map = None
                
            self.previously_scraped = False
            if self.existing_map is not None:
                for filename in os.listdir(self.rawDirectory):
                    if f'{self.existing_map}_{self.year}_11' in filename:
                        self.previously_scraped = True
                        print('Location/Date Previously Scraped')
                        break

            if self.previously_scraped == False:
                try:
                    self.driver = webdriver.Chrome()
                    self.wait = WebDriverWait(self.driver, 10)
                    ### request wunderground historical search page
                    self.driver.get('https://www.wunderground.com/history')
                    self.driver.implicitly_wait(1)
                    try:
                        location_select = self.driver.find_element(By.NAME, 'historySearch')
                        local_data = self.region_components[0]
                        print(f'Search String: {local_data}')
                        location_select.send_keys(local_data)
                        time.sleep(1)
                        autocomplete_elements = self.driver.find_elements(By.XPATH, "//li[starts-with(@class,'needsclick needsfocus defcon- is-city')]")
                        best_option = self.location_match(autocomplete_elements)
                        for option in autocomplete_elements:
                            if option == best_option:
                                option.click()
                                break
                    except Exception:
                        location_select = self.driver.find_element(By.NAME, 'historySearch')
                        location_select.clear()
                        local_data = self.region_components[1]
                        print(f'Search String: {local_data}')
                        location_select.send_keys(local_data)
                        time.sleep(1)
                        autocomplete_elements = self.driver.find_elements(By.XPATH, "//li[starts-with(@class,'needsclick needsfocus defcon- is-city')]")
                        best_option = self.location_match(autocomplete_elements)
                        for option in autocomplete_elements:
                            if option == best_option:
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
                    
                    # wait for page to load -- do not remove
                    time.sleep(2)
                    
                    ### get actual location
                    actual_location = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'columns small-12 city-header ng-star-inserted']"))).text
                    self.actual_geo, temp_loc = actual_location.split('\n', 1)
                    self.actual_name = temp_loc.split(' Weather History')[0]
                    print(f'Approximated Location: {self.actual_name}\n')
                    
                    self.previously_scraped = False
                    for filename in os.listdir(self.rawDirectory):
                        if f'{self.actual_name}_{self.year}_11' in filename:
                            self.previously_scraped = True
                            print('Location/Date Previously Scraped\n')
                            break
                            
                    if self.previously_scraped == False:
                        
                        ### navigate to monthly aggregation data
                        monthly_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Monthly")))
                        monthly_link.click()
                        
                        ### monthly data retrieval - index starts as 1
                        for index in range(0, 12):
                            #determine appropriate page load
                            if index != 0:
                                # select next month
                                select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "monthSelection"))))
                                select.select_by_index(index)
                                
                                # submit
                                view_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='submit-btn button radius ng-star-inserted']")))
                                view_button.click()
                            
                            #search and load monthly data to dataframe
                            table = self.wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class = 'days ng-star-inserted']")))
                            df = pd.read_html(table.get_attribute('outerHTML'))
                            df[0].to_csv(self.rawDirectory + '/' + self.actual_name + '_' + str(self.year) + '_' + str(index) + '_' + self.actual_geo + '.csv', 
                                         header = 1,
                                         index = False)
                    
                    # stores region-search map to dicitonary
                    self.location_map[self.region] = self.actual_name
                    self.driver.close()
                    time.sleep(1)
                
                except Exception:
                    self.driver.close()
                    time.sleep(1)
                
                #write location map to JSON file
                with open(self.rawDirectory + '/1_location-map.json', 'w') as fileObj:
                    json.dump(self.location_map, fileObj)
                fileObj.close()
        
if __name__ == "__main__":
    wunderground_scraper = Scraper()
    wunderground_scraper.scrape()