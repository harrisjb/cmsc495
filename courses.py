# Filename: courses.py
# Author: Shawn R Moses
# Date: July 3, 2018
# Current Version: s
# Description: Import the JSON file course information to AWS Dynamodb table "info".

from __future__ import print_function
import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1', endpoint_url="http://localhost:8000")
table = dynamodb.Table('info')

with open("/Users/MrMoses313/Documents/CMSC 495 6380/CMSC 495 WEEK 7/UMUC_classes/courses.json") as json_file:
    courses = json.load(json_file, parse_float=decimal.Decimal)
    for course in courses:
        subj = course['subj']
        num = int(course['num'])
        title = course['title']
        credits = int(course['credits'])
        classNum = int(course['classNum'])
        section = int(course['section'])
        startDate = int(course['startDate'])
        endDate = int(course['endDate'])
        day = course['day']
        time = int(course['time'])
        status = course['status']
        location = course['location']
        facultyFirst = course['facultyFirst']
        facultyLast = course['facultyLast']
        facultyMI = course['facultyMI']
        description = course['description']
        prereq = course['prereq']

        print("Adding courses:", subj, num)

        table.put_item(
           Item={
                'subj': subj,
                'num': num,
                'title': title,
                'credits': credits,
                'classNum': classNum,
                'section': section,
                'startDate': startDate,
                'endDate': endDate,
                'day': day,
                'time': time,
                'status': status,
                'location': location,
                'facultyFirst': facultyFirst,
                'facultyLast': facultyLast,
                'facultyMI': facultyMI,
                'description': description,
                'prereq': prereq
            }
)