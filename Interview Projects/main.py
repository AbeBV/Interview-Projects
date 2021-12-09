import streamlit as st 
import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pylab as plt
from datetime import date
from numpy import nanmean
from numpy import nanstd
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates


def q1(x):
    return x.quantile(0)

def q2(x):
    return x.quantile(.05)
def q3(x):
    return x.quantile(.25)    
def q4(x):
    return x.quantile(.5)        
def q5(x):
    return x.quantile(0.75)
def q6(x):
    return x.quantile(0.95)    
def q7(x):
    return x.quantile(1)        



header = st.container()
dataset = st.container()
features = st.container()
modelTraining = st.container()

#@st.cache
def get_data(filename):
	df = pd.read_excel (filename)
	return df

@st.cache
def get_dataCSV(filename, indexCol = True):
	if indexCol == True:
		df = pd.read_csv(filename, index_col = [0])
		return df
	else:
		df = pd.read_csv(filename)
		return df
dfSharpe = get_dataCSV('C:/Users/18479/Documents/Interview Projects/SharpeRatios_1.csv')
dfAlpha = get_dataCSV('C:/Users/18479/Documents/Interview Projects/AlphaOfFunds.csv')
dfCumulRet_Sharpe = get_dataCSV('C:/Users/18479/Documents/Interview Projects/Cumulative Returns Sharpe.csv')
dfCumulRet_Alpha = get_dataCSV('C:/Users/18479/Documents/Interview Projects/Cumulative Returns Alpha.csv')
dfSharpeYearsandWeights =  get_dataCSV('C:/Users/18479/Documents/Interview Projects/Sharpe Weights and Accounts.csv')
dfAlphaYearsandWeights = get_dataCSV('C:/Users/18479/Documents/Interview Projects/Alpha Weights and Accounts.csv')
dfFuturePortfolio = get_dataCSV('C:/Users/18479/Documents/Interview Projects/Combined Future Alpha Sharpe Portfolio.csv', False)

#df = pd.read_excel (r'C:\Users\18479\Downloads\Hedge Fund Data  - Trailing 5-Year Monthly Returns.xlsx')
df = get_data(r'C:\Users\18479\Downloads\Hedge Fund Data  - Trailing 5-Year Monthly Returns.xlsx')
for i in range(4, len(df.columns)):
    df.iloc[4,i] = df.iloc[4,i].date()
df.columns = df.iloc[4]
df = df.iloc[: , 1:]
df = df.iloc[5: , :]
df.reset_index(drop = True, inplace = True)
for i in range(4,len(df.columns)):
    df.iloc[:,i] = np.array(df.iloc[:,i],dtype = 'float32')

st.set_option('deprecation.showPyplotGlobalUse', False)

with header:
	st.title("Welcome to GCM Streamlit Project")

#with dataset:
	#st.write(df.style.set_precision(4))
	#st.write(df.head())

