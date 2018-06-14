import json

# Open the json file and load the json into variable 'data'
with open('dummydata.json', 'r') as file:
    data = json.load(file)

# If we print the data, it looks exactly like the form of a Python dictionary
# There is only one key, 'courses' whose value is a list of dictionaries for each course.
print(data)

print()

# Looking at each course as a separate dictionary:
courses = data['courses']
for course in courses:
    print(course)

print()

# Now, just like dictionaries, we can access the values by their key.
# For example, we can print the course subject and number along with the course title for each course in the list:
for course in courses:
    print(course['subj'] + ' ' + str(course['num']) + ' - ' + course['title'])