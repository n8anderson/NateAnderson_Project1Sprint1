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