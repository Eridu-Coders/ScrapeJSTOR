#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'fi11222'

import argparse
import urllib.request
import re
import random
import time
import sys
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions as EX
from selenium.webdriver.common.action_chains import ActionChains

# --------------------------------- Globals ----------------------------------------------------------------------------
g_url = 'http://www.jstor.org/action/doAdvancedSearch?{0}{1}c1=AND&c2=AND&c3=AND&c4=AND&c5=AND&&c6=AND&group=none&pt=&la=&ed=&acc=on&isbn=&sd=&f0=all&f1=all&f2=all&f3=all&f4=all&f5=all&f6=all'

# http://www.jstor.org/action/doAdvancedSearch?
# q0={0}&
# q1={1}&
# q2={2}&
# q3={3}&
# q4={4}&
# q5={5}&
# q6={6}&
# ar=on&
# c1=AND&c2=AND&c3=AND&c4=AND&c5=AND&&c6=AND&group=none&pt=&la=&ed=&acc=on&isbn=&sd=&f0=all&f1=all&f2=all&f3=all&f4=all&f5=all&f6=all

# http://www.jstor.org/action/doAdvancedSearch?
# q0={0}&
# q1={1}&
# q2={2}&
# q3={3}&
# q4={4}&
# q5={5}&
# q6={6}&
# ar=on&
# c1=AND&c2=AND&c3=AND&c4=AND&c5=AND&&c6=AND&
# group=none&
# pt=&la=&ed=&acc=on&isbn=&sd=&
# f0=all&f1=all&f2=all&f3=all&f4=all&f5=all&f6=all

# http://www.jstor.org/action/doAdvancedSearch?
# q0=ppna&
# q1=ppnb&q2=&q3=&q4=&q5=&q6=&
# c1=AND&c2=AND&c3=AND&c4=AND&c5=AND&&c6=AND&
# group=none&
# pt=&la=&ed=&acc=on&isbn=&sd=&
# f0=all&f1=all&f2=all&f3=all&f4=all&f5=all&f6=all

# http://www.jstor.org/action/doAdvancedSearch?
# q6=&q4=&c6=AND&c4=AND&ar=on&
# c1=AND&
# f5=all&q2=&q3=&pt=&la=&f0=all&c5=AND&q5=&ed=&
# f2=all&c3=AND&f1=all&isbn=&acc=on&f3=all&
# q0=ppna&
# q1=ppnb&
# f6=all&f4=all&group=none&sd=&c2=AND

# --------------------------------- Functions --------------------------------------------------------------------------
def getDriver():
    l_profile = webdriver.FirefoxProfile()

    mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"

    l_profile.set_preference("browser.download.folderList", 2)
    l_profile.set_preference("browser.download.manager.showWhenStarting", False)
    l_profile.set_preference("browser.download.dir", os.getcwd())
    l_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    l_profile.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    l_profile.set_preference("pdfjs.disabled", True)

    # Create a new instance of the Firefox driver
    l_driver = webdriver.Firefox(l_profile)

    # Resize the window to the screen width/height
    l_driver.set_window_size(1500, 1500)

    # Move the window to position x/y
    l_driver.set_window_position(1000, 1000)

    return l_driver

# wait random time between given bounds
def randomWait(p_minDelay, p_maxDelay):
    if p_minDelay > 0 and p_maxDelay > p_minDelay:
        l_wait = p_minDelay + (p_maxDelay - p_minDelay)*random.random()
        print('Waiting for {0:.2f} seconds ...'.format(l_wait))
        time.sleep(l_wait)

def processLink(p_linkUrl, p_driver):
    global g_acceptTC

    print('Load url Link:', p_linkUrl)

    # p_link.click()
    p_driver.get(p_linkUrl)

    try:
        l_accept = WebDriverWait(p_driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//input[@id="acceptTC"]')))

        print('Click Accept TC')
        l_accept.click()

    except EX.ElementNotVisibleException:
        print('Accept TC not visible')
    except EX.TimeoutException:
        print('Accept TC pop-up not found!!')
        sys.exit()

    randomWait(5, 10)

# --------------------------------- Main section -----------------------------------------------------------------------
if __name__ == "__main__":
    print('+------------------------------------------------------------+')
    print('| JSTOR Scraping                                             |')
    print('|                                                            |')
    print('| v. 1.0 - 16/05/2016                                        |')
    print('+------------------------------------------------------------+')

    l_parser = argparse.ArgumentParser(description='Crawl JSTOR.'.format(g_url))
    l_parser.add_argument('keywords', help='Search keyword(s)')

    # dummy class to receive the parsed args
    class C:
        def __init__(self):
            self.keywords = ''

    # do the argument parse
    c = C()
    l_parser.parse_args()
    parser = l_parser.parse_args(namespace=c)

    l_driver = getDriver()

    print('kw:', c.keywords)
    l_listKW = (c.keywords.split(' ') + ['', '', '', '', '', '', ''])[0:7]
    print('l_listKW:', l_listKW)

    l_kwString = '&'.join(['q{0}={1}'.format(i, l_listKW[i]) for i in range(len(l_listKW))])

    l_driver.get(g_url.format(l_kwString + '&', 'ar=on&'))

    l_linkList = []
    try:
        WebDriverWait(l_driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@class, "pdfLink")]')))

        print('Page loaded')

        l_count = 0
        l_finished = False
        l_linkList = []
        while not l_finished:
            for l_link in l_driver.find_elements_by_xpath('//a[contains(@class, "pdfLink")]'):
                l_linkUrl = l_link.get_attribute('href')
                print('[{0:<4}] l_linkUrl:'.format(l_count), l_linkUrl)

                l_linkList += [l_linkUrl]

                l_count += 1

            try:
                l_driver.find_element_by_xpath('//a[text()="Next »"]').click()
                WebDriverWait(l_driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//a[contains(@class, "pdfLink")]')))
            except EX.NoSuchElementException as e:
                print('Next: No such Element.')
                l_finished = True
            except EX.ElementNotSelectableException as e:
                print('Next: Element not selectable.')
                l_finished = True
            except Exception as e:
                print('Next: Unknown exception:', e)
                l_finished = True

    except EX.TimeoutException:
        print('pdf link not found ... Something is not right')

    l_driver.close()

    for l_link in l_linkList:
        l_driver = getDriver()
        processLink(l_link, l_driver)
        l_driver.close()