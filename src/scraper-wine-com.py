from bs4 import BeautifulSoup
import time
import requests
import re

class Scraper:

    def __init__(self):
        self.session = requests.Session()
        self.searchURL = 'https://www.wine.com/list/wine/7155?sortBy=mostInteresting'
        self.filePath = '../data/wine-com/raw/{}.txt'.format(time.time())
        self.headerData = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        
        with open(self.filePath,'w') as fileObj:
            fileObj.write('Product_Name|Product_Varietal|Product_Origin|Product_Price|Product_Attributes|Critical_Reviews|User_Avg_Rating|User_Rating_Count\r\n')  
        fileObj.close()
            
    def scrape(self):
        
        while self.searchURL is not None:
            print(self.searchURL)
            
            #request results page
            resultsPageResponse = self.session.get(self.searchURL, headers = self.headerData)
            
            #soupify results page
            self.resultsPageSoup = BeautifulSoup(resultsPageResponse.content, 'html.parser')
            
            #filter to results list
            resultsContainer = self.resultsPageSoup.find('ul', attrs = {'class':'listGridLayout_list'})
            
            #iterate through results page
            for product in resultsContainer.find_all('div', attrs = {'class': 'listGridItemInfo'}):

                #generate dictionary for parsed fields
                self.prodData = dict()
                
                self.prodData['Product_Name'] = product.find('span', attrs = {'class':'listGridItemInfo_name'}).text
                self.prodData['Product_Varietal'] = product.find('span', attrs = {'class':'listGridItemOrigin_varietal'}).text
                self.prodData['Product_Origin'] = product.find('span', attrs = {'class':'listGridItemOrigin_text'}).text
                
                try:
                    self.prodData['Product_Price'] = product.find('span', attrs = {'class':'productPrice_price-regWhole'}).text
                except Exception:
                    self.prodData['Product_Price'] = '0'
                    
                try:
                    self.prodData['Product_Attributes'] = ''
                    prodAttr = product.find('ul', attrs = {'class': 'prodAttr'})
                    for tag in prodAttr.find_all('li'):
                        self.prodData['Product_Attributes'] = self.prodData['Product_Attributes'] + tag.get('title') + ','
                except Exception:
                    self.prodData['Product_Attributes'] = ''
                    
                try:
                    self.prodData['Critical_Reviews'] = product.find('ul', attrs = {'class': 'wineRatings_list'}).text
                    self.prodData['Critical_Reviews'] = re.sub(r'\D', ' ', self.prodData['Critical_Reviews'])
                except Exception:
                    self.prodData['Critical_Reviews'] = ''
            
                try:
                    self.prodData['User_Avg_Rating'] = product.find('span', attrs = {'class':'averageRating_average'}).text
                    self.prodData['User_Rating_Count'] = product.find('span', attrs = {'class':'averageRating_number'}).text
                except Exception:
                    self.prodData['User_Avg_Rating'] = ''
                    self.prodData['User_Rating_Count'] = ''
                    
                #write data to disk
                self.writeProductData()
                

            #determine if next page exists - if so assign next searchURL
            try:
                paginationContainer = self.resultsPageSoup.find('div', attrs = {'class':'nextPagePagination'})
                self.searchURL = paginationContainer.a['href']
            except Exception:
                self.searchURL = None

            #sleep to prevent server timeout
            time.sleep(3)


    def writeProductData(self):
        try:
            with open(self.filePath, 'a') as fileObj:
                fileObj.write('{}|{}|{}|{}|{}|{}|{}|{}\r\n'.format(self.prodData['Product_Name'],
                                                                   self.prodData['Product_Varietal'],
                                                                   self.prodData['Product_Origin'],
                                                                   self.prodData['Product_Price'],
                                                                   self.prodData['Product_Attributes'],
                                                                   self.prodData['Critical_Reviews'],
                                                                   self.prodData['User_Avg_Rating'],
                                                                   self.prodData['User_Rating_Count']))
                fileObj.close()
        except Exception:
            print(f'{self.productURL} write fail')



if __name__ == "__main__":
    wine_com_scraper = Scraper()
    wine_com_scraper.scrape()