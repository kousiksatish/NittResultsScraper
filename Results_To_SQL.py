import MySQLdb
import sys
import ast

info = sys.argv[1] # name of file
courseTable = sys.argv[2] # name of course table
semNo = sys.argv[3] # sem no
yearNo = sys.argv[4] # year no
dept = sys.argv[5] # department
tablePrefix = sys.argv[6] # table Prefix
table = tablePrefix + dept # actual table name is concatenation of tablePrefix and dept

#DB CONFIG
DB_HOST = "***"
DB_USERNAME = "***"
DB_PASSWORD = "***"
DB_NAME = "***"

# Retrieve 3rd line of file
filep = open(info)
for i,line in enumerate(filep):
	if i==2:
		data = ast.literal_eval(line)

# Remove undefined Roll numbers
data = [student for student in data if "Name" in student]
temp = []
courses = []
compul = []

#Loop for each entry
for student in data:
	temp = []
	for course in student['Entries']:
		temp.append(course['CourseCode'] + ' : ' + course['CourseName']+' : '+course['Credit'])
	if not courses :
		courses = set(temp)
		compul = set(temp)
	elif compul.intersection(temp):
		courses = courses.union(temp)
		compul = compul.intersection(temp)
	else:
		print("Ommit" + student['Rollno'])
		courses = set(courses)


elec = courses
elec = elec.difference(compul)
# print compul # contains Compulsory courses
# print courses # contains All courses
# print elec # contains Elective courses

# DB OPERATIONS

# DB Connection and retrieval of cursor
db=MySQLdb.connect(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);
cur=db.cursor()

for course in courses:
	loggit = "INSERT INTO `" + courseTable + "` (`CourseCode`, `CourseName`, `Credits`, `Nature`, `Dept`, `Sem`, `Year`) VALUES ("
	loggit = loggit + "'" + course[:5] +"', "
	loggit = loggit + "'" + course[8:-4] +"', "
	loggit = loggit + "'" + course[-1:] + "', "
	if course in compul:
		loggit = loggit + "'compul', "
	elif course in elec:
		loggit = loggit + "'elec', "
	loggit = loggit + "'" + dept + "', '"+ semNo +"', '" + yearNo + "');"
	# print loggit
	cur.execute(loggit)


db.commit()

print 'Course table updated'

loggit = "CREATE TABLE `"+table+"` ("
loggit = loggit + '`RollNo` int(11) DEFAULT NULL,  `Name` char(35) DEFAULT NULL, '
for new in courses:
	loggit = loggit + '`' + new[:5] + '` int(2)'
	if new in compul:
		loggit = loggit + ' DEFAULT NULL, '  
	elif new in elec:
		loggit = loggit + ' DEFAULT 2, '
loggit = loggit + '`gpa` float DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1;'
cur.execute(loggit)
db.commit()

print 'Table created for the department'


for student in data:
	info = {}
	info['RollNo'] = student['Rollno']
	info['Name'] = student['Name']
	info['gpa'] = student['GPA']

	for course in student['Entries']:
		if(len(course['CourseCode']) == 4):
			course['CourseCode'] = course['CourseCode'] + '0'
		if(course['Grade']=='S'):
			grade='10'
		elif(course['Grade']=='A'):
			grade='9'
		elif(course['Grade']=='B'):
			grade='8'
		elif(course['Grade']=='C'):
			grade='7'
		elif(course['Grade']=='D'):
			grade='6'
		elif(course['Grade']=='E'):
			grade='5'
		elif(course['Grade']=='U'):
			grade='0'
		elif(course['Grade']=='Z'):
			grade='0'
		elif(course['Grade']=='F'):
			grade='0'
		elif(course['Grade']=='V'):
			grade='0'
		info[course['CourseCode']] = grade

	str = ''
	val = ''
	for key in info:
		str = str + '`' + key + '`, '
		val = val + "'" + info[key] + "', "
	
	str = str[:-2]
	val = val[:-2]
	loggit = "INSERT INTO " + table + " (" + str + ")" + " VALUES (" + val + ");"
	# print loggit
	cur.execute(loggit)
	db.commit()


print 'Entries updated in the table'

