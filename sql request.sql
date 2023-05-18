SELECT u.id AS 'userid', r.id AS 'roleid', u.username, u.email, u.firstname, u.lastname, CONCAT(u.firstname,' ', u.lastname) AS 'user_names', c.shortname AS 'coursename', c.id AS 'courseid', cc.id AS 'categoryid', cc.name AS 'categoryname', ccc.name AS 'parent1categoryname', r.shortname AS 'role_shortname'
FROM prefix_user u
INNER JOIN prefix_role_assignments ra ON ra.userid = u.id
INNER JOIN prefix_context ct ON ct.id = ra.contextid
INNER JOIN prefix_course c ON c.id = ct.instanceid
INNER JOIN prefix_role r ON r.id = ra.roleid
INNER JOIN prefix_course_categories cc ON cc.id = c.category
INNER JOIN prefix_course_categories ccc ON cc.parent = ccc.id
WHERE (r.id = 4 OR r.id = 3) AND c.shortname NOT LIKE '%📁%'
