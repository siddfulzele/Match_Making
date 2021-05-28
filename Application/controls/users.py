from flask import *
import os
import base64
import mysql.connector
from controls.preprosess import preprosess

preprosess = preprosess()

class users(object):
	"""docstring for users"""
	def __init__(self):
		print("This is init Usere")

	_conn = mysql.connector.connect(user='root',password='',host='localhost',database='matchmaking',port=3306)
	_conn.autocommit = True
	_crsr = _conn.cursor()


	def Login(self,email,password):
		self.email = email
		self.password = password

		self._crsr.execute("SELECT * FROM user_master WHERE email = %s ;",[self.email])
		Data = self._crsr.fetchall()	
		print(Data)
		for data in Data :
			if data[2] == self.email and data[3] == self.password:
				session['username'] = data[1]
				session['user_id'] = data[0]
				session['user_email'] = data[2]				
				session['profile_status'] = data[4]								
				session['loggedIn'] = True				
				return True
		else:
			return False


	# def AllUsers(self):
	# 	self._crsr.execute("SELECT * FROM users ORDER BY u_id ASC;")
	# 	users = self._crsr.fetchall()
	# 	return users

	def RandomUser(self):		
		user = self.SingleUser()[0]
		print(user[2])		
		sql = "SELECT * FROM user_details where cluster_labels="+str(session['cluster_labels'])
		sql_end = " and username != '"+user[1]+"' ORDER BY RAND() LIMIT 6"
		sql_ext = ""
		if user[5]!='bisexual':
			if user[5]=='gay':
				sql_ext += " and sex = '"+str(user[4])+"'"
			elif user[5]=='straight':
				sql_ext += " and sex != '"+str(user[4])+"'"

		if user[2] <= 30:
			sql_ext += " and age < 30 "
		elif user[2]>30 and user[2]<=40:
			sql_ext += " and age BETWEEN 30 AND 40 "
		elif row[2]>41 and row[2]<=50: 
			sql_ext += " and age BETWEEN 41 AND 50 "    
		else:
			sql_ext += " and age > 50 "    

		print(sql+sql_ext+sql_end)
		self._crsr.execute(sql+sql_ext+sql_end)	
		rand_users = self._crsr.fetchall()
		return rand_users

	def SingleUser(self):
		self.username = session['username']
		self._crsr.execute("SELECT * FROM user_details where username = %s ;",[self.username])		
		user = self._crsr.fetchall()		
		session['cluster_labels'] = user[0][19]
		return user
	
	def Register(self,username,email,password,isProfileCompleted):
		self.username = username
		self.email = email
		self.password = password
		self.isProfileCompleted = isProfileCompleted
		self._crsr.execute("SELECT * FROM user_master where email = %s;",[self.email])
		Data = self._crsr.fetchall()
		count = 0
		print(Data)
		for data in Data :
			if data[2] == email:
				count = 1
				break
		if count == 1:
			return False
		else:			
			self._crsr.execute("INSERT INTO user_master(username,email,password,isProfileCompleted) VALUES(%s,%s,%s,%s)",(self.username,self.email,self.password,self.isProfileCompleted))
			return True

	def CompleteProfile(self,age,sex,height,drinks,orientation,status,smokes,drugs,education_level,dropped_out,job,interests,body_profile,pets,location,location_preference,bio):
		print("Hello Siddhant")
		print(session['username'])
		print(age,sex,height,drinks,orientation,status,smokes,drugs,education_level,dropped_out,job,interests,body_profile,pets,location,location_preference,bio)
		self._crsr.execute("INSERT INTO user_details(username,age,sex,height,drinks,orientation,status,smokes,drugs,education_level,dropped_out,job,interests,body_profile,pets,location,location_preference,bio) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(session['username'],age,sex,height,drinks,orientation,status,smokes,drugs,education_level,dropped_out,job,interests,body_profile,pets,location,location_preference,bio))
		sql = "UPDATE user_master set isProfileCompleted = '1' where username = '"+session['username']+"'"		
		self._crsr.execute(sql)


		self.cluster_number = preprosess.New_Data_Process()
		print("\n",self.cluster_number,"\n")
		sql = "UPDATE user_details set cluster_labels = "+str(self.cluster_number)+" where username = '"+session['username']+"'"
		print(sql)
		self._crsr.execute(sql)

		return True

'''
	def Update(self,first_name,middle_name,last_name,mobile,email,aadhar_no,dob,gender,address,pin_code,district,occu,photo):
		self._crsr.execute("SELECT * FROM users")
		Data = self._crsr.fetchall()
		count = 0
		for data in Data :
			if data[8] == aadhar_no or data[5] == email:
				count = 1
				break
		if count == 1:
			return False
		else:
			self.u_photo = self.uploadfile(photo)
			self.status = "Active"
			self._crsr.execute("UPDATE users SET u_first_name = %s,u_middle_name = %s,u_last_name = %s,u_mobile = %s,u_aadhar_no = %s,u_dob = %s,u_gender = %s,u_address = %s,u_pin_code = %s,u_districts = %s,u_occupation = %s,u_photo = %s WHERE u_email = %s",(first_name,middle_name,last_name,mobile,aadhar_no,dob,gender,address,pin_code,district,occu,self.u_photo,email))

			return True

	def UpdateIncome(self,income):
		update = self._crsr.execute("UPDATE users SET u_income= %s WHERE u_email = %s",(income,session['u_email']))
		return True


	def uploadfile(self,photo):
		APP_ROOT = os.path.dirname(os.path.abspath(__file__))
		target = os.path.join(APP_ROOT,'../static/images/')
		print(target)
		filename = photo.filename
		print(target)
		destination = "/".join([target,filename])
		print(destination)
		photo.save(destination)
		return filename
'''