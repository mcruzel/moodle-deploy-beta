# moodle-deploy-beta
Deploy account and courses on a beta Moodle platform with :
- The extract of teacher list from the production platform (downloaded csv file generated by a custom report)
- A course model, which will be duplicated for each teacher

All accounts will be generated with an oauth2 authentication with the email of the account of production plaform.
In case of duplicate accounts (with different emails), all accounts will be registred in the same course (unless first and last name are not identical between the accounts)

Don't forget to edit config class on the script.

# Prerequisites on Moodle
- You need to create a course model on the beta platform
- Custom reports plugin, and 1 report (check the sql file in this git)
- An account for webservices (login+password), NOT A TOKEN

# List of used webservices :
- core_user_create_users
- core_course_duplicate_course
- enrol_manual_enrol_users
- core_user_get_users
- core_course_get_courses_by_field
- core_enrol_get_enrolled_users

# SQL File
The request will ignore courses in root category.
