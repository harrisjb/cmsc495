# cmsc495
Project for CMSC495

This project utilizes Python 3.x, AWS Lambda, AWS Dynamo DB, and the
Alexa SDK.



A web scraper written in Python takes UMUC course data, pushes the data to a
lambda function that saves the info to a Dynaomo DB table. That table is
then utilized by an Alexa skill allowing students to get info on
upcoming classes.



We used [Amazon's Python Alexa
SDK](https://github.com/alexa-labs/alexa-skills-kit-sdk-for-python)
which remains in beta, in order to create the skill. 


[Demo of the skill](https://www.youtube.com/watch?v=yr9jMEmBVPQ)
