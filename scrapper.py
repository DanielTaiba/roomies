from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup


class compartoDepto ():
    def __init__(self) -> None:
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        self.main_url = 'https://www.compartodepto.cl/'

    def travel_pages(self):
        next_page = '?page=1'
        while next_page is not None:
            self.driver.get(self.main_url+next_page)
            html = self.driver.execute_script('return document.documentElement.outerHTML')
            next_page = self.extract_page(html)
            self.driver.quit()

    def extract_page (self,html):
        soup = BeautifulSoup(html,'lxml')
        rooms = soup.find_all('div',attrs={'class':'listing_item'})
        with open('href_rooms.txt','a') as file:
            for room in rooms:
                file.write(room.a['href']+'\n')
        next_page = soup.find('div',attrs={'class':'listing_pagination_page listing_pagination-next'})
        if next_page is not None:
            next_page = next_page.a['href'] 
        return next_page

    def get_room_endpoint(self,file_name = 'href_rooms.txt'):
        with open(file_name,'r') as file:
            while(True):
                endpoint=file.readline()
                if not endpoint:
                    break
                yield endpoint
            
    def get_info_rooms(self):
        count=0
        for endpoint in self.get_room_endpoint(file_name='href_rooms.txt'):
            self.driver.get(self.main_url+endpoint) 
            html = self.driver.execute_script('return document.documentElement.outerHTML')
        
            path =  f'htmlRooms/room_{count}.html'
            with open(path,'w') as file:
                file.write(html)
            count+=1
        self.driver.quit()

    def parse_info_rooms(self,html):
        soup = BeautifulSoup(html,'lxml')
        contents = soup.find_all('div',attrs={'class':'content-block'})
        data_room=list()
        for content in contents:
            data_room.append(self.get_contents(content))
        return data_room
    
    def get_contents(self,contents):
        if contents.attrs=={}:
            try:
                return {'tag':contents.name,'text':contents.text}
            except:
                return{}
        else:
            try:
                data={
                    'attrs':contents.attrs,
                }
            except:
                data={'attrs':None}
            try:

                for c in contents.contents:
                    if c !='\n':
                        data['content']=self.get_contents(c)
            except:
                data['content']=None
            
            return data

if __name__=='__main__':
    web = compartoDepto()
    #web.travel_pages()
    web.get_info_rooms()
    #web.get_info_room()
    pass