#!/usr/local/bin/python

from __future__ import absolute_import, print_function
import itertools as it
from meza.io import read_csv, IterStringIO
from csv2ofx import utils
from csv2ofx.ofx import OFX
from csv2ofx.mappings.default import mapping
from tabula import read_pdf
from tabula import convert_into
import pandas as pd
from pandas.compat import StringIO
import csv
from datetime import datetime
import io

# Set the year, need a bit better way to handle this, somehow read/extract it from the PDF would be ideal
# Alternatively could
_year = " 2019"


# Read in the PDF
df = read_pdf("test.pdf")
# Convert it to CSV
df = df.to_csv(encoding='utf-8')

# Assign some headers
dataframe = pd.read_csv(StringIO(df), header=None, usecols=[1,2,3,4], names = ["Date","Description","Reference","Amount"])
# Add the year to the 'Month Day' formatted date
dataframe = dataframe.assign(Date = dataframe.Date + _year) 
# Convert that 'Month Day Year' formatted date to DD/MM/YYYY
dataframe["Date"] = pd.to_datetime(dataframe["Date"], format='%b %d %Y').dt.strftime('%m/%d/%Y')

dataframe["Account"] = "CHECKING"
# Lets write it to a file now
columns = ["Date", "Description", "Amount", "Account"]

print(dataframe)
export_csv = dataframe.to_csv(r'output.csv', index=None, header=True, columns=columns)







