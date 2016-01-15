from flask import Flask, request, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from twilio.rest import TwilioRestClient 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/emails'
db = SQLAlchemy(app)

#################################
#################################
########### ?? MODELS ?? ############
#################################
#################################

#any changes made here require the DB or at least table to be thrown out and replaced... so yeah or i guess that is what migrations are called. 


# Create our database model
class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True)
	phone = db.Column(db.String, unique=False)
	user_list = db.Column(db.String, unique =False)
	phone = db.Column(db.String, unique=False)
	first_name = db.Column(db.String(120), unique=False)
	last_name = db.Column(db.String(120), unique=False)


	def __init__(self, email, phone, first_name, last_name, user_list):
		self.email = email
		self.phone = phone
		self.first_name = first_name
		self.last_name = last_name
		user_list = user_list
	
	def __repr__(self):
		return '<E-mail %r>' % self.email


'''
class userList(db.Model):
	__tablename__ = "user_lists"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True)
'''

#new class here for text messages
class TextMessage(db.Model):
	__tablename__ = "messages"
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, primary_key=False, unique=False)
	message = db.Column(db.String, primary_key=False, unique=False)
	input_time = db.Column(db.DateTime, server_default=db.func.now())

	def __init__(self, title, message):
		self.title = title
		self.message = message

	def __repr__(self):
		return "<Message-Title'%s'>" % self.title


#new class/ object for a record - use this to record all messages that get sent
class MessageSentRecord(db.Model):
	__tablename__ = "sentmessages"
	id = db.Column(db.Integer, primary_key=True)
	#the unique ID of the TextMessage object that was sent
	message_id = db.Column(db.Integer, primary_key=False, unique = False)
	sent_date = db.Column(db.DateTime, server_default=db.func.now())
	#ID of the text recipient, either individual or group?
	contact_id = db.Column(db.Integer)

	def __init__(self, message_id, contact_id):
		self.message_id = message_id
		self.contact_id = contact_id

	def __repr__(self):
		return '<Text Record %s>' % self.message_id

#################################
#################################
######## CONTROLLERS?? ##########
#################################
#################################


@app.route('/viewContacts')
def viewContacts():
	#will one day need this to handle paganation ^ would have an option variable above /x or something or #x or is it more ?pg=x and then do some math below and we'd be all set. 
	#send the view thingy the links to the 'next' page as well as the 'previous' page
	#contacts = User.query.order_by(User.last_name).limit(25).all()
	#import pdb; pdb.set_trace()
	

	#import pdb; pdb.set_trace()

	contacts = User.query.limit(25).all()

	return render_template('view_contacts.html', contacts=contacts)



# Set "homepage" to index.html
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/createGroup', methods=['GET'])
def createGroup():
	return 'yeah so create a contact group'

@app.route('/viewMessages', methods=['GET'])
def viewMessages():
	#just need to render the messages now... 
	messages = TextMessage.query.order_by(TextMessage.input_time.desc()).limit(25).all()
	

	#import pdb; pdb.set_trace()

	return render_template('view_all_messages.html', msg=messages)


#add a text message to the database
@app.route('/messages', methods=['POST'])
def messages():
	#need to add the message to the database here, then navigate to the view of all the messages in the database - or the most recent X number
	if request.method == "POST":
		text_title = request.form['message_title']
		text_body = request.form['message_body']
		reg = TextMessage(text_title,text_body)
		db.session.add(reg)
		db.session.commit()

	#import pdb; pdb.set_trace()
	#will need to send the results of something, the query for all the messages to this template to have them printed out 

	#should render a 'congratulations the message was save type screen'

	#send_text('6508628723',text_body)  #this sends the text messgae. but now need to select a user to send the text message to directly 
	return render_template('view_saved_message.html', msg = reg)

def send_text(phone, message):
	# put your own credentials here 
	ACCOUNT_SID = "ACc25ceda583592ac491961e452ed64fe8" 
	AUTH_TOKEN = "f7312464f586255996cb8e8243d2c03c" 
 
	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
 	
	phone = int(phone)
	client.messages.create(
		to=phone, 
		from_="+14433992887", 
		body=message,  
	)

def record_text_sent(message_id, contact_id):
	#create new record/object to record the transaction. may need to update to include a list of IDs or maybe a contact_ID could be a group
	record = MessageSentRecord(message_id, contact_id)
	db.session.add(record)
	db.session.commit()

@app.route('/sendMessage', methods=['GET'])
def sendMessage():
	#now want to select message from list of saved messages
	#then select phone number from list of contacts
	#then send the text message to that phone number. 
	#this will instead need to grab the text message and the
	messages = TextMessage.query.order_by(TextMessage.input_time.desc()).limit(25).all()
	contacts = User.query.limit(25).all()

	return render_template('send_message.html', messages = messages, contacts = contacts)


@app.route('/messageSent', methods=['POST'])
def messageSent():
	if request.method == "POST":
		message_id = request.form['message_id']
		contact_id = request.form['contact_id']
	#need to actually send the message
	#grab the shit from the post
	#send the shit to the phone
		text_body = TextMessage.query.get(int(message_id)).message
		contact_phone = User.query.get(int(contact_id)).phone
		
		send_text(contact_phone,text_body)
		#grab the parameters from the form
		
		#now make a record of this action
		record_text_sent(message_id, contact_id)


		#here need to send the message and who it was sent to to the message confirmation screen
		html = "message id: " + str(message_id) + "  contact_id: " + str(contact_id) + "<br>" 
		#+ render_template('messageSent.html')
	return  render_template('messageSent.html', text = html)

@app.route('/viewHistory',methods=['GET'])
def viewHistory():
	history = MessageSentRecord.query.limit(25).all()
	headers = ['message_id','sent_date','contact_id']
	
	return render_template('viewHistory.html',results = history, headers = headers, len = len(headers))


# Save e-mail to database and send to success page
@app.route('/prereg', methods=['POST'])
def prereg():
	email = None
	if request.method == 'POST':
		email = request.form['email']
		# Check that email does not already exist (not a great query, but works)
		phone = request.form['phone']

		first_name = request.form['first_name']
		last_name = request.form['last_name']

		user_list = 1

		if not db.session.query(User).filter(User.email == email).count():
			#reg = User(email)
			reg = User(email, phone, first_name, last_name, user_list)
			db.session.add(reg)
			db.session.commit()
			return render_template('success.html')
	return render_template('index.html')

#@app.route('', method=[''])


if __name__ == '__main__':
	app.debug = True
	app.run()

