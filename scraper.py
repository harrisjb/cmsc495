"""
Filename: scraper.py
Author: Dave Springer
Date:
Description: This file contains functions to identify available sessions and to
scrape course data for a specified session.  Creates a JSON file holding the
course information in a format that can be understood by the database importer.

Revision History:

0.1.5   06/30/2018  Modified scrape so it takes a session name as an argument.
                    Scrape method now produces a JSON file for course data.
0.1.4   06/29/2018  Updated getSessions function so that a global dictionary
                    that maps the session name to the session ID is added
0.1.3   06/28/2018  Added function to determine which sessions are available
0.1.2   06/27/2018  Updated scrape function so that course attributes are scaped
                    and added to the course's dictionary
0.1.1   06/26/2018  Added scrape function which opens connection to UMUC's
                    schedule web page for a pre-specified URL for Fall 2018 and
                    creates a list of courses with empty dictionaries for each
                    course.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json

__sessions = dict()
__baseURL = 'http://webapps.umuc.edu/soc/us.cfm'

def getSessions():
    """
    This function scrapes the UMUC schedule website for a list of available
    terms and their associated session IDs, storing this information in a global
    dictionary of terms.  It returns a list of the dictionaries keys, a string
    list of term names
    """

    global __sessions

    # Open URL and create a BeautifulSoup object
    html = urlopen(__baseURL)
    bs = BeautifulSoup(html.read(), 'html.parser')

    # Find each term and add it to the dictionary
    for session in bs.find('select', {'id': 'soc-session'}).find_all('option'):

        sessionID = session.get('value')

        # Only add full terms (not sub terms)
        if len(sessionID) == 4:
            pattern = '([0-9]* [a-zA-Z]*)'
            sessionName = re.match(pattern, session.get_text()).groups()[0]
            __sessions[sessionName] = sessionID

    return list(__sessions.keys())

def scrape(sessionName):

    # Get session ID from the name and open URL of schedule for this session
    sessionID = __sessions[sessionName]

    url = '{}?fAcad=UGRD&fSess={}&fLoc=ALL&fSubj=&fFetchRows=99999'.format(
        __baseURL, sessionID)
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), 'html.parser')

    courses = []

    # Get each attribute for each course
    for course in bs.tbody.find_all('tr', {
        'class': 'soc-course soc-highlight-border soc-highlight-border-even'}):
        idCell = course.find('td', {'headers': 'soc-hd-course'})

        # Get course ID, consisting of the subject code and the 3-digit ID
        cID = idCell.find('span',{'class':'soc-course-id'}).get_text().split()
        subj = cID[0]
        id = cID[1]

        # Title and credits come from the same cell
        titleCell = idCell.next_sibling.next_sibling
        title = titleCell.get_text()[:-4]
        numCredits = titleCell.get_text()[-2]

        # Row 2: Description, with any prerequisites embedded
        row2 = course.next_sibling.next_sibling
        desc = row2.get_text()[1:]

        # Row 3: Class No., Section, Start/End, Day/Time, Status, Location
        row3 = row2.next_sibling.next_sibling
        classNum = row3.find('td', {'headers':'soc-hd-class'}).get_text()
        section = row3.find('td', {'headers':'soc-hd-goarmyed'}).get_text()
        date = row3.find('td', {'headers': 'soc-hd-date'}).get_text()
        day = row3.find('td', {'headers': 'soc-hd-day'}).get_text()
        time = row3.find('td', {'headers': 'soc-hd-time'}).get_text()
        status = row3.find('td', {'headers': 'soc-hd-status'}).get_text()
        location = row3.find('td', {'headers': 'soc-hd-location'}).get_text()

        # Row 4: Faculty information
        row4 = row3.next_sibling.next_sibling
        name = row4.find('td', {'colspan':'3'}).get_text()

        # Make dictionary for course information
        info = {
            'subj' : subj,
            'num' : id,
            'title' : title,
            'credits' : int(numCredits),
            'classNum' : int(classNum),
            'section' : int(section),
            'startDate' : date,
            'endDate' : date,
            'day' : day,
            'time' : time,
            'status' : status,
            'location' : location,
            'facultyFirst' : name,
            'facultyLast' : name,
            'facultyMI' : name,
            'description' : desc,
            'prereq' : ''
        }

        courses.append(info)

    # Build a dictionary with key, 'courses', whose value is the courses list
    data = {'courses': courses}

    # Write data as json file
    json.dump(data, fp=open('courses.json', 'w'), indent=4)


def testOutput(sessionName):
    """
    This function is used to test that information has been scraped as expected
    """
    getSessions()

    # List available sessions and their IDs
    print('==== Sessions ====')
    for k, v in __sessions.items():
        print('%s (%s)' % (k, v))

    print('\nScraping course data...\n')

    scrape(sessionName)

    # Test importing JSON file
    with open('courses.json', 'r') as file:
        data = json.load(file)

    # Print JSON data (Note: may not print all due to size. Verify in file.)
    print(json.dumps(data, indent=4))


# Test that all functions are working as expected
testOutput('2018 Fall')
