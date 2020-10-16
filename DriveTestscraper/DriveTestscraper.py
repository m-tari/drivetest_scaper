from requests import get
import time
url = "https://drivetest.ca/book-a-road-test/booking.html#/validate-driver-email"
url_test = "https://www.facebook.com/"
from bs4 import BeautifulSoup
from selenium import webdriver
from info import licenceNumber,emailAddressLic,expiryDate,emailAddresses,emailSubject,emailFrom,myTestDateString,testType

driver = webdriver.Chrome('/Users/josephshaju/Downloads/chromedriver')
driver.get(url)
#time.sleep(5) # Let the user actually see something!



"""
- Enter into website
- Input relevant information
- Select test centers to check (may be multiple)
    - Parse to find free date
        - if found store relevant information
- Send email about the dates if available, otherwise just send an update email
"""


email = driver.find_element_by_id("emailAddress")
confirmEmail = driver.find_element_by_id("confirmEmailAddress")
licNum = driver.find_element_by_id("licenceNumber")
licExpDate = driver.find_element_by_id("licenceExpiryDate")


email.send_keys(emailAddressLic)
confirmEmail.send_keys(emailAddressLic)
licNum.send_keys(licenceNumber)
licExpDate.send_keys(expiryDate)
driver.find_element_by_id("regSubmitBtn").click()

url_temp = driver.current_url
while (url_temp == url):
    url_temp = driver.current_url
driver.get(url_temp)

# html = driver.page_source
# print(html)
# soup = BeautifulSoup(html,'html.parser')
# new = soup.find(id='G2btn')
# print(new)
if testType == "G2":

    #driver.find_element_by_id("G2btn").click()
    #driver.find_elements_by_class_name(".ng-scope").click()
    #driver.find_element_by_css_selector(".ng-binding[@id = 'G2btn']").click()
    driver.find_element_by_css_selector("form[@id = 'G2btn']").click()
    #driver.find_element_by_xpath("//form//label[@for='lic_G2' and @id='G2btn']").click()

else:
    driver.find_element_by_id("Gbtn").click()
driver.find_element_by_css_selector("input[type='label'][value='SRF']").click()
# driver.find_element_by_css_selector(".btn").click()


# driver.find_element_by_id("submit_btn").click()
# driver.find_element_by_name("submitButton").click()




