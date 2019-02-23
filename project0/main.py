# -*- coding: utf-8 -*-
import argparse
import urllib.request
import tempfile
import contextlib
import sqlite3
import collections
import re
import os

from PyPDF2 import PdfFileReader

DB_NAME='arrests.db'

ArrestRecord = collections.namedtuple( 'ArrestRecord', [
    'datetime',
    'case_number',
    'arrests_location',
    'offense',
    'arrestee',
    'arrestee_birthday',
    'arrestee_address',
    'city',
    'state',
    'zip_code',
    'status',
    'officers',
])

@contextlib.contextmanager
def fetch_incidents(url):
    arrest_summary = urllib.request.urlopen( url )
    data = arrest_summary.read()
    with tempfile.TemporaryFile() as temp:
        temp.write( data )
        # Need to reset to the beginning of the file
        # before it can be read
        temp.seek(0)
        yield temp

def extract_incidents( local_file_handle ):
    """
    Extract incidents from a file handle that has already been
    opened. The data is returned as a list of ArrestRecord 
    objecs
    """
    # Boo cammel case functions!
    pdf_file = PdfFileReader( local_file_handle )
    page1 = pdf_file.getPage(0).extractText()
    # The data is just a bunch of line. 
    # So we can do, simply:
    step = len( ArrestRecord._fields )
    rv = []
    # Some fields end up getting split across multiple lines - 
    # these can be identified by the presence of a trailing space
    # regex them out of existence!
    page1 = re.sub('[- ]\n', ' ', page1)
    # We Also need to replace 'UNKNOWN' addresses with empty
    # strings for the city/state/zip
    page1 = re.sub('UNKNOWN\n', 'UNKNOWN\n\n\n\n', page1)
    lines = page1.split('\n')
    # Trim off the last couple of useless lines
    for i in range(0, len( lines ) - len(lines) % step, step ):
        rv.append( ArrestRecord._make( lines[i:i+step] ) )
    # Need to trim the first line (it's just the header)
    return rv[1:]

def createdb():
    # Make sure we clean up after ourselves
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    conn = sqlite3.connect(DB_NAME);
    c = conn.cursor()
    c.execute( '''
    CREATE TABLE arrests (
        datetime TEXT,
        case_number TEXT,
        arrests_location TEXT,
        offense TEXT,
        arrestee TEXT,
        arrestee_birthday TEXT,
        arrestee_address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        status TEXT,
        officers TEXT
    )
    ''' )
    return conn

def populatedb( db, incidents ):
    c = db.cursor()
    # This inserts all of the tuples we parsed at the same time
    c.executemany('INSERT INTO arrests VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', incidents);

def status( db ):
    c = db.cursor()
    c.execute('SELECT * FROM arrests LIMIT 1')
    arrest = ArrestRecord._make( c.fetchone() )
    output = 'þ'.join(arrest)
    print(output)
    return output

def main( url ):
    # Download data
    # Use a context manager to ensure that the temp file is cleaned up if we
    # encounter an exception
    with fetch_incidents(url) as incidents_file:
        # Extract Data
        incidents = extract_incidents( incidents_file )
        
        # Create Dataase
        db = createdb()
        
        # Insert Data
        populatedb(db, incidents)
        
        # Print Status
        return status(db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--arrests", type=str, required=True, 
                         help="The arrest summary url.")
     
    args = parser.parse_args()
    if args.arrests:
        main(args.arrests)

