from contextlib import contextmanager
from collections.abc import Generator
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as SelTimeoutException

from bs4 import BeautifulSoup

import requests

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
            self.driver.current_url
            print('ok')
        except SelTimeoutException:
            print('Таблица не прогрузилась!')

    def extract_pic(self, vendor: str, brand: str) -> None:
        page = BeautifulSoup(self.driver.current_url, 'lxml')
        table = page.find('div', id_='effect')


if __name__ == '__main__':
    with SeleniumWB.open_sel() as driver:
        driver.get_cite('https://itrade.forum-auto.ru/')
        driver.login('492963', '4fde77479d3bb97c')
        driver.get_pic('12018754B', None)
        sleep(5)
