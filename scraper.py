"""
Filename: scraper.py
Author: Dave Springer
Date: July 8, 2018
Current Version: 0.2.3
Description: This file contains functions to identify available sessions and to
scrape course data for a specified session.  Creates a JSON file holding the
course information in a format that can be understood by the database importer.

Revision History:
#       Date        By          Description
0.2.3   07/08/2018  Springer    Modified getSessions() function to look for
                                sub-semesters rather than just entire semesters
0.2.2   07/06/2018  Springer    Extracted prerequisites from description and
                                updated description so that it does not include
                                this information
0.2.1   07/05/2018  Springer    Extracted faculty first and last name from full
                                faculty field
0.2.0   07/03/2018  Springer    Extracted start and end date from string of
                                dates
0.1.4	07/01/2018	Springer	Minor modifications to formatting/comments
0.1.3   06/30/2018  Springer    Modified scrape so it takes a session name as an
                                argument. Scrape method now produces a JSON file
                                for course data.
0.1.2   06/29/2018  Springer    Updated getSessions function so that a global
                                dictionary that maps the session name to the
                                session ID is added
0.1.1   06/28/2018  Springer    Added function to determine which sessions are
                                available Updated scrape function so that course
                                attributes are scraped and added to the course's
                                dictionary
0.1.0   06/26/2018  Springer    Added scrape function which opens connection to
                                UMUC's schedule web page for a pre-specified URL
                                for Fall 2018 and creates a list of courses with
                                empty dictionaries for each course.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json

__sessions = {}
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
    semmesterID = ''
    semmesterName = ''
    for session in bs.find('select', {'id': 'soc-session'}).find_all('option'):

        # Splitting by '|' gives us two values-- semesterID and subSessionID
        sessionInfo = session.get('value').split('|')
        # If no subSession ID, then this is for the entire semester
        if len(sessionInfo) == 1:
            semmesterID = sessionInfo[0]
            sessionID = semmesterID

            # Get session name
            pattern = '[0-9]* [A-Za-z]*'
            semmesterName = re.search(pattern, session.get_text()).group()
            sessionName = semmesterName
        else:
            sessionID = semmesterID + '%7C' + sessionInfo[1]

            # Get session name
            pattern = '[A-Za-z]+( [A-Za-z0-9]+)*'
            sessionName = semmesterName + ' ' + \
                          re.search(pattern, session.get_text()).group()

        # Add course to dictionary
        __sessions[sessionName] = sessionID


    #return list(__sessions.keys())

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

        # Extract prerequisites from description
        match = re.match('(.*?)Prereq.*?: (.*?)\. (.*)', desc)
        if match:
            prereq = match.group(2)
            description = match.group(1) + match.group(3)
        else:
            prereq = ''
            description = desc

        # Row 3: Class No., Section, Start/End, Day/Time, Status, Location
        row3 = row2.next_sibling.next_sibling
        classNum = row3.find('td', {'headers':'soc-hd-class'}).get_text()
        section = row3.find('td', {'headers':'soc-hd-goarmyed'}).get_text()
        dates = row3.find('td', {'headers': 'soc-hd-date'})
        day = row3.find('td', {'headers': 'soc-hd-day'}).get_text()
        time = row3.find('td', {'headers': 'soc-hd-time'}).get_text()
        status = row3.find('td', {'headers': 'soc-hd-status'}).get_text()
        loc = row3.find('td', {'headers': 'soc-hd-location'}).get_text()

        # Format location for in-person classes (keep online as is)
        if loc == 'Online':
            location = loc
        else:
            location = loc.split('-')[0]

        # Get start/end dates from dates string
        dates = dates.get_text().split('-')
        start = dates[0]
        end = dates[1]

        # Row 4: Faculty information
        row4 = row3.next_sibling.next_sibling
        name = row4.find('td', {'colspan':'3'}).get_text()
        name = name[9:] # Strip "Faculty" header
        names = name.split(', ')
        if len(names) > 1: # Only if there is a faculty member listed
            last = names[0]
            first = names[1].split(' ')[0]
        else: # Otherwise, use default values
            last = ''
            first = ''

        # Make dictionary for course information
        info = {
            'subj' : subj,
            'num' : id,
            'title' : title,
            'credits' : int(numCredits),
            'classNum' : int(classNum),
            'section' : int(section),
            'startDate' : start,
            'endDate' : end,
            'day' : day,
            'time' : time,
            'status' : status,
            'location' : location,
            'facultyFirst' : first,
            'facultyLast' : last,
            'description' : description,
            'prereq' : prereq
        }

        courses.append(info)

    # Build a dictionary with key, 'courses', whose value is the courses list
    data = {'courses': courses}

    # Write data as json file
    json.dump(data, fp=open('courses.json', 'w'), indent=4)


def __testOutput(sessionName):
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
    #print(json.dumps(data, indent=4))


# Test that all functions are working as expected
__testOutput('2018 Fall US Session 2')
