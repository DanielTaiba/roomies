from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import os
from utils import writeJsonFile,normalizeString

class compartoDepto ():
    def __init__(self) -> None:
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        self.main_url = 'https://www.compartodepto.cl/'
        self.path_infoRooms = './infoRooms/'

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
    #### DEPRECATED ####
    def get_room_endpoint(self,file_name = 'href_rooms.txt'):
        with open(file_name,'r') as file:
            while(True):
                endpoint=file.readline()
                if not endpoint:
                    break
                yield endpoint
            
    def _info_rooms(self):
        count=0
        for endpoint in self.get_room_endpoint(file_name='href_rooms.txt'):
            self.driver.get(self.main_url+endpoint) 
            html = self.driver.execute_script('return document.documentElement.outerHTML')
        
            path =  f'htmlRooms/room_{count}.html'
            with open(path,'w') as file:
                file.write(html)
            count+=1
        self.driver.quit()

    def read_html(self,base_dir='./htmlRooms/'):
        list_data = []
        for page in os.listdir(base_dir):
            
            with open(base_dir+page) as html:
                data = self.parse_info_rooms(html)
            data['code']=page.split('.')[0]
            data['url']=page
            writeJsonFile(data=data,fileName='./infoRooms/'+data['code']+'.json')

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
    web.get_info_rooms()
    #web.get_info_rooms()
    #web.get_info_room()
    #web.read_html()
    pass