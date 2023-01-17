from contextlib import contextmanager
from collections.abc import Generator
from time import sleep
from itertools import chain
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as SelTimeoutException

from bs4 import BeautifulSoup


class SeleniumWB:

    def __init__(self) -> None:
        self.driver = webdriver.Chrome()

    def _close(self) -> None:
        self.driver.close()

    @staticmethod
    @contextmanager
    def open_sel() -> Generator['SeleniumWB', None, None]:
        driver = SeleniumWB()
        yield driver
        driver._close()

    def get_cite(self, cite: str) -> None:
        self.driver.get(cite)
        sleep(.1)

    def login(self, login: str, password: str) -> None:
        login_el = self.driver.find_element(By.NAME, 'login')
        password_el = self.driver.find_element(By.NAME, 'password')
        enter_btn = self.driver.find_element(By.ID, 'enter')

        login_el.send_keys(login)
        password_el.send_keys(password)
        enter_btn.click()
        sleep(.1)

    def get_pic(self, vendor: str, brand: str) -> None:
        search_bar = self.driver.find_element(By.ID, 'inp_search')
        search_btn = self.driver.find_element(By.CLASS_NAME, 'search-btn')

        search_bar.send_keys(vendor)
        search_btn.click()
        try:
            table = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'effect'))
            )
            return self.extract_pic(vendor, brand)
            
        except SelTimeoutException:
            print('Таблица не прогрузилась!')

            return None


    def extract_pic(self, vendor: str, brand: str) -> Optional[str]:
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        table = page.find('div', id='effect')
        for row in chain(table.find_all('tr', class_='tr'), table.find_all('tr', class_='tr_sa')):
            vendor_found, brand_found = row.find('td', class_='td2').text, row.find('td', class_='td3').text
            if vendor_found == vendor and brand_found == brand:
                pic_element = row.find('td', class_='td6')
                if pic_element.a:
                    return pic_element.a['href']
        return None


if __name__ == '__main__':
    with SeleniumWB.open_sel() as driver:
        driver.get_cite('https://itrade.forum-auto.ru/')
        driver.login('492963', '4fde77479d3bb97c')
        driver.get_pic('12018754B', 'CORTECO')
        sleep(5)
