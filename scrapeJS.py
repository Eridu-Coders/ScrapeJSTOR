#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'fi11222'

import argparse
import re
import random
import time
import sys
import os
import shutil

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

def processLink(p_article, p_csvOut):
    l_newFileName = re.sub(r'\W+', '_', p_article[1])[0:40] + '-' + \
                    re.sub('\W+', '_', p_article[2])[0:40] + '.pdf'
    l_newFileName = re.sub(r'_+', '_', l_newFileName)
    l_linkUrl = p_article[0]

    l_match = re.search(r'([^/]+\.pdf)$', l_linkUrl)
    if l_match:
        l_fileName = l_match.group(1)
    else:
        print('cannot find filename in [{0}] - ABORTING'.format(l_linkUrl))
        sys.exit()

    if os.path.isfile(l_newFileName) and os.stat(l_newFileName).st_size == 0:
        os.remove(l_newFileName)
        if os.path.isfile(l_fileName):
            os.remove(l_fileName)
        if os.path.isfile(l_fileName + '.part'):
            os.remove(l_fileName + '.part')

    if os.path.isfile(l_newFileName):
        print('Already downloaded:', l_newFileName)
    else:
        l_finished = False
        while not l_finished:
            l_driver = getDriver()

            print('Load url Link:', l_linkUrl, '-->', l_fileName)
            # p_link.click()
            l_driver.get(l_linkUrl)

            try:
                l_accept = WebDriverWait(l_driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@id="acceptTC"]')))

                print('Click Accept TC')
                l_accept.click()
                l_finished = True

            except EX.ElementNotVisibleException:
                print('Accept TC not visible')
            except EX.TimeoutException:
                print('Accept TC pop-up not found!!')
            except Exception as e:
                print('Unknown Exception', e)
                sys.exit()

            if l_finished:
                l_count = 0
                while not (os.path.isfile(l_fileName) and not os.path.isfile(l_fileName + '.part')):
                    time.sleep(1)
                    l_count += 1
                    print('Waiting ...', l_count, end='\r')

                    if l_count > 60*5:
                        l_finished = False
                        if os.path.isfile(l_fileName):
                            os.remove(l_fileName)
                        if os.path.isfile(l_fileName + '.part'):
                            os.remove(l_fileName + '.part')
                        break

                if l_finished:
                    print('download of [{0}] complete'.format(l_fileName))

                    time.sleep(.5)
                    print('renaming to:', l_newFileName)
                    os.rename(l_fileName, l_newFileName)

                    randomWait(5, 10)

            l_driver.close()

    p_csvOut.write('"{0}";"{1}";"{2}";"{3}";"{4}\n'.format(
        re.sub('"', '""', l_linkUrl),
        re.sub('"', '""', l_newFileName),
        re.sub('"', '""', l_title),
        re.sub('"', '""', l_author),
        re.sub('"', '""', l_source),
    ))

# --------------------------------- Main section -----------------------------------------------------------------------
if __name__ == "__main__":
    print('+------------------------------------------------------------+')
    print('| JSTOR Scraping                                             |')
    print('|                                                            |')
    print('| v. 1.1 - 17/05/2016                                        |')
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

    l_artList = []
    try:
        WebDriverWait(l_driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@class, "pdfLink")]')))

        print('Page loaded')

        l_count = 0
        l_finished = False
        while not l_finished:
            for l_row in l_driver.find_elements_by_xpath('//li[@class="row result-item"]'):

                l_link = l_row.find_element_by_xpath('.//a[contains(@class, "pdfLink")]')
                # tt-track
                l_title = l_row.find_element_by_xpath('.//a[contains(@class, "tt-track")]').text
                l_linkUrl = l_link.get_attribute('href')

                try:
                    l_author = l_row.find_element_by_xpath('.//div[@class= "contrib"]').text
                except Exception:
                    l_author = ''

                try:
                    l_source = l_row.find_element_by_xpath('.//div[@class= "src"]').text
                except Exception:
                    l_source = ''

                if len(l_title) > 50:
                    l_titleShort = l_title[0:50] + '... ({0})'.format(len(l_title))
                else:
                    l_titleShort = l_title
                print('[{0:<4}] {1:<60} {2:<60}'.format(l_count, l_linkUrl, l_titleShort))

                l_artList += [(l_linkUrl, l_title, l_author, l_source)]


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

    l_csvFileName = re.sub('\W+', '_', c.keywords) + '.csv'
    l_csvOut = open(l_csvFileName, 'w')
    l_csvOut.write('"URL";"FILE";"TITLE";"AUTHOR";"SOURCE"\n')

    l_count = 0
    for l_article in l_artList:
        print('------------[{0}]---------------------------'.format(l_count))
        processLink(l_article, l_csvOut)
        l_count += 1

    l_csvOut.close()
