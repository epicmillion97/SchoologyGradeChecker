#Created by https://github.com/epicmillion97
#Issues/Comments on Github



from bs4 import BeautifulSoup
import time
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import re
import argparse
import pandas as pd
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
#Currently Supports Chrome

schoolurl = 'https://***school***.schoology.com' # edit school to your district


def selenium_get_source(usernamekey, passwordkey):
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument('--headless') # runs in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3") # removes webdriver log messages
    chrome_options.add_argument("--disable-gpu") # disables gpu
    chrome_options.add_argument("--disable-software-rasterizer")  # removes gpu GL message
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # removes DevTools Listening
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    #firstarg=sys.argv[1]
    #secondarg=sys.argv[2]
    driver.get(schoolurl) # school schoology district login through microsoft azure


    time.sleep(1)
    username = driver.find_element_by_id("userNameInput")
    password = driver.find_element_by_id("passwordInput")
    signin = driver.find_element_by_id('submitButton')
    username.send_keys(usernamekey)
    password.send_keys(passwordkey)
    time.sleep(.25)
    signin.click()
    driver.get("{}/courses".format(schoolurl))
    driver.implicitly_wait(10)
    courses = driver.find_elements_by_tag_name('a')

    coursehref = [] # creates blank list for course href links
    for i in courses:
        href = i.get_attribute('href') # gets the href attribute of the element
        coursehref.append(href) # adds href link to coursehref

    coursehref = [x for x in coursehref if x != None] # cleans None type out of list
    coursehref = [i for i in coursehref if i.startswith('{}/course/'.format(schoolurl))] # list comprehension for elements that start with specific link
    coursehref1 = []

    for i in coursehref:
        coursehref1.append(i + '/student_grades')

    # retrieves html source for each course
    html_list = []
    for i in coursehref1:
        driver.get(i)
        driver.implicitly_wait(10)
        html = driver.page_source
        html_list.append(html)
    driver.quit()
    return html_list
    # finishes Selenium webscraping




def parsing_table(dataParentIdP1,html):
    soup = BeautifulSoup(html, 'html.parser')
    # takes html source for a course and returns grades
    grade_table = soup.find('table', {'role' : 'presentation'})
    for table in grade_table.find_all('tbody'):
        #dataParentIdP2 = table.find('tr', {'data-parent-id': "0"}).attrs['data-id'] # old method
        #print(dataParentIdP2)  #old method
        dataParentIdP2 = table.find_all('tr', {'data-parent-id': "0"})
        for section in dataParentIdP2:
            section = section.attrs['data-id']
            #print(section)
            section = section.split('-')
            dataParentId = str(dataParentIdP1) + '-' + str(section[1])

            #dataParentIdP2 = dataParentIdP2.split('-') #old method
            #dataParentId = str(dataParentIdP1) + '-' + str(dataParentIdP2[1]) # old method

            #print(dataParentId)
            rows = table.find_all('tr', {'data-parent-id' : "{}".format(dataParentId)})
            #print(len(rows))
            for row in rows:
                #assignments = row.find('th', class_ = "title-column clickable")

                #for assignment in assignments:
                try:
                    title = row.find('a', {'class' : 'sExtlink-processed'}).text.replace('assignment','').replace('discussion', '').replace('test-quiz', '').replace('Testassessment', '').replace('assessment','').replace('Note', '')
                except:
                    try:
                        title = row.find('span', {'class' : 'infotip hide-qmark sCommonInfotip-processed'}).text.replace('assignment','').replace('discussion', '').replace('test-quiz', '').replace('Testassessment', '').replace('assessment', '').replace('Note','')
                    except:
                        title = 'yeeeeee'
                try:
                    gradeTop = row.find('span', class_ = "rounded-grade").text
                except:
                    try:
                        gradeTop = row.find('span', class_ = "rubric-grade-value").text
                    except:
                        gradeTop = '-'
                try:
                    gradeBottom = row.find('span', class_ = "max-grade").text.replace(' / ', '')
                except:
                    gradeBottom = '-'


                # gets assignment due date
                try:
                    dueDate = row.find('span', class_="due-date").text
                except:
                    dueDate = '69/69/22 11:59pm' # yep 69

                # checks if assignment is submitted
                submitted = row.find('span', class_=re.compile("has-*"))
                if submitted != None:
                    submitted = True
                else:
                    excused = row.find('span', class_="exception-icon excused")
                    if excused != None:
                        submitted = True
                    else:
                        if gradeTop != '-':
                            submitted = True
                        else:
                            submitted = False


                formatedGrade = gradeTop + '/' + gradeBottom # formats grade
                grade =    {'title': title,
                            'formattedGrade': formatedGrade,
                            'dueDate' : dueDate,                    # adds elements to a dict
                            'due' : '',
                            'submitted': submitted,
                            }
                grades.append(grade) # appends grade dict to totalgrades list



def daysUntilDue():
    # calculates time until assignment is due
    for i in range(len(grades)):
        try:
            if grades[i]['dueDate'] == '69/69/22 11:59pm': #yeah 69
                due = 'no date'
                grades[i].update({'due' : due})
            else:
                due = grades[i]['dueDate'].replace('Due ','').replace('pm','')
                due = due.split('/')
                due1 = due[2].split(' ')
                del due[2]
                for x in due1:
                    due.append(x)


                month = due[0]
                day = due[1]
                year = due[2]


                date = datetime.datetime(int(year)+2000,int(month),int(day))
                now = datetime.datetime.now()
                due = (date-now).days
                grades[i].update({'due' : due})
        except:
            pass


def tocsv():
    columns = ['title', 'formattedGrade','dueDate','due','submitted']
    df = pd.DataFrame(grades, columns=columns)
    #print(df) #debugging csv to console
    df.to_csv('schoologygrades.csv', index=False) #Saves csv file


grades = []

def main(username, password):
    dataParentP1 = "900090" # if dataParentId error CHECK THIS LINE AND REFER TO GITHUB DOCUMENTATION
    html_list = selenium_get_source(username, password)
    for source in html_list:
        try:
            parsing_table(dataParentP1, source)
        except:
            pass
    daysUntilDue()
    tocsv()
    print('finished getting grades')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes Schoology and parses the data.')
    parser.add_argument('username',metavar='username', type=str, help='--Schoology Username--')
    parser.add_argument('password', metavar='password', type=str, help='--Schoology Password--')
    args = parser.parse_args()
    main(username = args.username, password = args.password)
