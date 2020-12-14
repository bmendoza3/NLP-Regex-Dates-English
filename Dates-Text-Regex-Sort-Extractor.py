#Imports
import pandas as pd
import re
import numpy as np
from datetime import datetime

#Get the doc
doc = []
with open('doc.txt') as file:
    for line in file:
        doc.append(line)

df = pd.Series(doc) #Save the doc into df variable.

#------------- Utility function ---------------#

def map_mth(date): #Function to replace the text year with number year and group it in format mm dd YYYY
#we create a dictionary with the months to use it later
  mth = dict({'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr':'04', 'May':'05', 'Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'})
  if "/" not in date:
    r_date = re.sub(r'^(\d{2}) ([a-zA-Z]*) (\d{4})$',lambda x: str(x.groups()[1])+' '+str(x.groups()[0])+' '+str(x.groups()[2]),date)
    splitted = r_date.split(' ')
    for indx,i in enumerate(splitted):
        if i in mth:
            splitted[indx] = mth.get(i)
        correct_date = '/'.join(splitted)
    return correct_date
  else:
    return date
    
#--------------- Date extract function -------#

#Works from 1900 to 2099.
#Day-missing dates are considered first day of the month.
#Month-missing dates are considered first month of the year (January or 01).
#Target Date format is mm/dd/yyyy.
#Abreviated years such as 90 and 66 are considered 19's.
 
def date_sorter(df):
    #regex code to detect dates in different formats    
    stest = df.str.findall(r'((?:(?:0?[1-9]|1[012])[/-])(?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)?\d{2}|(?:(?:0?[1-9]|1[012])[/-])?(?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}|(?:(?:0?[1-9]|[12]\d|3[01])[ ]*)?(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)[ ,.]*(?:0?[1-9]|[12]\d{1}|3[01])?[ ,]*(?:19|20)\d{2}|(?:\b)?(?:19|20)\d{2})')
    
    #Due to the nature of the returned value that gives us findall, we need to extract it from the list of len=1
    stest = stest.apply(lambda x: x[0])
    
    #Remove punctuation
    stest = stest.str.replace(r'[,.]', '')
    
    #Replace '-' with '/'
    stest = stest.str.replace('-', '/')
    
    #Get the first 3 letters of the Month (in words)
    stest = stest.str.replace(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)', lambda x: x.groups()[0][:3])
    
    #Add a leading zero to the month in the date format mm/dd/yyyy or mm/yyyy
    stest = stest.str.replace(r'((?:^|\s)[1-9]\/)', lambda x: '0'+str(x.groups()[0]))
    
    #Remove leading characters such as - / captured from typos
    stest = stest.str.replace(r'([^\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ ,.]*(?:0?[1-9]|[12]\d{1}|3[01])?[ ,]*(?:19|20)\d{2})', lambda x: x.groups()[0][1::])
    
    #Add a leading zero to the day in the date format mm/dd/yyyy
    stest = stest.str.replace(r'((?:0?[1-9]|1[012])[/-])([1-9][/-])((?:19|20)?\d{2})', lambda x: str(x.groups()[0]) +'0'+str(x.groups()[1])+str(x.groups()[2]))
   
    #Add the '19' to the abreviated years from the 19's so all the dates are mm/yyyy or mm/dd/yyyy
    stest = stest.str.replace(r'^((?:0[1-9]|1[012])\/)((?:0[1-9]|[12]\d|3[01])\/)(\d{2})$', lambda x: str(x.groups()[0])+str(x.groups()[1])+'19'+str(x.groups()[2]))
    
    #Add missing day to the date in format "Month Year"
    stest = stest.str.replace(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})$', lambda x: str(x.groups()[0])+' 01 '+str(x.groups()[1]))
    
    #Add missing day to the date in format "mm/yyyy"
    stest = stest.str.replace(r'^(\d{2})\/(\d{4})$', lambda x: str(x.groups()[0])+'/01/'+str(x.groups()[1]))
    
    #Add missing day and month to the date in format "yyyy"
    stest = stest.str.replace(r'^(\d{4})$', lambda x: '01/'+'01/'+str(x.groups()[0]))
    
    #Format the date from Month Day Year to mm/dd/yyyy
    stest = stest.apply(map_mth)
    
    #Transform from string to datetime
    stest_dates = pd.to_datetime(stest, format='%m/%d/%Y')
    
    #Sort from earliest to latest
    stest_dates = stest_dates.sort_values()
    
    #Sorted index series
    sr = pd.Series(stest_dates.index.values)
    
    return sr
