#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from datetime import date
import datetime
from datetime import timedelta  
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

#Populate yourFilePath with your file path...

path = r'/Daily_Reports/'

#/Users/gcalder2/OneDrive - University of Edinburgh

#Determine Env Variables
tDt = date.today()
yDt = tDt - timedelta(days=1)
tDt_human = datetime.datetime.now().strftime('%A %d %B %Y')
tDtx = datetime.datetime.today()

#Make Some Soup 
url = "https://www.gov.scot/publications/coronavirus-covid-19-tests-and-cases-in-scotland/"
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')
text = soup.get_text()
rows = soup.find_all('tr')
for row in rows:
    row_td = row.find_all('td')
str_cells = str(row_td)
cleantext = BeautifulSoup(str_cells, "lxml").get_text()
list_rows = []
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '',str_cells))
    list_rows.append(clean2)

df_0 = pd.DataFrame(list_rows)
df_1 = df_0[0].str.split(', ', expand=True)
df_1[0] = df_1[0].str.strip('[')
df_1.head(10)
col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)
df_2 = pd.DataFrame(all_header)
df_3 = df_2[0].str.split(',', expand=True)
frames = [df_3, df_1]
df_4 = pd.concat(frames)
df_5 = df_4.rename(columns=df_4.iloc[0])
df_6 = df_5.dropna(axis=0, how='any')
df_7 = df_6.drop(df_6.index[0])

all_header.append(cleantext2)
df_2 = pd.DataFrame(all_header)
df_3 = df_2[0].str.split(',', expand=True)
frames = [df_3, df_1]
df_4 = pd.concat(frames)
df_5 = df_4.rename(columns=df_4.iloc[0])
df_6 = df_5.dropna(axis=0, how='any')
df_7 = df_6.drop(df_6.index[0])
    
df_fix_1 = df_5.iloc[0:17, 0:4]
df_fix_2 =  df_fix_1.drop([0])
df_6 = df_fix_2.dropna(axis=0, how='any')
df_7 = df_6
df_7.columns = ['Health_Board','Positive_Cases','Hospitalisations','ICU']
df_7

df_7 = df_7.replace('\n','', regex=True)
df_7 = df_7.replace('],','', regex=True)
df_7 = df_7.replace('\**','',regex=True)
df_7 = df_7.iloc[0:17, 0:2]

#Remove Commas
df_7['Positive_Cases'] = df_7['Positive_Cases'].str.replace(',','')
df_7['Positive_Cases'] = df_7['Positive_Cases'].astype(int)
df_7.iloc[0,0] = 'Ayrshire'
df_7 = df_7.transpose()

#Sort header out
new_header_7 = df_7.iloc[0] 
df_7 = df_7[1:] 
df_7.columns = new_header_7

#Combine Grampian, Shetland and Orkney
df_7['Grampian'] = df_7.loc[:,'Grampian'] +  df_7.loc[:,'Shetland'] + df_7.loc[:,'Orkney']
df_7 = df_7.drop('Shetland', 1)
df_7 = df_7.drop('Orkney', 1)
df_7 = df_7.rename({'Grampian': 'Grampian, Shetland and Orkney'}, axis=1)

#Combine Highland and Western Isles
df_7['Highland'] = df_7.loc[:,'Highland'] +  df_7.loc[:,'Eileanan Siar (Western Isles)']
df_7 = df_7.drop('Eileanan Siar (Western Isles)', 1)
df_7 = df_7.rename({'Highland': 'Highland and Western Isles'}, axis=1)
df_7b = df_7.transpose()
df_7b = df_7b.reset_index()
df_7b.iloc[0,0] = 'Ayrshire'

#Import Yesterday's Case Data
df_yDt = pd.read_excel('{}SARS-Cov-2-Scotland-{}_raw.xlsx'.format(path,yDt), sheet_name='Total Cases')
#Drop last two and first column
df_yDt = df_yDt.drop(df_yDt.columns[[0,-1,-2],], axis=1) 


#Change date format
mapper = lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime.datetime) else x
df_yDt.columns = df_yDt.columns.map(mapper)
#Merge today's data with yesterday's
df_x = pd.merge(df_yDt, df_7b, how = 'right')
df_x = df_x.rename(columns={"Positive_Cases":(tDt)})


#Deal with DateTime formatting
df_x.columns = df_x.columns.map(mapper)

#Deal with nulls
df_x2=df_x.fillna(0)

#Total sum per column (except Health_Board)
df_x2.loc['Total']= df_x.iloc[:, 1:].sum(axis=0)
df_x2 = df_x2.replace(np.nan, 'Total', regex=True)

#Process data for plotting
df_plot = df_x2.head(n=0)
df_plot = df_x2.tail(n=1)

#Drop Health_Board Column
df_plot2 = df_plot.drop(['Health_Board'], axis=1)
df_plot2 = df_plot2.transpose()

