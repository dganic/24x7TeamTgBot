import os
import time
import pickle
import requests

from loguru import logger
from datetime import datetime
from selenium import webdriver
from multiprocessing import Process
from webdriver_manager.chrome import ChromeDriverManager

from data import config


cookies_file = config.cookies_file
session_cookie = config.session_cookie
wait_login = config.wait_login


def _add_cookies(session, cookies):
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    logger.info(f'Cookies added to session: {session}')
    return session


def _load_cookies():
    with open(cookies_file, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
    logger.info(f'Cookies loaded from file: {cookies_file}')
    logger.debug(f'Saved cookies from file: {cookies}')
    return cookies


def _save_cookies(cookies):
    with open(cookies_file, 'wb') as filehandler:
        pickle.dump(cookies, filehandler)
    logger.info(f'Cookies has been saved to file: {cookies_file}')


class Driver:
    def __init__(self, inst_url):
        self.inst_url = inst_url
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def save_chrome_cookies(self):
        logger.info(f'Chrome has been opened for new login to {self.inst_url}')
        self.driver.get(self.inst_url)
        while True:
            logger.info(f'Waiting for a login to {self.inst_url} in Chrome')
            time.sleep(wait_login)
            self.cookies = self.driver.get_cookies()
            self.cookies_name = [cookie for cookie in self.cookies if cookie['name'] == session_cookie]
            if self.cookies_name:
                _save_cookies(self.cookies)
                logger.info(f'Cookies from chrome have been saved')
                break

    def __del__(self):
        self.driver.quit()
        logger.info(f'Chrome has been closed')


class ServiceNow:
    def __init__(self, inst_url):
        self.inst_url = inst_url
        self.session = self._login()
        if self.session:
            logger.info('Session has been created')
        else:
            while not self.session:
                logger.warning('Session has not been created')
                logger.warning('Cookies not valid')
                os.remove(cookies_file)
                logger.info('Old cookies file has been removed')
                self.session = self._login()
            logger.info('Session has been created')
        self.proc_cookies_upd = Process(target=self._update_cookies)
        self.proc_cookies_upd.start()

    def _login(self):
        self.cookies = self._get_cookies()
        self.init_session = requests.Session()
        self.login_session = _add_cookies(self.init_session, self.cookies)
        self.resp_inst_url = self.login_session.get(self.inst_url, allow_redirects=False)
        logger.info(f'Response code from instance url (startup process): {self.resp_inst_url.status_code}')
        if self.resp_inst_url.status_code != 200:
            return None
        else:
            logger.info('Login process completed successfully')
            self.cookies_exp = self._get_cookies_exp_date()
            logger.info(f'Сookies expiration date: {self.cookies_exp}')
            return self.login_session

    def _get_cookies(self):
        while not cookies_file.is_file():
            logger.info(f'Cookies file not found: {cookies_file}')
            self.chrome = Driver(self.inst_url)
            self.chrome.save_chrome_cookies()
            del self.chrome
        logger.info(f'Cookies file found: {cookies_file}')
        self.cookies = _load_cookies()
        return self.cookies

    def _get_cookies_exp_date(self):
        self.cookies_exp_timestamp = [cookie.expires for cookie in self.resp_inst_url.cookies if
                                      cookie.name == session_cookie]
        return datetime.fromtimestamp(self.cookies_exp_timestamp[0])

    def _update_cookies(self):
        logger.info(f'Process for autoupdate session cookies has been started')
        while True:
            self.resp_inst_url = self.session.get(self.inst_url)
            logger.info('Cookies have been updated')
            self.cookies_exp = self._get_cookies_exp_date()
            logger.info(f'Cookies expiration date: {self.cookies_exp}')
            self.wait_update = int((self.cookies_exp - datetime.now()).total_seconds() * 0.9)
            logger.info(f'Cookies will be updated via: {self.wait_update} seconds')
            time.sleep(self.wait_update)

    def get_tickets(self, tickets_url):
        resp_tickets_url = self.session.get(self.inst_url + tickets_url)
        logger.info(f'Response code from tickets url: {resp_tickets_url.status_code}')
        return resp_tickets_url.json()