with features:
	dateForDist = st.sidebar.text_input("Enter Date Format YYYY-MM-DD where DD is first date of month ie 01", value = str(date.today().replace(day=1).replace(year = 2019)))
	format = '%Y-%m-%d'
	colSelect = dt.datetime.strptime(dateForDist, format).date()


	options = st.sidebar.multiselect(
     'Select columns to group by',
     ['Hedge Fund Strategy', 'Hedge Fund Sub-Strategy', 'Fund ID',],
     ['Fund ID'])
	#removeNaNBool = st.text_input("Remove NaN's type: Yes or No", value = "No")
	#removeNaNBool = removeNaNBool.lower()		
	vals = {colSelect: [q1, q2, q3,q4,q5,q6, q7]}
	df1 = df.groupby(options).agg(vals)
	#st.header(str(colSelect) + " " + ", ".join(options))
	df1.columns = ['Min', '5%','25%', 'Median','75%', '95%', 'Max']
	df2 = df.groupby(options).agg({colSelect:[nanstd,nanmean]})
	df2.columns = ['Std Dev', 'Mean']
	#if removeNaNBool == 'yes':
	#	pass
	df1 = pd.concat([df1,df2], axis = 1)
	#df1.dropna(inplace = True)
	st.header("Distributional Statistics For Period Of " + dateForDist + " By Selected Columns")
	st.write(df1.style.format("{:.4f}"))

	meanMonthlyReturn = np.nanmean(df[colSelect])
	sdMonthlyReturn = np.nanstd(df[colSelect])
	stdDevSz = st.sidebar.number_input("Enter Standard Deviation", value = 2, step = 1)
	
	dfOutlierPerMonth = df[["Hedge Fund Strategy", "Hedge Fund Sub-Strategy", "Fund ID",colSelect]].dropna(axis = 0)

	st.header("Return Outliers For Period Of " + dateForDist + " By Selected Standard Deviations")
	st.write(dfOutlierPerMonth.style.set_precision(4))
	dfOutlierPerMonth_Filtered = dfOutlierPerMonth[(dfOutlierPerMonth[colSelect] >= meanMonthlyReturn + stdDevSz * sdMonthlyReturn) | (dfOutlierPerMonth[colSelect] <= meanMonthlyReturn - stdDevSz * sdMonthlyReturn)]
	
	dfOutlierPerMonth_Filtered.sort_values(by = colSelect, ascending = False, inplace = True)
	st.header("Top 3 Largest Monthly Returns For The Period Of " + dateForDist)
	st.write(dfOutlierPerMonth_Filtered.iloc[:3].style.set_precision(4))
	st.header("Bottom 3 Largest Monthly Returns For The Period Of " + dateForDist )
	st.write(dfOutlierPerMonth_Filtered.iloc[-3:].style.set_precision(4))
	
	### Plot of Return for given year
	st.header("Distribution of returns among all existing funds in the period of " + str(colSelect))
	sns.distplot(dfOutlierPerMonth[colSelect])
	st.pyplot()
	

	fundID = st.sidebar.number_input("Enter Fund", value = 24, step = 1)
	fundID_Row = np.where(df["Fund ID"] == fundID)[0]
	#st.write(fundID_Row)
	dfScatter = pd.DataFrame(columns = ["X_Val", "Y_Val"])
	dfScatter["X_Val"] = df.columns[3:]
	#st.write(df.iloc[fundID_Row,3:])
	dfScatter["Y_Val"] = df.iloc[fundID_Row,3:].values[0]

	x_var = df.columns[3:]
	#x_var = pd.DataFrame(x_var)
	#dfScatter = pd.concat([dfScatter,dfScatter.columns], axis = 0, ignore_index = True)
	#st.write(dfScatter)
	#st.write(x_var)
	#st.write(dfScatter)

	#sns.set(font_scale=1)
	ax = sns.scatterplot(data = dfScatter,x = "X_Val", y = "Y_Val")

	ax.set_xlim(dfScatter['X_Val'].min()-dt.timedelta(days = 60), dfScatter['X_Val'].max()+dt.timedelta(days = 60))
	ax.set_xlabel("Dates", fontsize = 10)
	ax.set_ylabel("Returns", fontsize = 10)
	ax.set_title("Monthly Returns Over Time For Fund " + str(int(fundID)), fontsize = 20)
	#ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
	ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
	st.pyplot()
	#dataScatter = pd.DataFrame
	st.header("Sharpe Ratios For All Funds")
	st.write(dfSharpe)

	### Top and Bottom Sharpe Data Selected By Mean, SD, Sharpe Ratio

	SharpeFundsPickedAmt = st.sidebar.number_input("Enter Top/Bottom Amount Of Funds By Sharpe Data", value = 5, step = 1, min_value  = 1, max_value = 10 )
	SharpeFundsPickedAmt = int(SharpeFundsPickedAmt)
	selectedSharpeDataCol = st.sidebar.selectbox(
     'Select Top/Bottom From Mean Excess Returns, SD, Sharpe Ratio',
     ('Mean_Excess_Returns', 'SD_Excess_Return', 'Sharpe_Ratio'))


	dfSharpeCopy = dfSharpe.copy()
	dfSharpeCopy.sort_values(by = selectedSharpeDataCol, ascending = False, inplace = True)

	st.header("Top " + str(SharpeFundsPickedAmt) + " Funds By " + selectedSharpeDataCol)
	st.write(dfSharpeCopy.head(SharpeFundsPickedAmt))
	st.header("Bottom " + str(SharpeFundsPickedAmt) + " Funds By " + selectedSharpeDataCol)	
	st.write(dfSharpeCopy.tail(SharpeFundsPickedAmt))

	### Alpha Tables and Sorting Starts here

	st.header("Alpha, Beta, Statistical Significance of Alpha For Funds")
	st.write(dfAlpha)


	### Top and Bottom Sharpe Data Selected By Mean, SD, Sharpe Ratio

	AlphaFundsPickedAmt = st.sidebar.number_input("Enter Top/Bottom Amount Of Funds By Alpha/Beta Data", value = 5, step = 1, min_value  = 1, max_value = 10 )
	AlphaFundsPickedAmt = int(AlphaFundsPickedAmt)
	selectedAlphaDataCol = st.sidebar.selectbox(
     'Select Top/Bottom From Alpha, Beta, Alpha P-Value',
     ('Alpha', 'Beta', 'Alpha P-Value'))


	dfAlphaCopy = dfAlpha.copy()
	dfAlphaCopy.sort_values(by = selectedAlphaDataCol, ascending = False, inplace = True)

	st.header("Top " + str(AlphaFundsPickedAmt) + " Funds By " + selectedAlphaDataCol)
	st.write(dfAlphaCopy.head(AlphaFundsPickedAmt))
	st.header("Bottom " + str(SharpeFundsPickedAmt) + " Funds By " + selectedAlphaDataCol)	
	st.write(dfAlphaCopy.tail(AlphaFundsPickedAmt))	
	
	st.header("Weights of Risk Parity Portfolio Funds For A Given Year Based On Sharpe Filtering")
	st.write(dfSharpeYearsandWeights)
	# Plotting Culumative Returns of Backtested Sharpe Portfolio
	dfCumulRet_Sharpe_copy = dfCumulRet_Sharpe.copy()
	dfCumulRet_Sharpe_copy["Date"] = pd.to_datetime(dfCumulRet_Sharpe_copy["Date"])
	#st.write(dfCumulRet_Sharpe_copy)
	fig = plt.figure()
	ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
	#ax1.plot(cumulative_ret)
	ax1.plot(dfCumulRet_Sharpe_copy["Date"],dfCumulRet_Sharpe_copy["Cumulative_Returns"], label='Risk Parity')
	ax1.plot(dfCumulRet_Sharpe_copy["Date"],dfCumulRet_Sharpe_copy["EQ_Cumulative_Returns"],  label='Equal Weight', color = 'r')
	#ax1.plot(dfCumulRet_Eq, label='Risk Parity')
	#ax1.plot(dfCumulRet,  label='Equal Weight', color = 'r')
	ax1.set_xlabel('Date')
	ax1.set_ylabel("Cumulative Returns")
	ax1.set_title("Portfolio Cumulative Returns Of Risk Parity Portfolio Filtered On Sharpe Ratio From Previous Year")
	ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
	ax1.legend()
	st.write(fig)

	st.header("Weights of Risk Parity Portfolio Funds For A Given Year Based On Alpha Filtering")
	#st.write(dfAlphaYearsandWeights)
	# Plotting Culumative Returns of Backtested Sharpe Portfolio
	dfCumulRet_Alpha_copy = dfCumulRet_Alpha.copy()
	dfCumulRet_Alpha_copy["Date"] = pd.to_datetime(dfCumulRet_Alpha_copy["Date"])
	fig = plt.figure()
	ax2 = fig.add_axes([0.1,0.1,0.8,0.8])
	#ax1.plot(cumulative_ret)
	ax2.plot(dfCumulRet_Alpha_copy["Date"],dfCumulRet_Alpha_copy["Cumulative_Returns"], label='Risk Parity')
	ax2.plot(dfCumulRet_Alpha_copy["Date"],dfCumulRet_Alpha_copy["EQ_Cumulative_Returns"],  label='Equal Weight', color = 'r')

	ax2.set_xlabel('Date')
	ax2.set_ylabel("Cumulative Returns")
	ax2.set_title("Portfolio Cumulative Returns Of Risk Parity Portfolio Filtered On Alpha Ratio From Previous Year")
	ax2.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
	ax2.legend()
	st.write(fig)

	st.header("Future Alpha and Sharpe Filtered Risk Parity Portfolio Weights")
	st.write(dfFuturePortfolio)




