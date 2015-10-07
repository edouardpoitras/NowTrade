"""
Various NowTrade configurtion options.

This will eventually be moved to a external configuration file that will be
read from any directory in your path.
"""
### NowTrade Global Settings ###


# Logging settings
import logging
LOG_FILE = 'nowtrade.log'
LOGGING_DEFAULT_CONSOLE = logging.WARNING
LOGGING_DEFAULT_FILE = logging.WARNING

# Action module
#LOGGING_Action_CONSOLE = logging.DEBUG
#LOGGING_Action_FILE = logging.DEBUG

# Criteria module
#LOGGING_Above_CONSOLE = logging.DEBUG
#LOGGING_Above_FILE = logging.DEBUG
#LOGGING_BarsSinceLong_CONSOLE = logging.DEBUG
#LOGGING_BarsSinceLong_FILE = logging.DEBUG

# Criteria Group module
#LOGGING_CriteriaGroup_CONSOLE = logging.DEBUG
#LOGGING_CriteriaGroup_FILE = logging.DEBUG

# Data Connection module
#LOGGING_YahooConnection_CONSOLE = logging.DEBUG
#LOGGING_YahooConnection_FILE = logging.DEBUG
#LOGGING_MongoDatabaseConnection_CONSOLE = logging.DEBUG
#LOGGING_MongoDatabaseConnection_FILE = logging.DEBUG

# Dataset module
#LOGGING_Dataset_CONSOLE = logging.DEBUG
#LOGGING_Dataset_FILE = logging.DEBUG

# Ensemble module
#LOGGING_Ensemble_CONSOLE = logging.DEBUG
#LOGGING_Ensemble_FILE = logging.DEBUG

# Figures module
#LOGGING_Figures_CONSOLE = logging.DEBUG
#LOGGING_Figures_FILE = logging.DEBUG

# Neural Network module
#LOGGING_NeuralNetwork_FILE = logging.DEBUG
#LOGGING_NeuralNetwork_CONSOLE = logging.DEBUG

# Notification module
#LOGGING_SMTPNotification_CONSOLE = logging.DEBUG
#LOGGING_SMTPNotification_FILE = logging.DEBUG

# Report module
#LOGGING_Report_CONSOLE = logging.DEBUG
#LOGGING_Report_FILE = logging.DEBUG

# Strategy module
#LOGGING_Strategy_CONSOLE = logging.DEBUG
#LOGGING_Strategy_FILE = logging.DEBUG

# Symbol List module
#LOGGING_SymbolList_CONSOLE = logging.DEBUG
#LOGGING_SymbolList_FILE = logging.DEBUG
#LOGGING_StockList_CONSOLE = logging.DEBUG
#LOGGING_StockList_FILE = logging.DEBUG

# Technical Indicator module
#LOGGING_SMA_CONSOLE = logging.DEBUG
#LOGGING_SMA_FILE = logging.DEBUG
#LOGGING_Shift_CONSOLE = logging.DEBUG
#LOGGING_Shift_FILE = logging.DEBUG

# Trade module
#LOGGING_Trade_CONSOLE = logging.DEBUG
#LOGGING_Trade_FILE = logging.DEBUG

# Trading Amount module
#LOGGING_StaticAmount_CONSOLE = logging.DEBUG
#LOGGING_StaticAmount_FILE = logging.DEBUG

# Trading Fee module
#LOGGING_StaticFee_CONSOLE = logging.DEBUG
#LOGGING_StaticFee_FILE = logging.DEBUG

# Trading Profile module
#LOGGING_TradingProfile_CONSOLE = logging.DEBUG
#LOGGING_TradingProfile_FILE = logging.DEBUG


## Notification Settings ##
GMAIL_USERNAME = 'sender@gmail.com'
GMAIL_PASSWORD = 'password'
RECIPIENT = 'recipient@email.com'
