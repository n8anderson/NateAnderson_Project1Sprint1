# NateAnderson_Project1Sprint1
Project is written in python using the requests package
Make sure to have requests package installed in order to run the program

Project takes college data and saves it to a plain text file under the name School_Data.txt

*** UPDATE 2/17/2021 ***

Added automated testing to test for github workflows:

test_getschooldata(url) - Takes data from the api college scorecard website and checks to see
if it gets over 1000 results. Passes if it is true

test_db() - creates a test database, then adds one arbitrary entry to the database and checks to see
if it was actually added. If it was true, then it passes.


*** UPDATE 2/23/2021 ***

Added new feature that pulls information from an excel sheet and saves it in the database as a new
table.

Two new tests to test functionality of the feature

Updated requirements to include Pandas and Openpyxl

test_getexcel() - Tests to see if we actually get the data from the excel sheet

test_occudb() - Tests to see if data is pushed into a new table in the database, and can be 
retrieved

*** UPDATE 3/18/2021 ***

TO RUN THE GUI

You must enter the file that you want to use exactly as it is written. Path may be included if the file is not within
the same project directory. Press select file after entering in the file name. 

You must run Populate API Data prior to running any map data, this will take a couple of minutes as it is gathering from
the API website. 

After running both of these functions you may interact with the map buttons and generate the table. To generate the table
press the 'generate table' button. You can then sort each column in ascending or descending order.

The ratios that are given in the table and map are the same. One is Jobs per Graduate, which divides the number of jobs 
in a state, by the number of grads in the state. The other is average salary of a state divided by the percent of 
people with a declining balance on loans. 

Some issues that I have run into:
1) I could not get the color coding to work
2) I could not find a better way to have the program run other than requiring the buttons to be pressed prior to any data
being shown.
   
One new test was created:

test_getratios() - will test to see if a dictionary is created with values. I could not figure out a way to test the
values inside of the dictionary for accuracy, so i just made sure that they were actually there. It passes if the len
of the dictionary is greater than 0.