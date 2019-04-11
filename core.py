
import os
import time
import platform
import unittest
import logging
import json
import requests

from selenium import webdriver
import allure

from .libs.decorators import TryRequests
from .exceptions import RequestSoftAssert, WebSoftAssert
from .logger import check_console_error


log = logging.getLogger(__name__)


class WebTestCase(unittest.TestCase, WebSoftAssert):

    def setUp(self):
        self.assert_errors = '\n'

        if platform.system() == 'Win32':
            chromedriver = "E:\\instal\\Programming\\chromedriver.exe"
            os.environ["webdriver.chrome.driver"] = chromedriver
            self.driver = webdriver.Chrome(chromedriver)

        if platform.system() == 'Linux':
            chromedriver = "/usr/bin/chromedriver"
            os.environ["webdriver.chrome.driver"] = chromedriver
            self.driver = webdriver.Chrome(chromedriver)

        if platform.system() == 'Darwin':
            self.driver = webdriver.Chrome()

        self.driver.maximize_window()

    def tearDown(self):
        # from datetime import datetime
        # screen_path = os.path.dirname(__file__) + '\\screenshots\\%s.png' % \
        #               datetime.now().strftime("%Y-%m-%d_%H%M%S")
        # self.driver.save_screenshot(screen_path)
        # print('Test URL: %s' % self.driver.current_url)
        # print('ScreenShot URL: %s' % screen_path)
        check_console_error(self.driver)
        if self.driver:
            self.driver.close()
        self.check_assert_errors()

    @property
    def log(self):
        """ логирование
        пример использования:
            self.log.info('---- some info -----')
            self.log.error('some shit')
            self.log.critical('Alarm dosn`t work')
        """
        return log

    def sleep(self, timeout=1):
        time.sleep(timeout)


# ----------------------------------------------------------------------------#
#                               REQUESTS
# ----------------------------------------------------------------------------#
class RequestTestCase(unittest.TestCase, RequestSoftAssert):

    session = requests.session()
    response = None

    def setup_method(self, method):
        self.assert_errors = '\n'

    def teardown_method(self, method):
        with allure.step('[close] Закрытие сессии'):
            if self.session:
                self.session.close()
        self.check_assert_errors()

    @TryRequests
    @allure.step('[Request] {url}')
    def make_request(
            self, url, method="GET", status_code=200,
            params=None, headers={}, data=None, cookies={}, **kwargs
    ):
        """ выполнение request запросов при тестировании API с логированием"""
        head_param = {"Api-Agent": "android"}
        head_param.update(headers)
        self.response = self.session.request(
            url=url,
            method=method,
            params=params,
            headers=head_param,
            data=data,
            verify=False,
            cookies=cookies,
            timeout=15,
            **kwargs
        )
        log.info(
            f"API[request]: \n"
            f"\tURL: {url} \n"
            f"\tMETHOD: {method} \n"
            f"\tPARAMS: {params} \n"
            f"\tHEADERS: {headers} \n"
            f"\tDATA: {data}"
        )

        self.soft_assert_equal(
            self.response.status_code,
            status_code,
            "Не совпадает код ответа request запроса"
        )

        try:
            _json = self.response.json()
        except Exception:
            _json = None

        allure.attach(
            json.dumps(_json, indent=4),
            name='[Response] {code} {reasone}, {seconds}sec'.format(
                code=self.response.status_code,
                reasone=self.response.reason,
                seconds=self.response.elapsed.total_seconds(),
            ),
            attachment_type=allure.attachment_type.JSON
        )
        log.info(
            "API[response]: \n"
            "\tCODE: {code}, {reason}, {seconds} sec\n"
            "\tJSON: \n{json}\n".format(
                code=self.response.status_code,
                reason=self.response.reason,
                seconds=self.response.elapsed.total_seconds(),
                json=json.dumps(_json, indent=4)
            )
        )
        # check_api_response(self)
        return self.response

    @property
    def log(self):
        """ логирование
        пример использования:
            self.log.info('---- some info -----')
            self.log.error('some shit')
            self.log.critical('Alarm dosn`t work')
        """
        return log
