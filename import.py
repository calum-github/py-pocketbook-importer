#!/usr/local/bin/python

import tabula
import pandas as pd
from pandas.compat import StringIO
import csv
from datetime import datetime
import io
import os
import sys
import camelot
import numpy as np

# Set the year, need a bit better way to handle this, somehow read/extract it from the PDF would be ideal
# Alternatively could
_year = " 2018"

# Get the name of the pdf passed in
pdf_name = sys.argv[1]
csv_name = sys.argv[2]
csv_name = "2018_Visa_All.csv"
output_mode = sys.argv[3]

top = 215
left = 51
height = 294
width = 524

x1 = left
y1 = top
y2 = top + height
x2 = left + width


table_area = [x1,y1,x2,y2]
#print(table_area)

def process_using_camelot(pdf_name,csv_name,output_mode,table_area):
	# Use camelot to read the DPF
	tables = camelot.read_pdf(pdf_name, flavor='stream')
	# tables = camelot.read_pdf(pdf_name, flavor='stream', table_areas=['51','215','575','509'])

	# set df to the dataframe from camelot
	df = tables[0].df
	# print(df)
	# Assign our Columns same names
	df.columns = ["Date", "Description", "Reference", "Amount"]
	# # Perform some clean up on the rows
	# # Remove row if it contains data we are not looking for
	# # Here we will remove lines that are NOT dates and thus transactions
	df = df[~df.Date.str.contains("Account Name")]
	df = df[~df.Date.str.contains("Account Number")]
	df = df[~df.Date.str.contains("Transactions")]
	df = df[~df.Date.str.contains("Date")]
	df = df[~df.Date.str.contains("Card Number")]
	# # Remove row that contains customer care crap n the amount column
	df = df[~df.Amount.str.contains("Customer Care")]
	# Remove continued on next page
	df = df[~df.Amount.str.contains("Continued next page")]
	# Remove row if it contains Closing Balance
	df = df[~df.Date.str.contains("Closing Balance")]
	# Replace empty strings in the Date column 
	df = df[df.Date != '']
	# Add the year to the date column
	df = df.assign(Date = df.Date + _year) 
	# # Convert that 'Month Day Year' formatted date to DD/MM/YYYY
	df["Date"] = pd.to_datetime(df["Date"], format='%b %d %Y').dt.strftime('%d/%m/%Y')
	# Convert amounts from positive to negative and negative to postive. This is because pocketbook doesn't treat
	# the imported files correctly, it mistakes credits for debits and debits for credits.
	# Convert the values in Amount which are strings to a float
	df["Amount"] = df["Amount"].astype(float)
	# Now multiply those values by -1 to invert the values
	df["Amount"] *= -1
	# Add a new column called Account and fill it with CHECKING
	df["Account"] = "CHECKING"
	# List of columns we care about
	columns = ["Date", "Description", "Amount", "Account"]
	# Print out the df
	print(df)
	# Export the CSV to a new file
	if output_mode == "create":
		#print("using create mode")
		export_csv = df.to_csv(csv_name, index=None, header=False, columns=columns)
	# Export the csv to the same file, append to it
	elif output_mode == "append":
		#print("using append mode")
		export_csv = df.to_csv(csv_name, mode="a", index=None, header=False, columns=columns)


def create_qif(csv_name):
	# This function will create a QIF file from a csv file
	# Create a QIF file, use the name of the csv, but change the extension to .qif
	qif_file_name = csv_name.rsplit('.',1)[0] + ".qif"
	qif = open(qif_file_name, "w+")
	# Write out a header
	qif.write("!Type:CCard \n")
	# Read in the CSV first
	with open(csv_name) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			qif.write('D' + row[0] + '\n')
			qif.write('T' + row[2] + '\n')		
			qif.write('P' + row[1] + '\n')
			qif.write("^" + '\n')
	# Close off the file
	qif.close()

def process_using_tabular(pdf_name,csv_name,output_mode):
	# Use Tabular to read the PDF
	df = tabula.read_pdf(pdf_name, pages="all") # area=(y1, x1, y2, x2))
	# Convert it to CSV
	df = df.to_csv(encoding='utf-8')
	# # Assign some headers
	dataframe = pd.read_csv(StringIO(df), header=None, usecols=[1,2,3,4], names = ["Date","Description","Reference","Amount"])
	# Remove row if it contains Closing Balance
	dataframe = dataframe[~(dataframe == 'Closing Balance')]
	# Remove row if it contains NaN
	dataframe = dataframe[pd.notnull(dataframe['Date'])]
	# # Add the year to the 'Month Day' formatted date
	dataframe = dataframe.assign(Date = dataframe.Date + _year) 
	# # Convert that 'Month Day Year' formatted date to DD/MM/YYYY
	dataframe["Date"] = pd.to_datetime(dataframe["Date"], format='%b %d %Y').dt.strftime('%m/%d/%Y')
	dataframe["Account"] = "CHECKING"
	# # Lets write it to a file now
	columns = ["Date", "Description", "Amount", "Account"]
	print(dataframe)
	# Export the CSV to a new file
	if output_mode == "create":
		#print("using create mode")
		export_csv = dataframe.to_csv(csv_name, index=None, header=True, columns=columns)
	# Export the csv to the same file, append to it
	elif output_mode == "append":
		#print("using append mode")
		export_csv = dataframe.to_csv(csv_name, mode="a", index=None, header=False, columns=columns)

# Process it and output a CSV

#process_using_tabular(pdf_name,csv_name,output_mode)

process_using_camelot(pdf_name,csv_name,output_mode,table_area)

create_qif(csv_name)






