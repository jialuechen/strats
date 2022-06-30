# <center>Strats : Built for Professional Quants</center>

### Strats is an asynchronous and event-driven Python library for algorithmic trading, supporting both backtesting, paper or live trading via Interactive Brokers.

## Features
+ Built on reliable Interactive Brokers official Python APIs.
+ Multiple choices for data sources for backtesting.
+ Full Integration with TA-Lib.
+ Asynchronous architecture for running market events.
+ Compatible with PostgreSQL for storing data.
+ Easy to work with other scientific or machine learning libraries to build your own strategy. 

## Required Software
+ Latest Interactive Brokers Trader Workstation or IB Gateway(If you want to try paper/live trading). Make sure the API port is enabled.
+ PostgreSQL Server

## Required Third-Party Python Library
+ ibapi (please follow the official installation guide on Interactive Brokers website. Personal recommended choice is to run its setup.py to install it as a regular library)
+ pandas
+ numpy
+ psycopg2
+ TA-Lib

## License
This software is distributed under the Apache 2.0 license.