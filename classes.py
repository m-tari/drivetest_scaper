from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

import numpy as np
import pandas as pd
import time
import calendar
import yagmail


class testCase(object):
	"""A drivetest test case"""
	def __init__(self, name,**kwargs):

		self.name 			  = name
		self.testType         = "G2"
		self.locations_gta    =["Toronto Etobicoke", "Oshawa", "Brampton", "Newmarket", "Burlington", "Mississauga", "Oakville",
								 "Toronto Downsview", "Toronto Metro East",
								"Toronto Port Union"]
		self.location         = self.locations_gta
		self.headless         = False
		self.incognito        = False
		self.write			  = False
		self.verify           = False
		self.sendEmail        = True

	def sendEmail(self):
		print("Sending Email.......")

		receiver = self.emailAddress
		subject = "New timeslots found on drivetest.ca website"
		body = """\
		Hello

		A new timeslot is found on drivetest.ca website.
		Please book it as soons as possible.

		Best,
		Book.Road.Test.Online team

		"""
		yag = yagmail.SMTP(self.cloundEmailAddress)
		yag.send(
		    to=receiver,
		    subject=subject,
		    contents=body, 
		    attachments='./open_timeslots.csv'
		)
		print("Sending Email.......DONE")

	def bookARoadTest(self):

		self.url = "https://drivetest.ca/book-a-road-test/booking.html#/validate-driver-email"
		if self.verify==True:
			self.url = "https://drivetest.ca/book-a-road-test/booking.html#/verify-driver"

		# chrome Options
		options = Options()
		options.add_argument("--window-size=1420,1080")
		options.add_experimental_option("detach", True) # keep window open after the method is done	
		if self.headless==True:
			options.add_argument("--headless")
		if self.headless==True:
			options.add_argument("--incognito")		

		driver = webdriver.Chrome(self.driver_path, options=options)
		driver.get(self.url)

		# wait maximum 10 seconds for elements
		ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)		
		wait = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)
		

		### filling the forms ###
		licNum = wait.until(EC.element_to_be_clickable((By.ID, 'licenceNumber')))		
		licExpDate = wait.until(EC.element_to_be_clickable((By.ID, 'licenceExpiryDate')))
		licNum.send_keys(self.licenceNumber)
		licExpDate.send_keys(self.expiryDate)
		# if we are ooking for the first time and not editing existing one	
		if self.verify==False:
			emailAddress = wait.until(EC.element_to_be_clickable((By.ID, 'emailAddress')))		
			confirmEmailAddress = wait.until(EC.element_to_be_clickable((By.ID, 'confirmEmailAddress')))		
			emailAddress.send_keys(self.emailAddress)
			confirmEmailAddress.send_keys(self.emailAddress)


		time.sleep(4)						
		regSubmitBtn =wait.until(EC.element_to_be_clickable((By.ID, 'regSubmitBtn')))
		regSubmitBtn.click()

		if self.verify==True:
			reschedule_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="8488627"]/div/div/div[2]/div/span[2]/button')))
			reschedule_btn.click()
			reschedule2_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page_book_a_road_test_booking"]/div[4]/div/div/div/div/div/div[4]/button[1]')))
			reschedule2_btn.click()

		else:
			if self.testType == 'G2':
				wait.until(EC.element_to_be_clickable((By.ID, 'G2btn'))).click()
			elif self.testType == 'G':
				wait.until(EC.element_to_be_clickable((By.ID, 'Gbtn'))).click()
			continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="booking-licence"]/div/form/div/div[4]/button')))
			continue_btn.click()
		
		open_timeslots = pd.DataFrame(columns=['Location', 'Day', 'Month', 'Time'])

		# select 1 location
		for location in self.location:

			print("Searching in location: "+str(location))
			# Select the location
			location_btn = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@title=\"'+str(location)+'\"]')))
			time.sleep(1)					
			location_btn.click()
			print("location clicked")

			continue_btn2 = driver.find_element_by_xpath('//*[@id="booking-location"]/div/div/form/div[2]/div[2]/button')
			driver.execute_script("arguments[0].scrollIntoView();", continue_btn2)			
			time.sleep(1)
			# clicking continue is only needed for the first location
			if location==self.location[0]:
				continue_btn2.click()
				print("continue_btn2 clicked")
			time.sleep(2)		

			for month in self.months:
				# for desired dates, look into availability and save date and time
				datetime_object = datetime.datetime.strptime(month, "%b")
				month_number = datetime_object.month
				dates_in_a_month = calendar.monthrange(year, month_number)[1]
				dates = np.arange(1,dates_in_a_month)

				for date in dates:
					print("date = "+str(date))
					# date_btn = driver.find_element_by_xpath('//*[@title='+str(date)+']')
					date_btn = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@title='+str(date)+']'))) 
					if (date_btn.get_attribute('tabindex') == "0" and self.write==True): # active date slot for selecting has tabindex=0
						date_btn.click()
						# Continue
						continue_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="calendarSubmit"]/button')))
						continue_btn3.click()
						# select available dates
						time.sleep(3)
						time_btns = driver.find_elements_by_xpath('//label[starts-with(@id,"btn")]')
						for time_btn in time_btns:
							hour = time_btn.text
							# store all timeslotes
							print("Found an open slot (day, month, hour): " + str(date) + ", " + str(month) + ", " + str(hour))
							open_timeslots = open_timeslots.append({'Location':location, 'Day':date, 'Month':month, 'Time':hour}, ignore_index=True)
						# scroll to the top
						date_btn_1 = driver.find_element_by_xpath('//*[@title='+str(1)+']')
						time.sleep(1)						
						driver.execute_script("arguments[0].scrollIntoView(true);", date_btn_1)
						time.sleep(2)						
				# check next month
				time.sleep(1)
				continue_btn2 = driver.find_element_by_xpath('//*[@id="booking-location"]/div/div/form/div[2]/div[2]/button/span')						
				driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn2)					
				nextMonth_btn = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@title="next month"]')))	
				nextMonth_btn.click()

				# wait till first date of preivoius month is staled
				wait.until(EC.staleness_of(date_btn))

			driver.execute_script("window.scrollTo(0, -100)") 							

		# store all open timeslots into a csv file
		open_timeslots.to_csv('./open_timeslots.csv', index=False)

		# quit drivetest.ca booking page
		quit_btn = driver.find_element_by_xpath('//*[@title="Quit"]')
		quit_btn.click()

		# close the chrome driver window
		driver.quit()

		# send an email with the list of open timeslots attached
		if self.sendEmail:
			self.sendEmail()
	