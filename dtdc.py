from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import multiprocessing
from IPython.display import display
import time as t
from datetime import date, time, datetime

pd.option_context('display.max_rows', None, 'display.max_columns', None)


def main(trackingNumber='V61886334'):
    # pageURL = 'https://www.dtdc.in/tracking/tracking_results.asp'
    pageURL = 'https://tracking.dtdc.com/ctbs-tracking/customerInterface.tr?submitName=showCITrackingDetails&cType' \
              '=Consignment&cnNo={tID}#{tID}'.format(tID=trackingNumber)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable_gpu')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(pageURL)

    '''inputField = driver.find_element_by_name("strCnno2")
    inputField.send_keys(trackingNumber)

    trackButton = driver.find_element_by_class_name("submit-button")
    trackButton.click()

    t.sleep(2)
    cookieButton = driver.find_element_by_id("CybotCookiebotDialogBodyButtonAccept")
    cookieButton.click()'''

    '''
    iframeElements = driver.find_elements(By.TAG_NAME, "iframe")

    # print([i.get_attribute("id") for i in iframeElements])
    driver.switch_to.frame(iframeElements[0])

    t.sleep(3)'''

    # driver.switch_to().frame("ifm1")
    collapseButton = driver.find_element_by_id("collapseOne_sign ")
    collapseButton.click()

    timeCounter = 0
    while True:
        t.sleep(1)
        try:
            imgElement = driver.find_element_by_xpath("/html/body/div[5]")
        except NoSuchElementException as e:
            imgElement = None

        if imgElement is None:
            break
        else:
            timeCounter += 1
        if timeCounter > 10:
            print("[Info] Timeout Error")
            driver.quit()
            exit(1)

    divElement = driver.find_element_by_id(trackingNumber + "_displayBar")
    statusUl = divElement.find_element_by_id("breadcrumbs-two")
    liElements = statusUl.find_elements(By.TAG_NAME, "li")

    status = ""
    for elem in liElements:
        styleAttr = elem.get_attribute("style")
        if styleAttr == "opacity: 1;":
            status = elem.text

    tableDataDict = {}
    locs = []
    tableHeading = driver.find_elements_by_xpath(
        "//*[@id='{tID}_displayBar']/table/thead/tr/th".format(tID=trackingNumber))
    for i, head in enumerate(tableHeading):
        heading = head.text
        if heading:
            tableDataDict[heading] = []
            locs.append(i)

    # print(tableDataDict)
    # print(locs)

    tableData = driver.find_elements_by_xpath(
        "//*[@id='activityDetailsForChildCn_{tID}']/tr".format(tID=trackingNumber))
    for i, data in enumerate(tableData):
        # print(data.text)
        if i % 2 == 0:
            rowData = data.find_elements(By.TAG_NAME, "td")
            # print(len(rowData))
            for j, loc in enumerate(locs):
                key = list(tableDataDict.keys())[j]
                tableDataDict[key].append(rowData[loc].text)

    df = pd.DataFrame(tableDataDict)
    # more options can be specified also

    driver.quit()
    timeNow = datetime.now()
    updatedTime = datetime.combine(date.today(), time(timeNow.hour, timeNow.minute, timeNow.second))
    print("Updated Time:  %s\t Status: %s" % (str(updatedTime), status))
    display(df)
    print("\n\n\n")
    # return updatedTime, status, df


if __name__ == '__main__':
    trackingNumber = input("Tracking Number: ")
    while True:
        # updatedTime, status, df = multiprocessing.Value()
        start = t.time()

        p = multiprocessing.Process(target=main, name="Main", args=(trackingNumber,))
        p.start()

        t.sleep(20)
        p.terminate()
        p.join()
        t.sleep(60*30)
