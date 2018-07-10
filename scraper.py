"""
Filename: scraper.py
Author: Dave Springer
Date: July 9, 2018
Current Version: 1.0.0
Description: This file contains functions to identify available sessions and to
scrape course data for a specified session.  Creates a JSON file holding the
course information in a format that can be understood by the database importer.

Revision History:
#       Date        By          Description
1.0.0   07/09/2018  Springer    Commented out calls to testing functions
0.3.5   07/09/2018  Springer    Added function call for the database importer to
                                add courses once they have been scraped
0.3.4   07/09/2018  Springer    Fixed an error where only even-number course
                                rows were being scraped
0.3.3   07/09/2018  Springer    Added a getSubjects function that returns all
                                subjects available on schedule
0.3.2   07/09/2018  Springer    Added exception handling for bad web connection
0.3.1   07/09/2018  Springer    Added subject parameter to scrape function to
                                filter results
0.3.0   07/09/2018  Springer    Replaced output of empty strings with 'None'
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
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import re
import json
import courses

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

    try:
        # Open URL and create a BeautifulSoup object
        html = urlopen(__baseURL)
        bs = BeautifulSoup(html.read(), 'html.parser')
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')
    else:
        # Find each term and add it to the dictionary
        semmesterID = ''
        semmesterName = ''
        for session in bs.find('select', {'id': 'soc-session'}).find_all(
                'option'):

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

    return list(__sessions.keys())

def getSubjects():
    """
    Can be called to scrape all available subjects from the schedule page
    :return:
    """
    try:
        # Open URL and create a BeautifulSoup object
        html = urlopen(__baseURL)
        bs = BeautifulSoup(html.read(), 'html.parser')
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')
    else:
        subjects = bs.find('select', {'id':'soc-subject2'}).find_all('option')
        return [s.get('value') for s in subjects if s.get('value') != '']


def scrape(sessionName, subject = '', callDatabase=True):

    # Get session ID from the name and open URL of schedule for this session
    sessionID = __sessions[sessionName]

    url = '{}?fAcad=UGRD&fSess={}&fLoc=ALL&fSubj={}&fFetchRows=99999'.format(
        __baseURL, sessionID, subject)

    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')
    else:
        bs = BeautifulSoup(html.read(), 'html.parser')

        courseList = []

        # Even rows are id'ed differently than odd, so must scrape both
        rows = ('soc-course soc-highlight-border soc-highlight-border-even',
                'soc-course soc-highlight-border ')
        for row in rows:
            # Get each attribute for each course
            for course in bs.tbody.find_all('tr', {
                'class': row}):
                idCell = course.find('td', {'headers': 'soc-hd-course'})

                # Get course ID, consisting of the subject code and the 3-digit ID
                cID = idCell.find('span',
                                  {'class': 'soc-course-id'}).get_text().split()
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
                    prereq = 'None'
                    description = desc

                # Row 3: Class No., Section, Start/End, Day/Time, Status, Location
                row3 = row2.next_sibling.next_sibling
                classNum = row3.find('td', {'headers': 'soc-hd-class'}).get_text()
                section = row3.find('td', {'headers': 'soc-hd-goarmyed'}).get_text()
                dates = row3.find('td', {'headers': 'soc-hd-date'})
                day = row3.find('td', {'headers': 'soc-hd-day'}).get_text()
                time = row3.find('td', {'headers': 'soc-hd-time'}).get_text()
                status = row3.find('td', {'headers': 'soc-hd-status'}).get_text()
                loc = row3.find('td', {'headers': 'soc-hd-location'}).get_text()

                # Handle empty string values for day and time
                if day == '':
                    day = 'None'
                if time == '':
                    time = 'None'

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
                name = row4.find('td', {'colspan': '3'}).get_text()
                name = name[9:]  # Strip "Faculty" header
                names = name.split(', ')
                if len(names) > 1:  # Only if there is a faculty member listed
                    last = names[0]
                    first = names[1].split(' ')[0]
                else:  # Otherwise, use default values
                    last = 'None'
                    first = 'None'

                # Make dictionary for course information
                info = {
                    'subj': subj,
                    'num': id,
                    'title': title,
                    'credits': int(numCredits),
                    'classNum': int(classNum),
                    'section': int(section),
                    'startDate': start,
                    'endDate': end,
                    'day': day,
                    'time': time,
                    'status': status,
                    'location': location,
                    'facultyFirst': first,
                    'facultyLast': last,
                    'description': description,
                    'prereq': prereq
                }

                courseList.append(info)


        # Build a dictionary with key, 'courses', whose value is the courses list
        data = {'courses': courseList}

        # Write data as json file
        json.dump(data, fp=open('courses.json', 'w'), indent=4)

        print(len(data['courses']))

    if callDatabase:
        courses.update()


def __testOutput(sessionName, subject = ''):
    """
    This function is used to test that information has been scraped as expected
    """
    getSessions()

    # List all available subjects
    subjects = getSubjects()
    print('==== Subjects ====')
    for subj in subjects:
        print(subj)

    # List available sessions and their IDs
    print('\n==== Sessions ====')
    for k, v in __sessions.items():
        print('%s (%s)' % (k, v))

    print('\nScraping course data...\n')

    scrape(sessionName, subject, False)

    print('Done!')

    # Test importing JSON file
    with open('courses.json', 'r') as file:
        data = json.load(file)

    # Print JSON data (Note: may not print all for larger JSONs. Verify file.)
    #print('\n==== JSON Output ====')
    #print(json.dumps(data, indent=4))

# Test that all functions are working as expected
#__testOutput('2018 Fall', 'CMSC')
