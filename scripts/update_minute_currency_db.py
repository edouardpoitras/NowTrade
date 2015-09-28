#!/usr/bin/python
# Populates a local mongo db with currency minute data using the ForexiteConnection class.
from nowtrade import data_connection
import datetime
start = datetime.datetime(2014, 05, 17)
end = datetime.datetime(2015, 02, 20)
data_connection.populate_currency_minute(start, end, sleep=60)