#Import Yesterday's Death Data
df_Deaths = pd.read_excel ('{}SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(path,yDt), sheet_name='Deaths') 
#Drop first column
df_Deaths = df_Deaths.drop(df_Deaths.columns[[0],], axis=1) 
df_Deaths.columns = df_Deaths.columns.map(mapper)
#Report deaths
result_3 = re.search('(.*) patients who tested positive have died', text)
total_deaths = (result_3.group(1))
total_deaths = str(result_3.group(1))
total_deaths = total_deaths.replace(",","")
tot_deaths = int(total_deaths)
#Deaths Calculations
#tot_deaths
old_deaths = df_Deaths.iloc[1,-1]
new_deaths = tot_deaths-old_deaths
#new_deaths
dict_1 = {new_deaths:'Deaths_New', tot_deaths: 'Deaths_Cum' }
df_Deaths[tDt] = dict_1
#Transpose
df_Deaths_Tran = df_Deaths.transpose()
#Calculate % increase of deaths
m = round((new_deaths/old_deaths)*100,1)
#Sort out formatting for deaths for future imports
df_DeathsX = df_Deaths
df_Deaths_XTran = df_Deaths.transpose()
#Plot cases and deaths together
df_Deaths2 = df_Deaths.drop(0)
df_Deaths3 = df_Deaths2.transpose()
df_Deaths4 = df_Deaths3.drop(['Date'])
df_Deaths4.columns = ['Deaths']
#Merge Death Data and Case Data
df_casesDeaths = pd.merge(df_plot2, df_Deaths4, how = 'left',  left_index=True, right_index =True)
df_casesDeaths = df_casesDeaths.rename(columns={"Total":('Cases')})

#Remove year from date
df_casesDeaths = df_casesDeaths.reset_index()
df_casesDeaths = df_casesDeaths.rename({'index': 'Dates'}, axis=1)
df_casesDeaths.Dates = df_casesDeaths.Dates.str[5:]
stringDt = str(tDt)
stringDt = stringDt[5:]
df_casesDeaths.iloc[-1,0] = stringDt
df_casesDeaths = df_casesDeaths.set_index('Dates')


#Find number of new cases today, by Health_Board
df_Old = df_x2.iloc[:, [0,-2]] 
df_New = df_x2.iloc[:, [0,-1]] 
df_Join = pd.merge(df_Old, df_New, how = 'right', on = ['Health_Board'])

df_Join.to_excel('{}COVID-19_Scotland_CPT_DPC_{}.xlsx'.format(path,tDt), sheet_name='CPT & DPC')

df_Join['newCases'] = (df_Join.iloc[:,-1]-df_Join.iloc[:,-2])

#What is the total increase in case numbers across the whole country?
x = df_x2.iloc[-1,-2]
y = df_x2.iloc[-1,-1]
y = int(y)
z = int(y-x)
p = (z/x)*100
p2 = round(p,1)
yb = int(y)


result_2 = re.search('A total of (.*) people in Scotland have been tested', text)
total_tests = (result_2.group(1))
total_tests = total_tests.replace(',','')
tot = int(total_tests)

#Calculate proportion of positive tests
pos = round((y/tot)*100,1)

#Increase per row with total and allowing new areas
df_x2['Increase'] =  (df_x2.iloc[:, -1] - df_x2.iloc[:, -2])
df_x2['pIncrease'] =  (df_x2['Increase'] / df_x2.iloc[:, -3]) * 100

#Set value of Increase and pIncrease
df_x2.loc[['Total'], ['Increase']] = z
df_x2.loc[['Total'], ['pIncrease']] = p2
df_Deaths.columns = df_Deaths.columns.map(mapper)
#Transpose data 
df_xT = df_x2.transpose()
df_tDt = df_x2
df_tDt.columns = df_tDt.columns.map(mapper)

#****************************************Calculate Per Capita Metrics***********************************************

# Bring in population size data
df_pop = pd.read_csv('{}Scotland_Population_Size_By_HealthBoard_Grouped.csv'.format(path))
#Set string for Ayshire and Arran
df_pop.iloc[0,0] = 'Ayrshire'

#Merge pop data with case data
df_pop2 =  pd.merge(df_tDt, df_pop, how = 'right').sort_values('Health_Board')
df_pop2 = df_pop2.fillna(0)

#Drop last two and first column
df_pop2x = df_pop2.drop(df_pop2.columns[[-2,-3]], axis=1) 
df_pop2x = df_pop2x.transpose()

#Sort header out
new_header = df_pop2x.iloc[0] 
df_pop2x = df_pop2x[1:] 
df_pop2x.columns = new_header


#Drop troublesome last column
df_pop2x = df_pop2x.drop(df_pop2x.columns[-1], axis=1) 
#Transpose back to perform per capita calculations
df_pop3x = df_pop2x.transpose()
#Reset the index after tranposing
df_pop3x = df_pop3x.reset_index()
#Add increase back in so we can calculate incidence
df_pop3x['Increase'] =  (df_pop3x.iloc[:, -2] - df_pop3x.iloc[:, -3])
#Calculate Per Capita Metrics
df_pop3x['Prevalence'] =  (((df_pop3x.iloc[:,-3] )/(df_pop3x.loc[:,'Pop_Size']))*10000)
df_pop3x['Incidence'] =  (((df_pop3x.loc[:, 'Increase'])/(df_pop3x.loc[:,'Pop_Size']))*10000)

#Export raw case and death data
df_DeathsX.to_excel('{}/SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(path,tDt), sheet_name='Deaths') 
df_x2.to_excel('{}/SARS-Cov-2-Scotland-{}_raw.xlsx'.format(path,tDt), sheet_name='Total Cases')
df_Deaths_XTran.to_excel('{}/SARS-Cov-2-Scotland-{}_deaths_trans.xlsx'.format(path,tDt), sheet_name='Deaths')
df_xT.to_excel('{}/SARS-Cov-2-Scotland-{}_cases_trans.xlsx'.format(path,tDt), sheet_name='Total Cases')


#Import Today's Case Data
df_tDt = pd.read_excel ('{}SARS-Cov-2-Scotland-{}_Raw.xlsx'.format(path,tDt), sheet_name='Total Cases')
#Drop last two columns and last row
df_multi = df_tDt.drop(df_tDt.columns[[0,-1,-2],], axis=1) 
df_multi.drop(df_multi.tail(1).index,inplace=True) 
df_multi.columns = df_multi.columns.map(mapper)
df_multi2 = df_multi.transpose()
#Sort header out
new_header = df_multi2.iloc[0] 
df_multi3 = df_multi2[1:] 
df_multi3.columns = new_header

#Sort Columns Alphabetically to Retain Consistent Colouring in Plot
df_multi3 = df_multi3.reindex(sorted(df_multi3.columns), axis=1)
#Remove year from date
df_multi3 = df_multi3.reset_index()
df_multi3 = df_multi3.rename({'index': 'Dates'}, axis=1)
df_multi3.Dates = df_multi3.Dates.str[5:]
df_multi3 = df_multi3.set_index('Dates')

df_prevx = df_pop3x.transpose()
#Sort header out
new_header2 = df_prevx.iloc[0] 
df_prevx = df_prevx[1:] 
df_prevx.columns = new_header2

#Line Graph of Prevalence by Health Board Over Time
df_prevx.drop(df_prevx.tail(3).index,inplace=True)
df_prevx2 = df_prevx.iloc[:,0:].div(df_prevx.iloc[-1,:], axis=1)
df_prevx3 = df_prevx2 * 10000
df_prevx3.drop(df_prevx3.tail(1).index,inplace=True) 
df_prevx3 = df_prevx3.reindex(sorted(df_prevx3.columns), axis=1)

df_prevx3 = df_prevx3.reset_index()
df_prevx3 = df_prevx3.rename({'index': 'Dates', 'Total': 'Average'}, axis=1)
df_prevx3.Dates = df_prevx3.Dates.str[5:]
df_prevx3.iloc[-1,0] = stringDt
df_prevx3 = df_prevx3.set_index('Dates')

#Incidence
df_incdx = df_pop3x.transpose()
#Sort header out
new_header2 = df_incdx.iloc[0] 
df_incdx = df_incdx[1:] 
df_incdx.columns = new_header2
df_incdx = df_incdx.tail(1)

#Cases Per Test  and Deaths Per Cases (CPT & DPC)
df_CPT_Old = pd.read_excel('{}COVID-19_Scotland_CPT_DPC_{}.xlsx'.format(path,yDt))
#df_CPT_Old['Date'] = df_CPT_Old['Date'].dt.date
data_CPT_new = {'Date': [tDt], 'Cases': [y], 'Deaths': [tot_deaths], 'Tests': [tot], 'CPT': [round(y/tot,5)], 'DPC': [round(tot_deaths/y,5)]}
df_CPT_New = pd.DataFrame(data=data_CPT_new)
df_CPT = df_CPT_Old.append(df_CPT_New)
df_CPT = df_CPT.reset_index()
df_CPT['Date']= pd.to_datetime(df_CPT['Date']) 
#Drop old index column
df_CPT2 = df_CPT.drop(df_CPT.columns[0,], axis=1)

#Export sheets
df_CPT_x = df_CPT2[['Date','Tests','Cases','Deaths','CPT','DPC']]
#df_CPT_x['Date'] = df_CPT_x['Date'].dt.strftime('%Y-%m-%d')
df_CPT_x.to_excel(('{}COVID-19_Scotland_CPT_DPC_{}.xlsx'.format(path,tDt)), sheet_name='CPT & DPC')


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('{}COVID-19_Scotland_data_all_{}.xlsx'.format(path,tDt), engine='xlsxwriter')
# Write each dataframe to a different worksheet in same file
df_Deaths_XTran.to_excel(writer, sheet_name='Scotland Deaths')
df_xT.to_excel(writer, sheet_name = 'Cases By Health Board')
df_prevx3.to_excel(writer, sheet_name = 'Cumulative Incidence Grouped')
df_incdx.to_excel(writer,sheet_name= 'Incidence by Health Board', index=False)
df_CPT_x.to_excel(writer,sheet_name='CPT & DPC')
writer.save()


# In[ ]:





# In[ ]:




