#!/usr/bin/python
# Updates a local mongo db with currency minute/hour data using the OandaConnection class.
from nowtrade import data_connection
ACCOUNT_ID = ''
ACCESS_TOKEN = ''
data_connection.populate_oanda_currency(ACCOUNT_ID, ACCESS_TOKEN, ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CAD', 'USD_CHF', 'AUD_USD'], granularity='M5', periods=5000, database='oanda-5min')
data_connection.populate_oanda_currency(ACCOUNT_ID, ACCESS_TOKEN, ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CAD', 'USD_CHF', 'AUD_USD'], granularity='M15', periods=5000, database='oanda-15min')
data_connection.populate_oanda_currency(ACCOUNT_ID, ACCESS_TOKEN, ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CAD', 'USD_CHF', 'AUD_USD'], granularity='H1', periods=5000, database='oanda-1hour')
data_connection.populate_oanda_currency(ACCOUNT_ID, ACCESS_TOKEN, ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CAD', 'USD_CHF', 'AUD_USD'], granularity='D', periods=5000, database='oanda-day')
