from flask import *
import os
import base64
import mysql.connector
import numpy as np
import pandas as pd

import re 
import string
import nltk
from nltk.corpus import words, stopwords
import pickle 
# Setting options

pd.set_option('display.max_colwidth', -1)
nltk.download('stopwords')
nltk.download('words')

# Load stop words
stop_words = stopwords.words('english')
wordlist = words.words()


class preprosess(object):
	"""docstring for users"""
	def __init__(self):
		print("This is init preprosess")		

	_conn = mysql.connector.connect(user='root',password='',host='localhost',database='matchmaking',port=3306)
	_conn.autocommit = True
	_crsr = _conn.cursor()

	def pet_encoding(self,x):
	    if x=='likes dogs and likes cats':
	        return [1,1,0,0,0,0]
	    
	    elif x=='likes dogs':
	        return [1,0,0,0,0,0]
	    
	    elif x=='likes dogs and has cats':
	        return [1,1,0,1,0,0]
	    
	    elif x=='has dogs':
	        return [1,0,1,0,0,0]
	    
	    elif x=='has dogs and likes cats':
	        return [1,1,1,0,0,0]
	    
	    elif x=='likes dogs and dislikes cats':
	        return [1,0,0,0,0,1]
	    
	    elif x=='has dogs and has cats':
	        return [1,1,1,1,0,0]
	    
	    elif x=='has cats':
	        return [0,1,0,1,0,0]
	    
	    elif x=='likes cats':
	        return [0,1,0,0,0,0]
	    
	    elif x=='has dogs and dislikes cats':
	        return [1,0,1,0,0,1]
	    
	    elif x=='dislikes dogs and dislikes cats':
	        return [0,0,0,0,1,1]
	    
	    elif x=='dislikes dogs and likes cats':
	        return [0,1,0,0,1,0]
	    
	    elif x=='dislikes dogs':
	        return [0,0,0,0,1,0]
	    
	    elif x=='dislikes dogs and has cats':
	        return [0,1,0,1,1,0]
	    
	    elif x=='dislikes cats':
	        return [0,0,0,0,0,1]
	    else:
	        print('Error'+x)

	def drop_punc(self,my_text):
	    clean_text = re.sub('[%s]' % re.escape(string.punctuation), ' ', my_text)
	    return clean_text

	# Function for making all text lowercase
	def lower_case(self,my_text):
	    clean_text = my_text.lower()
	    return clean_text

	# Function for removing all numbers
	def remove_numbers(self,my_text):
	    clean_text = re.sub('\w*\d\w*', '', my_text)
	    return clean_text

	# Function for removing emojis
	def deEmojify(self,inputString):
	    return inputString.encode('ascii', 'ignore').decode('ascii')

	# Function for removing stop words
	def remove_stop(self,my_text):
	    text_list = my_text.split()
	    return ' '.join([word for word in text_list if word not in stop_words])

	# Function for stripping whitespace
	def my_strip(self,my_text):
	    try: return my_text.strip()
	    except Exception as e: return None

	# Curated list of additional stop-words for this project

	# Function for removing my stop words
	def remove_my_stop(self,my_text):
	    my_stop_words = ['mmmmm','im']
	    text_list = my_text.split()
	    return ' '.join([word for word in text_list if word not in my_stop_words])

	## to determine the language of the bio

	# Function to detect english
	def is_english(self,my_text):
	    if my_text is None:
	        return my_text
	    text_list = my_text.split()
	    english = 0
	    non_english = 0
	    for word in text_list:
	        if word not in wordlist:
	            non_english += 1
	        else:
	            english += 1
	    if english > 0.25*non_english:
	        return True
	    else: return False


	def nmf_predict(self,text):
		topics = ['Knowing each other','Explore','Full of life','Fun Partner','Easy Going','Meeting new people']
		#nmf_model_tf_idf_file = open('nmf_model_tf_idf.pkl','rb')	
		nmf_model_tf_idf = pickle.load(open('nmf_model_tf_idf.pkl','rb'))

		tf_idf_file =  open('tf_idf.pkl','rb')
		tf_idf = pickle.load(tf_idf_file)  
		
		text_vect = tf_idf.transform([text])
		result = nmf_model_tf_idf.transform(text_vect)
		return topics[np.argmax(result)]


	def New_Data_Process(self):
		self.username = session['username']
		self._crsr.execute("SELECT * FROM user_details where username = %s ;",[self.username])
		db_column_names = ['user_id', 'username', 'age', 'status', 'sex', 'orientation', 'drinks', 'drugs', 'height', 'job', 'location', 'pets', 'smokes', 'body_profile', 'education_level', 'dropped_out', 'bio', 'interests', 'location_preference', 'cluster_labels']
		new_row = self._crsr.fetchone()
		new_row = list(new_row)
		data_dict = {}
		for i in range(len(new_row)):
			data_dict[db_column_names[i]] = new_row[i]
		new_data = pd.DataFrame([data_dict])

		data = pd.read_csv("user_details.csv")

		new_data.drop(['cluster_labels'],axis=1,inplace=True)
		data = data.append(new_data,ignore_index=True)
		data.drop(['user_id','username','sex','height'],axis=1,inplace=True)
		data['education_level'] = data['education_level'].astype(str).astype(int)
		#Age
		data['age'] = data['age'].astype(str).astype(int)
		data['age']=data['age'].apply(lambda x: 58 if x>58 else x)
		data['age']=data['age'].apply(lambda x:'18-30' if x<=30 else('31_40' if x>30 and x <=40 else('41_50' if x>40 and x<=50 else '50+')))
		dummies=pd.get_dummies(data['age'],drop_first=True)
		data=pd.concat([data,dummies],axis=1)
		data.drop('age',axis=1,inplace=True)
		#Drinks & Drugs & Orientation
		data['drinks']=data['drinks'].apply(lambda x:'rarely' if x=='very often' else ('often' if x=='desperately' else x))
		data['drugs']=data['drugs'].apply(lambda x: 'sometimes' if x=='often' else x)
		dummies=pd.get_dummies(data[['drinks','drugs','orientation']],drop_first=True)
		data=pd.concat([data,dummies],axis=1)
		data=data.drop(['drinks','drugs','orientation'],axis=1)
		#Smokes
		data['smokes']=data['smokes'].apply(lambda x: 'sometimes' if x=='when drinking' or x=='trying to quit' else x)
		dummies=pd.get_dummies(data['smokes'],drop_first=True)
		dummies=dummies.rename(columns={'sometimes':'smokes_sometimes','yes':'smokes_yes'})
		data=pd.concat([data,dummies],axis=1)
		data.drop('smokes',axis=1,inplace=True)
		#Body Profile
		data['body_profile']=data['body_profile'].apply(lambda x:'skinny' if (x=='skinny' or x=='thin' or x=='used up')
                                                       else('athletic' if(x=='athletic' or x=='jacked') 
                                                       else('fit' if (x=='average' or x=='fit')
                                                       else('above average' if (x=='curvy' or x=='full figured' or x=='a little extra')else 'fat'))))
		dummies=pd.get_dummies(data['body_profile'],drop_first=True)
		data=pd.concat([data,dummies],axis=1)		
		data.drop('body_profile',axis=1,inplace=True)
		#Status
		data['status']=data['status'].apply(lambda x:'single' if x=='single' else 'other')
		dummies=pd.get_dummies(data['status'],drop_first=True)
		data=pd.concat([data,dummies],axis=1)
		data.drop('status',axis=1,inplace=True)
		#interests
		data['interests'] = data['interests'].str.lower()
		data['interests']=data['interests'].apply(lambda x:'music' if x=='music' or x=='singinig' or x=='instruments' or x=='dance'
		                                             else('artist' if x=='calligraphy' or x=='diy' or x=='painting' or x=='sketching' or x=='designing' or x=='craft' 
		                                             else('game_video' if x=='video games' or x=='social_networking'
		                                             else ('outdoor' if x=='fishing' or x=='sports' or x=='yoga' or x=='camping'
		                                             else('movies' if x=='movies' or x=='acting' or x=='makeup'
		                                             else ('read/write' if x=='reading' or x=='writting' else x))))))

		dummies=pd.get_dummies(data['interests'])
		dummies.drop('artist',axis=1,inplace=True)
		data=pd.concat([data,dummies],axis=1)		
		data.drop('interests',axis=1,inplace=True)
		#dropped_out
		dummies=pd.get_dummies(data['dropped_out'],drop_first=True)
		dummies=dummies.rename(columns={'yes':'dropped_out_yes'})
		data=pd.concat([data,dummies],axis=1)
		data.drop('dropped_out',axis=1,inplace=True)
		#location_preference
		dummies=pd.get_dummies(data['location_preference'],drop_first=True)
		dummies=dummies.rename(columns={'same city':'location_same_city','same state':'location_same_state'})
		data=pd.concat([data,dummies],axis=1)
		data.drop('location_preference',axis=1,inplace=True)
		#location
		data['location']=data['location'].str.lower()
		data['location']=data['location'].apply(lambda x: x.split(', ')[0])
		top_20_locations=['san francisco','oakland','berkeley','san mateo','palo alto','san rafael','alameda','san leandro','redwood city','emeryville','daly city','walnut creek','hayward','pacifica','el cerrito','menlo park','martinez','benicia','richmond','burlingame']
		data['location']=data['location'].apply(lambda x: x if x in top_20_locations else "location_other")	
		dummies=pd.get_dummies(data['location'])
		dummies = dummies[['benicia', 'berkeley', 'burlingame', 'daly city', 'el cerrito',
		       'emeryville', 'hayward', 'location_other', 'martinez', 'menlo park',
		       'oakland', 'pacifica', 'palo alto', 'redwood city', 'richmond',
		       'san francisco', 'san leandro', 'san mateo', 'san rafael',
		       'walnut creek']]
		data=pd.concat([data,dummies],axis=1)
		data.drop('location',axis=1,inplace=True)
		#JOb
		data['job']=data['job'].apply(lambda x:'science / tech / engineering' if x=='computer / hardware / software'
                                       else('other' if (x=='rather not say' or x=='unemployed' or x=='retired' or x=='military' or
                                                       x=='transportation' or x=='political / government' or x=='clerical / administrative'
                                                       or x=='hospitality / travel'  or x=='construction / craftsmanship' or x=='law / legal services')
                                           else x)
                                       )
		data['job']=data['job'].apply(lambda x:'other_job' if x=='other' else x)
		dummies=pd.get_dummies(data['job'])
		dummies.drop('artistic / musical / writer',axis=1,inplace=True)
		data=pd.concat([data,dummies],axis=1)	
		data.drop('job',axis=1,inplace=True)

		#Pet		
		col_name=['likes dogs','likes cats','has dog','has cat','dislikes dogs','dislike cats']
		for i in col_name:
		    data[i]=''
		for i in range(len(data['pets'])):
		    results=self.pet_encoding(data['pets'][i].lower())		   
		    for j in range(len(results)):
		        data[col_name[j]][i]=results[j]
		data.drop('pets',axis=1,inplace=True)

		#BIO
		
		last_row = data.tail(1)			
		#last_row['bio_cleaned'] = self.deEmojify(self.remove_numbers(self.drop_punc(self.lower_case(last_row['bio']))))
		#last_row['bio_cleaned'] = self.remove_my_stop(self.remove_stop(last_row['bio_cleaned']))
		last_row['bio_cleaned'] = last_row['bio'].apply(self.lower_case).apply(self.drop_punc).apply(self.remove_numbers).apply(self.deEmojify)
		last_row['bio_cleaned'] = last_row['bio_cleaned'].apply(self.remove_stop).apply(self.remove_my_stop)
		last_row['bio_cleaned'] = last_row['bio_cleaned'].str.strip()

		
		topics = ['Knowing each other','Explore','Full of life','Fun Partner','Easy Going','Meeting new people']
		test_bio = list(last_row['bio_cleaned'])[0]
		bio_label = self.nmf_predict(text=test_bio)
		temp = pd.DataFrame(np.zeros(shape=(1,len(topics))), columns = topics)
		for x in topics:
		    if bio_label == x:
		        temp[x] = 1
		temp.drop(['Easy Going'],axis=1,inplace=True)
		temp.index = last_row.index
		final_row = pd.concat([last_row,temp],axis=1)
		final_row.drop(['bio','bio_cleaned'],axis=1,inplace=True)

		with open('logistic_regression_model.pkl', 'rb') as file:
		    model = pickle.load(file)

		test=final_row.iloc[0,:]
		test=np.array(test).reshape((1,-1))

		cluster_number=model.predict(test)
		cluster_number=int(cluster_number)
	
		return cluster_number
