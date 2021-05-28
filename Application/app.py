from flask import *
from controls.users import users


app = Flask(__name__)

user = users()

@app.route('/')
def main():
	return redirect(url_for('login'))
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		user_pass = request.form['password']
		result = user.Login(email,user_pass)
		if result == True:
			print(session.get('profile_status'))
			if session.get('profile_status') == '1':
				return redirect(url_for('userHome'))
			else:
				return redirect(url_for('completeProfile'))
		else:			
			flash('Username or Password Not Match', 'danger')
			return redirect(url_for('login'))
	return render_template("login.html")

@app.route('/userHome')
def userHome():
	if session.get('loggedIn') == True:
		curr_user = user.SingleUser()
		rand_users = user.RandomUser()				
		data = curr_user + rand_users		
		return render_template('user/userhome.html',data=data)
	else:
		return redirect(url_for('login'))

@app.route('/user_logout')
def user_logout():
   # remove the username from the session if it is there
   session.pop('username',None)
   session.pop('user_id',None)
   session.pop('loggedIn', None)   
   return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		re_password = request.form['re_password']
		if re_password == password:
			isProfileComplete = '0'
			result = user.Register(username,email,password,isProfileComplete)
			if result == True:			
				flash('You are Registration Success... now goto login', 'success')
				return redirect(url_for('login'))
			else:
				error = "Email id already in use"
				return render_template("register.html",error=error)	
		else:
			error = "Password missMatch"
			return render_template("register.html",error=error)

	return render_template("register.html")


@app.route('/completeProfile',methods=['GET','POST'])
def completeProfile():
	if request.method == 'POST':
		age = request.form['age']
		sex = request.form['sex']
		height = request.form['height']
		drink = request.form['drink']
		orientation = request.form['orientation']
		status = request.form['status']
		smokes = request.form['smokes']
		drugs = request.form['drugs']
		education_level = request.form['edu_level']
		dropped_out = request.form['dropped_out']
		job = request.form['job']
		interests = request.form['interests']
		body_profile= request.form['body_profile']
		pet = request.form['pet']
		location = request.form['location']
		location_preference= request.form['location_preference']
		bio = request.form['bio']
		print(bio)
		result = user.CompleteProfile(age,sex,height,drink,orientation,status,smokes,drugs,education_level,dropped_out,job,interests,body_profile,pet,location,location_preference,bio)
		if result == True:
			return redirect(url_for('userHome'))
	return render_template("user/userprofileform.html")

app.secret_key = 'siddfulzele26'
if __name__ == '__main__':
   app.run(debug=True)
