# CS 5293 Project 0 Jordan Crawford

## Overview

This is a python program for parsing the City of Norman arrest record files
(stored as publicly accessible pdfs) into a basic sqlite database.
Essentially, each invocation of the program is passed the URL for one pdf page
of the Norman arrest records. The program fetches that pdf, creates a database
file called `arrests.db`, inserts one record into that file for each row in the
pdf, and prints an example row. Note that, at this time, the program only
actually parses the first page of the pdf, and that the parsing of the
police-published pdf may be fragile. 


## Sample Usage

To run the program, execute:
```bash
pipenv run python project0/main.py --arrests $URL
```
This prints to standard out an example row:
```
2/18/2019 11:39þ2019-00013652þ12TH AVE NE / E ROBINSON STþASSAULT/BATTERY WITH DEADLY WEAPONþDARION KEIS WILLHOITEþ11/26/1996þ1300 CREEKSIDE DRþNormanþOKþ73071þFDBDC (Jail)þ0813 - Judy; 
```
It also produces a file 'arrests.db' in the current working directory. Note
that if that file exists previously, it will be deleted. This is a sqlite
database that contains a single table `arrests`, whose structure mirrors the
table produced by the police exactly. Where information isn't available in the
police pdf, it is replaced by `UNKNOWN` or `''` (the empty string) in the
database. 

## Tests

Tests here reference an example file that is bundled with the tests, both via
a url that can be passed to `urllib.request` and via a standard file path. This
means that the test can be run without depending on any remote resources. 

To run tests execute:
```
pipenv run python setup.py test
```
This prints the test result (generated via pytest) to standard out. 
