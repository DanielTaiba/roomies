from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import os
from utils import writeJsonFile,normalizeString

class compartoDepto ():
    def __init__(self) -> None:
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        self.main_url = 'https://www.compartodepto.cl'
        self.path_infoRooms = './infoRooms/'
        self.path_generalStats = './generalStats/'
        self.urls={
            'CL':"https://www.compartodepto.cl",
            'UK':"https://www.roomgo.co.uk",#united kingdom
            'NZ':'https://www.roomgo.co.nz',#new zealand        
            'IE':"https://ie.roomgo.net",#ireland
            'US':"https://www.roomgo.net",#eeuu
            'HK':"https://www.roomgo.com.hk",#Hong Kong
            'CA':"https://ca.roomgo.net",#canada
            'AU':"https://au.roomgo.net",#australia
            'SG':"https://www.roomgo.com.sg",#singapure
            'AR':"https://www.roomgo.com.ar",
            'BE':"https://www.appartager.be",
            'SZ':"https://www.roomgo.ch",#suiza
            'FR':"https://www.appartager.com",#france
            'IT':"https://www.roomgo.it",
            #'VE':"https://www.compartoapto.com.ve",#venezuela deactivated
            'BR':"https://www.roomgo.com.br",
            'LU':"https://www.appartager.lu",#luxembourg
            'CO':"https://www.compartoapto.com",#Colombia
            'ES':"https://www.roomgo.es",
            'MX':"https://www.roomgo.com.mx",
            'PT':"https://www.roomgo.pt",#portugal
     }
    
    def get_general_stats(self):
        if not os.path.exists(self.path_generalStats):
            os.makedirs(self.path_generalStats)

        for countryCode,url in self.urls.items():
            self.driver.get(url)
            html = self.driver.execute_script('return document.documentElement.outerHTML')
            data = self.parse_general_stats(html,countryCode)
            writeJsonFile(data,fileName=self.path_generalStats+countryCode+'.json')
        self.driver.quit()
    
    def parse_general_stats(self,html,countryCode):
        soup = BeautifulSoup(html,'lxml')
        titles = soup.find_all('div',attrs={'class':'hp_title'})
        stats = soup.find_all('div',attrs={'class':'stats_box'})

        try:
            roomies = titles[-2].text.split(' ')[0]
            roomies = int(roomies.replace(',',''))
        except:
            roomies = None

        try:
            rooms = titles[-1].text.split(' ')[0]
            rooms = int(rooms.replace(',','')) 
        except:
            rooms=None
        
        list_stats=[]
        for stat in stats:
            try:
                title=normalizeString(stats[0].find('div',attrs={'class':'stats_box_title'}).text)
            except:
                title=None

            try:
                names = stat.find_all('div',attrs={'class':'left'})
                values = stat.find_all('div',attrs={'class':'right'})
                contents = {normalizeString(names[i].text):normalizeString(values[i].text) for i in range(min(len(names),len(values)))}
            except:
                contents={}
            list_stats.append({
                'title':title,
                'contents':contents
            })
        
        return {
            'pais':countryCode,
            'roomies':roomies,
            'rooms':rooms,
            'stats':list_stats
        }

    def get_info_rooms(self):
        if not os.path.exists(self.path_infoRooms):
            os.makedirs(self.path_infoRooms)
        next_page = '?page=1'
        
        while next_page is not None:
            self.driver.get(self.main_url+next_page)
            html = self.driver.execute_script('return document.documentElement.outerHTML')
            next_page = self.extract_page(html)
        self.driver.quit()

    def extract_page (self,html):
        soup = BeautifulSoup(html,'lxml')
        rooms = soup.find_all('div',attrs={'class':'listing_item'})
        for room in rooms:
            try:
                endpoint = room.a['href']
            except:
                endpoint = None
            
            if endpoint is not None:
                self.driver.get(self.main_url+endpoint)
                data = self.parse_info_rooms(self.driver.execute_script('return document.documentElement.outerHTML'))
                data['code']=endpoint.split('/')[-1]
                data['url']=endpoint
                data['status'] = 'active'
                writeJsonFile(data=data,fileName=self.path_infoRooms+data['code']+'.json')
                self.driver.back()

        next_page = soup.find('div',attrs={'class':'listing_pagination_page listing_pagination-next'})
        if next_page is not None:
            next_page = next_page.a['href'] 
        return next_page

    def parse_info_rooms(self,html):
        soup = BeautifulSoup(html,'lxml')
        #find
        header = soup.find('div',attrs={'class':'header-block'})
        about_room = soup.find('div',attrs={'class':'about-room'})
        desc = soup.find('div',attrs={'class':'description-text'})

        try:
            area = normalizeString(header.attrs['data-test-address']) 
        except:
            area = None
        
        try:
            title = normalizeString(header.h1.string)
        except:
            title = None

        try:
            cost = soup.find('h4',attrs={'class':'cost-detail'}).span.string
            cost = cost.split(' ')[-1]
            cost = cost.replace('.','')
            cost = int(cost)
        except:
            cost = None

        try:
            features=[]
            for feat in about_room.find_all('li',attrs={'class':'prop-icon'}):
                feat = feat.text.replace('\n\n\n\n                        ','')
                feat = feat.split('\n')
                features.append(normalizeString(feat[0]))
        except:
            features = []
        
        try:
            desc = [ normalizeString(d.text) for d in  desc.find_all('p') if d.text != '']
        except:
            desc = []
        
        return {
            'area':area,
            'title':title,
            'cost':cost,
            'features': features,
            'description':desc
        }

    def get_contents(self,content):
        data =  {
            'name_tag': content.name,
            'attrs':content.attrs,
            'text':content.text,
            'childrens': [self.get_contents(child) for child in content.children if not isinstance(child,str)],
        }
        return data

if __name__=='__main__':
    web = compartoDepto()
    #web.get_info_rooms()
    web.get_general_stats()
    pass