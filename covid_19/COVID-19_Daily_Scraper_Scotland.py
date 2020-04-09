#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
#import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
from datetime import date
import datetime
from datetime import timedelta  
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import yagmail
import dropbox
from pylab import rcParams
from matplotlib import rc_params
from cycler import cycler
from ipynb.fs.full.Fx_Send_Daily_Report import send_daily_report

new_prop_cycle = cycler('color', ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf','#FFD700','#000000'])

plt.rc('axes', prop_cycle=new_prop_cycle)
plt.rcParams['axes.facecolor']='white'
plt.rcParams['savefig.facecolor']='white'

#Determine Env Variables
tDt = date.today()
yDt = tDt - timedelta(days=1)
tDt_human = datetime.datetime.now().strftime('%A %d %B %Y')

#Make Some Soup 
url = "https://www.gov.scot/coronavirus-covid-19/"
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
df_1 = df_0[0].str.split(',', expand=True)
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
#df_7.rename(columns={'[Health board': 'Health_Board'},inplace=True)
#df_7.iloc[-1,1]['Positive_Cases'] = df_7['Positive_Cases'].str.strip(']')
#df_7.Health_Board.str.replace("\\n ]", "")
#df_7.Health_Board.strip()
#df_7.Health_Board.str.replace('\\n',' ', regex=True) 
#df_7['Positive_Cases'] = df_7['Positive_Cases'].str.strip(']')
df_7.rename(columns={ df_7.columns[1]: "Positive_Cases" }, inplace = True)
df_7.rename(columns={ df_7.columns[0]: "Health_Board" }, inplace = True)
df_7 = df_7.replace('\n','', regex=True)
df_7 = df_7.replace(']','', regex=True)
df_7 = df_7.replace('\*','',regex=True)
df_7['Positive_Cases'] = df_7['Positive_Cases'].astype(int)

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
#Force Ayrshire and Arran to Ayrshire
df_7b.iloc[0,0] = 'Ayrshire'


#Import Yesterday's Case Data
df_yDt = pd.read_excel(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_raw.xlsx'.format(yDt), sheet_name='Total Cases')
#Drop last two and first column
cols = [0,-1,-2]
df_yDt = df_yDt.drop(df_yDt.columns[[cols],], axis=1) 


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
df_Deaths = pd.read_excel (r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(yDt), sheet_name='Deaths') 
#Drop first column
df_Deaths = df_Deaths.drop(df_Deaths.columns[[0],], axis=1) 
df_Deaths.columns = df_Deaths.columns.map(mapper)
#Report deaths
result_3 = re.search('(.*) patients who tested positive have died', text)
total_deaths = (result_3.group(1))
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
txt_5 = "The death toll is currently {}.\nThe number of new deaths reported today was {}, which represents a {}% increase on yesterday.".format(total_deaths, new_deaths, m)
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

#Plot the epiCurve and deathCurve

#Set figure size for plotting
rcParams['figure.figsize'] = 11, 11
#Plot
plot1 = df_casesDeaths.plot.line(rot=0, fontsize = 14)
plot1.set_title('COVID-19 Cases and Deaths in Scotland', size = 16)
plot1.set_ylabel("Cumulative Number", size = 16)
plot1.set_xlabel("Date", size = 14)
plot1.legend(loc = 'upper left', facecolor = '#F7F7F7' ,prop = {'size':14})
fig = plot1.get_figure()
fig.savefig(r'filepath\Daily_Reports\COVID-19_Scotland_casesDeaths_Plot_{}.png'.format(tDt),dpi=400 , bbox_inches="tight")
#fig.show()


#Find number of new cases today, by Health_Board
df_Old = df_x2.iloc[:, [0,-2]] 
df_New = df_x2.iloc[:, [0,-1]] 
df_Join = pd.merge(df_Old, df_New, how = 'right', on = ['Health_Board'])
df_Join['newCases'] = (df_Join.iloc[:,-1]-df_Join.iloc[:,-2])

#What is the total increase in case numbers across the whole country?
x = df_x2.iloc[-1,-2]
y = df_x2.iloc[-1,-1]
y = int(y)
z = int(y-x)
p = (z/x)*100
p2 = round(p,1)

#Remove trailing zero
yb = int(y)

#Find tests
result_2 = re.search('A total of (.*) people in Scotland have been tested', text)
total_tests = (result_2.group(1))
total_tests = total_tests.replace(',','')
tot = int(total_tests)

txt_1 = "The total number of cases is currently {}.\nThe number of new cases today is {}, which represents a {}% increase on yesterday.".format(yb,z,p2)


#Calculate proportion of positive tests
pos = round((y/tot)*100,1)

txt_2 = "\n\nTests:\nThe total number of tests reported is {}.\nThe total number of positive cases to date is {}. \nThe percentage of tests which were positive is currently {}%.".format(tot,y,pos)


#Increase per row with total and allowing new areas
df_x2['Increase'] =  (df_x2.iloc[:, -1] - df_x2.iloc[:, -2])
df_x2['pIncrease'] =  (df_x2['Increase'] / df_x2.iloc[:, -3]) * 100
#Remove total row so that we can report biggest increase by region, not overall
df_x2b = df_x2.iloc[:-1]
#What is the largest increase in case numbers (in absolute and % terms)
Inc_max = (df_x2b['Increase'].max())
pInc_max = (df_x2b['pIncrease'].max()) 
# Where did these increases occur? 
Inc_maxLoc = list(df_x2b['Health_Board'][df_x2b.Increase == df_x2b.Increase.max()]) 
pInc_maxLoc = list(df_x2['Health_Board'][df_x2.pIncrease == df_x2.pIncrease.max()])      
#Convert to int and return max value
Inc_max = int(Inc_max) 
pInc_max2 = round(pInc_max,0)
pInc_max2 = str(pInc_max2)
pInc_max2 = pInc_max2.rstrip(".0")

#Manual Override for max increase (%) and location. Need to update this part of the code to deal with the grouped healthboards.
#pInc_max2 = 18
#pInc_maxLoc = 'Fife'

txt_4 = "The largest increase in cases in absolute terms by health board was {} cases, which occurred in {}.\nThe largest relative increase in cases was {}%, which occurred in {}.".format(Inc_max, Inc_maxLoc, pInc_max2, pInc_maxLoc)

#Set value of Increase and pIncrease
df_x2.loc[['Total'], ['Increase']] = z
df_x2.loc[['Total'], ['pIncrease']] = p2
df_Deaths.columns = df_Deaths.columns.map(mapper)
#Transpose data 
df_xT = df_x2.transpose()


#**********************Fastest Doubling Time By Health_Board *****************************************************
#This is manually populated using a calculator built in excel at the moment. Doubling time function is in development.
txt_4b = "The fastest doubling time for cases over the past 7 days was XXX days, which occurred in YYY."   


#Doubling time calculations

# ***************************************   Cases ****************************************

#Set date value for lookback

dx_Dt = tDt - timedelta(days=7)

#watch out for date (using yDt for dev, should be tDt in prod)
df_tDt = df_x2
df_tDt.iloc[0,0] = 'Ayrshire'

#Change Datetime Format
df_tDt.columns = df_tDt.columns.map(mapper)

#Drop columns
cols = [0,1,-1,-2]
df_tDt= df_tDt.drop(df_tDt.columns[[cols],], axis=1) 


df_tDt = df_x2
cols = [0,-1,-2]
df_tDt_Total = df_tDt.drop(df_tDt.columns[[cols],], axis=1) 
df_tDt_Total = df_tDt_Total.tail(1)
#Set Date Values
t1 = dx_Dt
t2 = tDt
#Calculate index position of dates
z1 = -(abs((tDt - t1).days)+1)
z2 = -(abs((tDt - t2).days)+1)
#Return corresponding cases numbers for dates selected
q1 = df_tDt_Total.iloc[0][z1]
q2 = df_tDt_Total.iloc[0][z2]
tx = abs((t2 - t1).days)
qx = np.log(q2/q1)
ln2 = np.log(2)
Td_C = round(tx * (ln2/qx),1)
txt_Dt_Cases = ('The doubling time for the number of cases over the past 7 days was {} days.'.format(Td_C))
#txt_Dt_Cases

# ***************************************   Deaths ****************************************

#df_Deaths2
#Set Date Values
t1 = dx_Dt
t2 = tDt

#Calculate index position of dates
z1 = -(abs((tDt - t1).days)+1)
z2 = -(abs((tDt - t2).days)+1)

#Return corresponding cases numbers for dates selected
q1 = df_Deaths2.iloc[0][z1]
q2 = df_Deaths2.iloc[0][z2]

tx = abs((t2 - t1).days)
qx = np.log(q2/q1)
ln2 = np.log(2)
Td_D = round(tx * (ln2/qx),1)

txt_Dt_Deaths = ('The doubling time for deaths over the past 7 days was {} days.'.format(Td_D))

#txt_Dt_Deaths



#****************************************Calculate Per Capita Metrics***********************************************

# Bring in population size data
df_pop = pd.read_csv(r"C:\Users\gcalder2\Daily_Reports\Scotland_Population_Size_By_HealthBoard_Grouped.csv")
#Set string for Ayshire and Arran
df_pop.iloc[0,0] = 'Ayrshire'

#Merge pop data with case data
df_pop2 =  pd.merge(df_tDt, df_pop, how = 'right').sort_values('Health_Board')
df_pop2 = df_pop2.fillna(0)

#Drop last two and first column
cols = [-2,-3]
df_pop2x = df_pop2.drop(df_pop2.columns[cols], axis=1) 
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

#What is the largest case prevalence and case incidence
prevMax = round(df_pop3x['Prevalence'].max(),1)
incdMax = round(df_pop3x['Incidence'].max(),1)

# Where did these increases occur? 
prevMaxLoc = list(df_pop3x['Health_Board'][df_pop3x.Prevalence == df_pop3x.Prevalence.max()]) 
incdMaxLoc = list(df_pop3x['Health_Board'][df_pop3x.Incidence == df_pop3x.Incidence.max()])
txt_6 = "The highest incidence over the last day was {}, which occurred in {}. \nThe highest cumulative incidence is {}, which is in {}. ".format(incdMax, incdMaxLoc, prevMax, prevMaxLoc)

txt_all = "Deaths:\n{}\n{}\n\nCases:\n{}\n{}\n\nCases per capita (measured per 10,000 head of population):\n{}\n\nHealth Boards: \n{}\n{}".format(txt_5, txt_Dt_Deaths, txt_1, txt_Dt_Cases, txt_6, txt_4, txt_4b)

characters_to_remove = "[]'" 
for character in characters_to_remove:
    txt_all = txt_all.replace(character,"")  

#Export raw case and death data
df_DeathsX.to_excel(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(tDt), sheet_name='Deaths') 
df_x2.to_excel(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_raw.xlsx'.format(tDt), sheet_name='Total Cases')
df_Deaths_XTran.to_excel(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_deaths_trans.xlsx'.format(tDt), sheet_name='Deaths')
df_xT.to_excel(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_cases_trans.xlsx'.format(tDt), sheet_name='Total Cases')

#line graph of cases by health board

#Set figure size for plotting
rcParams['figure.figsize'] = 11, 11

#Import Today's Case Data
df_tDt = pd.read_excel (r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_Raw.xlsx'.format(tDt), sheet_name='Total Cases')
#Drop last two columns and last row
cols = [0,-1,-2]
df_multi = df_tDt.drop(df_tDt.columns[[cols],], axis=1) 
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

#Plot
plot2 = df_multi3.plot.line(rot=0, fontsize = 14)
plot2.set_title('COVID-19 Cases By Health Board', size = 16)
plot2.set_ylabel("Cumulative Number of Cases", size = 16)
plot2.set_xlabel("Date", size = 14)
plot2.legend(loc = 'upper left', facecolor = '#F7F7F7', prop = {'size':14})
fig2 = plot2.get_figure()
fig2.savefig(r'filepath\Daily_Reports\COVID-19_Scotland_CasesHealthBoard_Plot_{}.png'.format(tDt),dpi = 400, bbox_inches="tight")
#fig2.show()
df_prevx = df_pop3x.transpose()
#Sort header out
new_header2 = df_prevx.iloc[0] 
df_prevx = df_prevx[1:] 
df_prevx.columns = new_header2

#No need to combine healthboards as already done upstream
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

#Plot
plot3 = df_prevx3.plot.line(rot=0)
plot3.set_title('Cumulative Incidence of COVID-19 Over Time',size = 16)
plot3.set_ylabel("Cases Per 10k Population", size = 14)
plot3.set_xlabel("Date", size = 14)
plot3.legend(loc = 'upper left', facecolor = '#F7F7F7', prop = {'size':14})
#ax = plt.gca()
#fig, ax = plt.subplots()
#ax.set_prop_cycle('color', palettable.colorbrewer.qualitative.Dark2_8.mpl_colors)
fig3 = plot3.get_figure()
fig3.savefig(r'filepath\Daily_Reports\COVID-19_Scotland_cumIncidence_timeSeries_Plot_{}.png'.format(tDt),dpi = 400,bbox_inches="tight")

#Bar Chart

df_bar = df_prevx2.reset_index()
df_bar.drop(df_bar.tail(1).index,inplace=True) 
df_bar2 = df_bar.tail(1)
df_bar2 = df_bar2.rename({'index': 'Dates', 'Total': 'Average'}, axis=1)
#df_bar2.Dates = df_bar2.Dates.str[5:]
df_bar2 = df_bar2.set_index('Dates')
df_bar3 = df_bar2 * 10000
df_bar4 = df_bar3.transpose()

#Plot

rcParams['figure.figsize'] = 14, 14
rcParams.update({'font.size': 14})

plot4 = df_bar4.plot.bar(align = 'center', width = 0.8, rot = 75)
plot4.set_title('Cumulative Incidence of COVID-19 {}'.format(tDt), size = 16)
plot4.set_ylabel("Cases Per 10k Population", size = 16)
plot4.set_xlabel("")
plot4.get_legend().remove()
#plot4.set_xticklabels([])
fig4 = plot4.get_figure()
fig4.savefig(r'filepath\Daily_Reports\COVID-19_Scotland_cumIncidence_BarChart_{}.png'.format(tDt),dpi = 400, bbox_inches="tight")

#Incidence
df_incdx = df_pop3x.transpose()
#Sort header out
new_header2 = df_incdx.iloc[0] 
df_incdx = df_incdx[1:] 
df_incdx.columns = new_header2
df_incdx = df_incdx.tail(1)
txt_omni = "Hello,\n\nHere is the daily report for COVID-19 in Scotland for {}. \n\n".format(tDt_human) + txt_all +  txt_2 + "\n\nPlease find the raw data and graphs for cases, deaths and per capita metrics attached. To enhance graph readability and to account for cases being reallocated across health boards, the following health boards are grouped together: Grampian, Shetland and Orkney; Highland and Western Isles. \n \nPlease note that this is an automated service. For any queries, please contact g.calder@ed.ac.uk. \n\nThe data in this report are provided by Health Protection Scotland and published daily by the Scottish Government here https://www.gov.scot/coronavirus-covid-19/\n\nThank you."
print(txt_omni)

rcParams['figure.figsize'] = 12, 12


#Cases Per Test  and Deaths Per Cases (CPT & DPC)
df_CPT_Old = pd.read_excel(r"C:\Users\gcalder2\Daily_Reports\COVID-19_Scotland_CPT_DPC_{}.xlsx".format(yDt))
#df_CPT_Old['Date'] = df_CPT_Old['Date'].dt.date
data_CPT_new = {'Date': [tDt], 'Cases': [y], 'Deaths': [tot_deaths], 'Tests': [tot], 'CPT': [round(y/tot,5)], 'DPC': [round(tot_deaths/y,5)]}
df_CPT_New = pd.DataFrame(data=data_CPT_new)
df_CPT = df_CPT_Old.append(df_CPT_New)

#df_CPT.iloc[-1,4] = tDt.strftime('%Y-%m-%d')
df_CPT = df_CPT.reset_index()
df_CPT['Date']= pd.to_datetime(df_CPT['Date']) 
#Drop old index column
df_CPT2 = df_CPT.drop(df_CPT.columns[0,], axis=1) 
df_CPT2_Plot = df_CPT2[['Date','CPT','DPC']]
#df_CPT2_Plot['Date']= pd.to_datetime(df_CPT2_Plot['Date']) 
df_CPT2_Plot['Date'] = df_CPT2_Plot['Date'].dt.strftime('%Y-%m-%d')
df_CPT2_Plot.Date = df_CPT2_Plot.Date.str[5:]
df_CPT2_Plot = df_CPT2_Plot.set_index('Date')
df_CPT2_Plot2 = df_CPT2_Plot * 100 

#Plot
plot5 = df_CPT2_Plot2.plot.line(rot=0)
plot5.set_title('COVID-19 Cases Per Test & Deaths Per Case',size = 16)
plot5.set_ylabel("%", size = 14)
plot5.set_xlabel("Date", size = 14)
plot5.legend(loc = 'upper left', facecolor = '#F7F7F7', prop = {'size':14})
fig5 = plot5.get_figure()
fig5.savefig((r"C:\Users\gcalder2\Daily_Reports\COVID-19_Scotland_CPT_Plot_{}.png".format(tDt)),dpi = 400,bbox_inches="tight")

#Export sheets
df_CPT_x = df_CPT2[['Date','Tests','Cases','Deaths','CPT','DPC']]
#df_CPT_x['Date'] = df_CPT_x['Date'].dt.strftime('%Y-%m-%d')
df_CPT_x.to_excel((r"C:\Users\gcalder2\Daily_Reports\COVID-19_Scotland_CPT_DPC_{}.xlsx".format(tDt)), sheet_name='CPT & DPC')


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(r'filepath\Daily_Reports\COVID-19_Scotland_data_all_{}.xlsx'.format(tDt), engine='xlsxwriter')
# Write each dataframe to a different worksheet in same file
df_Deaths_XTran.to_excel(writer, sheet_name='Scotland Deaths')
df_xT.to_excel(writer, sheet_name = 'Cases By Health Board')
df_prevx3.to_excel(writer, sheet_name = 'Cumulative Incidence Grouped')
df_incdx.to_excel(writer,sheet_name= 'Incidence by Health Board', index=False)
df_CPT_x.to_excel(writer,sheet_name='CPT & DPC')
writer.save()


people = ['person1@email.com','person2@email.com']

print(people)

#Send report using pre-defined mailing function
send_daily_report(list3 = people, text = txt_omni)


#Send output to drop box (currently sending basic raw i.e. no per capita)

dbx = dropbox.Dropbox('yourDropboxKey')

with open(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_raw.xlsx'.format(tDt), "rb") as f:
    dbx.files_upload(f.read(), '/Daily_scraper_reports/SARS-Cov-2-Scotland-{}_raw.xlsx'.format(tDt), mute = True)
    
with open(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(tDt), "rb") as f:
    dbx.files_upload(f.read(), '/Daily_scraper_reports/SARS-Cov-2-Scotland-{}_deaths_raw.xlsx'.format(tDt), mute = True)
    
with open(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_deaths_trans.xlsx'.format(tDt), "rb") as f:
    dbx.files_upload(f.read(), '/Daily_scraper_reports/SARS-Cov-2-Scotland-{}_deaths_trans.xlsx'.format(tDt), mute = True)  

with open(r'filepath\Daily_Reports\SARS-Cov-2-Scotland-{}_cases_trans.xlsx'.format(tDt), "rb") as f:
    dbx.files_upload(f.read(), '/Daily_scraper_reports/SARS-Cov-2-Scotland-{}_cases_trans.xlsx'.format(tDt), mute = True)  

#Return meta data
#print(dbx.files_get_metadata('/SARS-Cov-2-Scotland-{}.xlsx'.format(yDt)).server_modified)




