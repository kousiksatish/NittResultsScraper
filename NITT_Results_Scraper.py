from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import MySQLdb
import sys
from bs4 import BeautifulSoup

class RollnoError(Exception):
	def __init__(self, mismatch):
		Exception.__init__(self,mismatch)

for arg in sys.argv:
	print arg

rangeInput = sys.argv[1]
moreInfo = sys.argv[2]

start = unicode(rangeInput[:9])
end = unicode(rangeInput[12:])

driver = webdriver.Firefox()
driver.get("http://www.nitt.edu/prm/nitreg/ShowRes.aspx")

rollno = start

print 'GPA Check started'
completeData = []
while rollno<=end:
	elem = driver.find_element_by_name("TextBox1")
	elem.clear()
	elem.send_keys(rollno)
	elem.send_keys(Keys.RETURN)
	src=BeautifulSoup(driver.page_source,"html.parser")
	viewState=src.find('input', attrs = {'name':'__VIEWSTATE'})
	error = 0
	try:
		if len(viewState['value']) == 536:
			error = 1
			raise RollnoError('Rollno viewstate error')

		# Current Rollno data
		currRollnoData = {"Rollno" : rollno}
		
		selectBox = Select(driver.find_element_by_name('Dt1'))
		selectBox.select_by_visible_text("MAY-2016(REGULAR)")
		src = BeautifulSoup(driver.page_source,"html.parser")

		# Scrap name of rollno
		name=src.find_all('span',id='LblName')
		for data in name:
			currRollnoData['Name'] = unicode(data.string)

		# Scrap GPA of rollno
		gp=src.find_all('span',id='LblGPA')
		for data in gp:
			gpa=data.string
			currRollnoData['GPA'] = gpa
		# entries variable to store each variable of the table
		entries = []

		# Scrap the table
		tables = src.find_all('table', id='DataGrid1')		
		for table in tables:
			tr_tags = table.find_all('tr', attrs = {'class' : ['DataGridItem', 'DataGridAlternatingItem']})
			for tr in tr_tags:
				myList = []
				td_tags = tr.find_all('td')
				for td in td_tags:
					myList.append(unicode(td.string))
				data = { "S.No" : myList[0],
					"CourseCode" : myList[1],
					"CourseName" : myList[2],
					"Credit" : myList[3],
					"Grade" : myList[4],
					"AttGrade" : myList[5]}
				entries.append(data)
		currRollnoData['Entries'] = entries
		print rollno + ': Success!'
	except RollnoError as x:
		print rollno + ': ' + unicode(x)
	except Exception as e:
		# print rollno + ': Other error' + unicode(e)
		print rollno + ': Other error' + unicode(e)
	if error!=1:
		completeData.append(currRollnoData)
	rollno = int(rollno) + 1
	rollno = unicode(rollno)

f = open(moreInfo, 'w')
f.write(moreInfo + '\n' + rangeInput + '\n' + repr(completeData))
f.close
driver.quit()