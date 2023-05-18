# This script is used to deploy a beta test phase on Moodle for teachers, using the teacher list of the current Moodle and a test course to duplicate.
# Each teacher will be registred as a teacher in a copy of the test course on the beta Moodle.
# The key used for find the teacher on the beta Moodle is the email (email = username)
# Method used for logging is oatuh2

# Get the list of teachers from the current Moodle with sql report : ->
# Export the report as csv file and name it teacher_list.csv

# Autor : Maxime Cruzel
# Date : 2023-05-17
# Version : 1.0

import csv
import requests
import json
import time
import urllib.parse

class teachers:
    list_of_teachers = []
    
class config:
    login_ws = ''
    password_ws = ''
    url = ''
    categoryid_of_courses = 0 # the cateryid where to create the courses
    courseid_to_duplicate = 0 # the course to duplicate
    course_name_prefix = 'Cours BETA v1 - '
    course_shortname_prefix = 'BETAv1 - '
    
def request_ws(ws, param_request):
    login = config.login_ws
    password = config.password_ws
    password = urllib.parse.quote(password)
    url_moodle = config.url
    time.sleep(0.05)
    request_url = url_moodle+"webservice/rest/simpleserver.php?wsusername="+str(login)+"&wspassword="+str(password)+"&moodlewsrestformat=json&wsfunction="+ws+"&"
    webservice_reponse_content = requests.get(request_url, params=param_request)
    webservice_reponse_content_formated = json.loads(webservice_reponse_content.text)
    return webservice_reponse_content_formated

def create_user(teacher):
    username = teacher[0].lower() # Moodle accept email with uppercase, but not username
    ws = 'core_user_create_users'
    param_request = {
        'users[0][username]': username,
        'users[0][auth]': 'oauth2',
        'users[0][firstname]': teacher[1],
        'users[0][lastname]': teacher[2],
        'users[0][email]': teacher[0],
    }
    user_created = request_ws(ws, param_request)
    print(user_created)

        
    userid_created = user_created[0]['id']
    return userid_created

def create_course(teacher_firstname, teacher_lastname):
    ws = 'core_course_duplicate_course'
    param_request = {
        'courseid': config.courseid_to_duplicate,
        'fullname': config.course_name_prefix+teacher_firstname+' '+teacher_lastname,
        'shortname': config.course_shortname_prefix+teacher_firstname+' '+teacher_lastname,
        'categoryid': config.categoryid_of_courses
    }
    response_ws = request_ws(ws, param_request)
    
    # in case of teacher have multiple accounts on the main Moodle, this will cause an error because
    # the shortname of the course will be the same as another course
    if 'errorcode' in response_ws:
        if response_ws['errorcode'] == 'shortnametaken':
            ws = 'core_course_get_courses_by_field'
            param_request = {
            'field': 'shortname',
            'value': config.course_shortname_prefix+teacher_firstname+' '+teacher_lastname
            }
            courseid = request_ws(ws, param_request)['courses'][0]['id']
            return courseid # so we return the courseid of the course already created
        else:
            print(f'Fatal Error while creating course : {response_ws["message"]}')
            exit()
    else:
        courseid = response_ws['id']
        return courseid

def enrol_teacher_in_course(userid, courseid):
    ws = 'enrol_manual_enrol_users'	
    param_request = {
        'enrolments[0][roleid]': 3,
        'enrolments[0][userid]': userid,
        'enrolments[0][courseid]': courseid
    }
    response_ws = request_ws(ws, param_request)
    print(response_ws)
    
# read csv teacher_list.csv
with open('teacher_list.csv', newline='', encoding="utf8") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    # skip csv header
    next(csvreader)
    for row in csvreader:
        email = row[3]
        firstname = row[4]
        lastname = row[5]
        if email not in teachers.list_of_teachers:
            teachers.list_of_teachers.append([email, firstname, lastname])

# try to find the teacher on the beta Moodle
scanned_teachers = []
for teacher in teachers.list_of_teachers:
    if teacher[0] in scanned_teachers:
        continue
    
    teacher_email = teacher[0]
    teacher_firstname = teacher[1]
    teacher_lastname = teacher[2]
    param_request = {
        'criteria[0][key]': 'email',
        'criteria[0][value]': teacher_email
        }
    response_ws = request_ws('core_user_get_users', param_request)

        
    if len(response_ws['users']) == 0: # if the teacher is not found on Moodle
        print("Teacher not found : "+teacher_email)
        # create the teacher account on the beta Moodle
        userid = create_user(teacher)
        print("Teacher created : "+teacher_email)
        # create the course on the beta Moodle
        courseid = create_course(teacher_firstname, teacher_lastname)
        # enrol the teacher in the course
        enrol_teacher_in_course(userid, courseid)
        scanned_teachers.append(teacher_email)
    else: # if the teacher is found on Beta Moodle
        userid = response_ws['users'][0]['id']
        # Verify of the course is already created
        ws = 'core_course_get_courses_by_field'
        param_request = {
            'field': 'shortname',
            'value': config.course_shortname_prefix+teacher_firstname+' '+teacher_lastname
        }
        courses_found = request_ws(ws, param_request)
        if len(courses_found['courses']) > 0:
            print("Course already created : "+teacher_email)
            # Verify if the teacher is already enrolled in the course
            ws = 'core_enrol_get_enrolled_users'
            param_request = {
                'courseid': courses_found['courses'][0]['id']
            }
            enrol_found = request_ws(ws, param_request)
            if len(enrol_found)>0: # if the course have multiple users we need to check if the teacher is enrolled
                for user in enrol_found:
                    if user['id'] == userid:
                        print("Teacher already enrolled in the course : "+teacher_email)
                        continue
                    else:
                        # enrol the teacher in the course
                        print("Teacher not enrolled in the course : "+teacher_email)
                        enrol_teacher_in_course(userid, courses_found['courses'][0]['id'])
                        continue
            else: # if the course have not users, we are sure that the teacher is not enrolled
                # enrol the teacher in the course
                print("Teacher not enrolled in the course : "+teacher_email)
                enrol_teacher_in_course(userid, courses_found['courses'][0]['id'])
                continue
        else:
            # Teacher exist but course not found
            
            print("Teacher found : "+teacher_email)
            # create the course on the beta Moodle
            courseid = create_course(teacher_firstname, teacher_lastname)
            # enrol the teacher in the course
            enrol_teacher_in_course(userid, courseid)
            scanned_teachers.append(teacher_email)
            
