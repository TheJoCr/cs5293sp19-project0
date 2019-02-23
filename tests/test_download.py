import pytest
from project0 import main
import contextlib
import datetime

TEST_RECORD_URL = 'file:///projects/cs5293p19-project0/tests/resources/test_arrest_record.pdf'
TEST_RECORD_PATH = './tests/resources/test_arrest_record.pdf'

def test_fetch():
    with main.fetch_incidents(TEST_RECORD_URL) as temp:
        assert len( temp.read() ) == 38778

def test_extract_sanity():
    incidents = main.extract_incidents( TEST_RECORD_PATH )
    assert len(incidents) > 0

def test_extract_count():
    incidents = main.extract_incidents( TEST_RECORD_PATH )
    assert len(incidents) == 15

def test_extract_dates():
    """
    Verifies that we matched fields by checking that the first field of
    every thing looks like a date in the correct range
    """
    f = './tests/resources/test_arrest_record.pdf'
    incidents = main.extract_incidents( f )
    for incident in incidents:
        # Make sure we can parse it
        time = datetime.datetime.strptime( incident.datetime, '%m/%d/%Y %H:%M' )
        # And that it is in about the right time frame
        assert datetime.datetime(2019, 2, 15) < time
        assert datetime.datetime(2019, 2, 25) > time

def test_create():
    """
    Creates the database, and verifies that the table exists.
    """
    conn = main.createdb();
    c = conn.cursor()
    table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    # Have to do the silly tuple syntax here
    assert ('arrests',) in table_names

def test_create_clean_up():
    """
    Make sure that we clean up an existing file when creating a new database
    """
    with open(main.DB_NAME, 'w') as f:
        f.write('DELETE ME!')
    test_create()

def test_populate_db():
    """
    Create a test object, insert it, and validate that we can get it out again
    """
    conn = main.createdb();
    in_ar = main.ArrestRecord(
        'test_datetime', 
        'test_case_number',
        'test_arrests_location',
        'test_offense',
        'test_arrestee',
        'test_arrestee_birthday',
        'test_arrestee_address',
        'test_city',
        'test_state',
        'test_zip_code',
        'test_status',
        'test_officers',
    )
    main.populatedb( conn, [in_ar ])
    # Test the total size
    assert conn.cursor().execute(
        'SELECT COUNT(*) FROM arrests'
    ).fetchone()[0] == 1
    # And that they match
    out = conn.cursor().execute(
        'SELECT * FROM arrests LIMIT 1'
    ).fetchone()
    out_ar = main.ArrestRecord._make(out)
    assert out_ar == in_ar
    return conn

def test_status():
    #Set up by populating db with test values
    conn = test_populate_db()
    assert 'þ' in main.status(conn) 

def test_main():
    status = main.main( TEST_RECORD_URL )
    # Basic check that it makes sense
    assert 'þ' in status
    # Now, double check the beginning is correct time stamp
    time = datetime.datetime.strptime( status.split('þ')[0], '%m/%d/%Y %H:%M' )
    # And that it is in about the right time frame
    assert datetime.datetime(2019, 2, 15) < time
    assert datetime.datetime(2019, 2, 25) > time
