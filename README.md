# SchoologyGradeChecker
**Schoology Grade Scraper - Returns CSV of Grades**
▶️Currently Supports Cabell Schoology◀️

Python Schoology Script to retrieve student grades.

## Necessary Libraries
- Beautiful Soup
- Selenium
- Pandas
- Numpy
- webdrivermanager

# Setup
- Install required python libraries
pip install -r requirements.txt
- Download Schoologygrades.py


# Running

## Using terminal
- Run in terminal with arguments of **username** and **password**
- python SchoologyGradeChecker.py **username** and **pasword**
- Output of schoologygrades.csv file

## Using in python file
```python
import SchoologyGradeChecker
SchoologyGradeChecker.main(username, password)
df = pd.read_csv('./schoologygrades.csv')
```


# Debugging
- Finishes but no data in the csv
  Caused by dataParentP1 not being set correctly for the semester
  
