import json

"""
This file is a placeholder for the scraper code.
Scraper will get information for each course and put all information in a list of courses.
While the final code will generate this list, a dummy data list has been created here.
"""

# The list would look something like this:
courses = [
    {
        'subj':'CMSC',
        'num':'150',
        'title':'Introduction to Discrete Structures',
        'credits':3,
        'classNum':51039,
        'section':6380,
        'startDate':'21-May-18',
        'endDate':'15-Jul-18',
        'day':'',
        'time':'',
        'status':'Open',
        'location':'Online',
        'facultyLast':'Shash',
        'facultyFirst':'Abdulnasir',
        'facultyMI':'M',
        'description':'Prerequisite or corequisite: MATH 140. A survey of fundamental mathematical concepts relevant to computer science. The objective is to address problems in computer science. Proof techniques presented are those used for modeling and solving problems in computer science. Discussion covers functions, relations, infinite sets, and propositional logic. Topics also include graphs and trees, as well as selected applications. Students may receive credit for only one of the following courses: CMSC 150 or CMSC 250.',
    },
    {
        'subj':'CMSC',
        'num':150,
        'title':'Introduction to Discrete Structures',
        'credits':3,
        'classNum':51439,
        'section':6381,
        'startDate':'21-May-18',
        'endDate':'15-Jul-18',
        'day':'',
        'time':'',
        'status':'Open',
        'location':'Online',
        'facultyLast':'Potolea',
        'facultyFirst':'Rodicia',
        'facultyMI':'',
        'description':'Prerequisite or corequisite: MATH 140. A survey of fundamental mathematical concepts relevant to computer science. The objective is to address problems in computer science. Proof techniques presented are those used for modeling and solving problems in computer science. Discussion covers functions, relations, infinite sets, and propositional logic. Topics also include graphs and trees, as well as selected applications. Students may receive credit for only one of the following courses: CMSC 150 or CMSC 250.',
    },
    {
        'subj':'CMSC',
        'num':330,
        'title':'Advanced Programming Languages',
        'credits':3,
        'classNum':51037,
        'section':6380,
        'startDate':'21-May-18',
        'endDate':'15-Jul-18',
        'day':'',
        'time':'',
        'status':'Open',
        'location':'Online',
        'facultyLast':'Elm',
        'facultyFirst':'Michael',
        'facultyMI':'A',
        'description':'Prerequisite: CMSC 230 or CMSC 350. A comparative study of programming languages. The aim is to write safe and secure computer programs. Topics include the syntax and semantics of programming languages and run-time support required for various programming languages. Programming projects using selected languages are required.',
    }
]

# Build a dictionary with one key, 'courses', whose value is the courses list
data = {'courses' : courses}

# Write data as json file
json.dump(data, fp=open('courses.json', 'w'), indent=4)