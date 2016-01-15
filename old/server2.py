import telegram
from time import sleep
import json, requests
from requests.auth import HTTPBasicAuth
from decimal import Decimal
import MySQLdb
import random

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2



def returnDBCursor(host = "127.0.0.1", user = "root", password = "" , db = "watsonbot"):
    db = MySQLdb.connect(host=host,    
                     user=user,
                     db=db)
    cur = db.cursor()
    return db, cur

def checkId(cur, userId):
    cur.execute("select * from users where id = " + str(userId))     
    if len(list(cur)) > 0:    
      return True
    else: return False

def insertNewUser(db, cur, userId, update):
    
    if update.first_name:    
        firstName = update.first_name
    else:
        firstName = ""

    if update.last_name:  
        lastName = update.last_name
    else:
        lastName = ""
    query = "insert into users (id, first_name, last_name, current_step, museum_preference) values (" + str(userId) + ", '" + firstName + "', '" + lastName + "',0,1)"
    cur.execute(query)
    db.commit()

def deleteUser(db, cur, userId):
	query = "DELETE FROM users WHERE id = " + str(userId)
	cur.execute(query)
	db.commit()
    
def userHasPreference(cur, userId, preference):
	query = "select " + preference + " from users where id = " + str(userId)
	cur.execute(query)
	preference = cur.fetchone()[0]
	
	if preference == 1:
		return True
	else:
		return False

def getFirstName(cur, userId):
    query = "select first_name from users where id = " +str(userId)
    cur.execute(query)
    first_name = cur.fetchone()[0]
    return first_name

def saveGender(cur, db, userId, gender):
    query = "update users set gender = '" + gender + "' where id = "+ str(userId)
    cur.execute(query)    
    pass

def saveAge(cur, db, userId, age):
    query = "update users set age = '" + age + "' where id = "+ str(userId)
    cur.execute(query)
    db.commit()
    pass

def saveCountry(cur, db, userId, country):
    query = "update users set country = '" + country + "' where id = "+ str(userId)
    cur.execute(query)    
    db.commit()    
    pass

def saveMuseumPreference(cur, db, userId, preference):
    query = "update users set museum_preference = '" + str(preference) + "' where id = "+ str(userId)
    cur.execute(query)    
    db.commit()    
    pass

def saveDaysStaying(cur, db, userId, days):
    query = "update users set stay_days = '" + str(days) + "' where id = "+ str(userId)
    cur.execute(query)    
    db.commit()    
    pass

def incrementCurrentStep(cur, db, userId):
    query = "update users set current_step = current_step + 1 where id =" + str(userId)
    cur.execute(query)
    db.commit()
    pass

def returnCurrentStep(cur, userId):
    query = "select current_step from users where id = " + str(userId)
    cur.execute(query)
    currentStep = cur.fetchone()[0]
    return currentStep

def setLastCurrentStep(cur, db, userId):
    query = "update users set current_step = 7 where id =" + str(userId)
    cur.execute(query)
    db.commit()

def getAttractionTitle(cur, attractionId):
	query = "select TitleEN from attractions where BINARY Trcid ='" + str(attractionId)+"'"
	cur.execute(query)
	title = cur.fetchone()[0]
	return title

def getAttractionShortDescription(cur, attractionId):
	query = "select ShortdescriptionEN from attractions where Trcid ='" + str(attractionId)+"'"
	cur.execute(query)
	description = cur.fetchone()[0]
	return description
	
def getAttractionWebsites(cur, attractionId):
	query = "select Urls from attractions where Trcid ='" + str(attractionId)+"'"
	cur.execute(query)
	urls = cur.fetchone()[0]
	return urls

def getAttractionType(cur, attractionId):
	query = "select Types from attractions where Trcid = '" + str(attractionId) + "'"
	cur.execute(query)
	type = cur.fetchone()[0]
	return type

def getRandomAttractionId(cur):
	query = "SELECT Trcid FROM attractions ORDER BY RAND() LIMIT 0,1;"
	cur.execute(query)
	attractionID = cur.fetchone()[0]
	return attractionID


def main():
    
    # Telegram Bot Authorization Token
    #bot = telegram.Bot('178800175:AAF0skUmAYjSI60CezycyVcrm9QKSJFz7Bk')
    
    # Telegram Bot Authorization Token (@DamskoBot (IamsterdamBot))
    bot = telegram.Bot('179472698:AAFBLff6TGp6tHb69zDeG8AtFG8dhaUrdm0')

    # Get database handler
    db, cur = returnDBCursor()
       
    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None


    while True:
        
        try:
            update_id = echo(bot, update_id, db, cur)
            
        except telegram.TelegramError as e:
            # These are network problems with Telegram.
            if e.message in ("Bad Gateway", "Timed out"):
                sleep(1)
            elif e.message == "Unauthorized":
                # The user has removed or blocked the bot.
                update_id += 1
            else:
                raise e
        except URLError as e:
            # These are network problems on our end.
 	         sleep(1)


def echo(bot, update_id, db, cur):
    # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        
        user_id = update.message.chat.id
        message = update.message.text

        #removes emoticons (Watson doesn't like them)
        message = message.encode('ascii', 'ignore').decode('ascii')
		
        keyboard = None
        responseMessage = ""
        
        if message != "":
        	keyboard, responseMessage = generateResponse(cur, db,  user_id, message, update.message.chat)
        else:
			keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
			responseMessage = "I really like your emoticon or sticker!"
        	
    	print "received message: " + message
        print "response: " + responseMessage

        if responseMessage:
            # Reply to the message
            bot.sendMessage(chat_id=chat_id,
                            text = responseMessage,
                            reply_markup=keyboard)
            
    return update_id

#generates keyboards
def keyboardmake(keyboardlist,resize=1,once=1,selective=''):
 if(resize==1):
  options="\"resize_keyboard\":true"
 else:
  options="\"resize_keyboard\":false"
 if(once==1):
  options=options+","+"\"one_time_keyboard\":true"
 else:
  options=options+","+"\"one_time_keyboard\":false"
 if(selective==1):
  options=options+","+"\"selective\":1"
 if(selective==2):
  options=options+","+"\"selective\":2"
 return("{\"keyboard\":"+json.dumps(keyboardlist).replace('"', '\"')+","+options+"}")

	

def generateResponse(cur, db, user_id, message, update):
	if checkId(cur, user_id):
  		userProfileStep = returnCurrentStep(cur, user_id)
  		print 'current step = ' + str(userProfileStep) 
  		
  		if userProfileStep < 7:
   			keyboard, response = introductionConversation(cur, db, user_id, message, userProfileStep)
  		else:
   			keyboard, response = regularConversation(cur, db, user_id, message)
 	else:
  		insertNewUser(db, cur, user_id, update)
  		keyboard = None
  		response = ""
  		keyboard, response = introductionConversation(cur, db, user_id, message, 0)
 
	return keyboard, response
  
def introductionConversation(cur, db, user_id, message, userProfileStep):
	keyboard = None
	response = ""
	 
	if userProfileStep == 0:
		response = "Hi there, can I ask you some questions about yourself?"
		keyboard = keyboardmake([["Yes", "No"]])
		incrementCurrentStep(cur, db, user_id)
		return keyboard, response
	  
	elif userProfileStep == 1:
		if message == "Yes":
			response = "What is your gender?"
			keyboard = keyboardmake([["I'm a MALE", "I'm a FEMALE"]])
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response
		elif message == "No":
			response = "Don't worry, I can still answer your questions about Amsterdam! I can't give you personalized suggestions however."
			keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
			setLastCurrentStep(cur, db, user_id)
			return keyboard, response
		else:
			response = "Can I ask you some questions first? Please click yes or no."
			keyboard = keyboardmake([["Yes", "No"]])
			return keyboard, response

	elif userProfileStep == 2:
		if message == "I'm a MALE":
			saveGender(cur, db, user_id, "male")
			response = "To what age category do you belong?"
			keyboard = keyboardmake([["<18", "18-24"], ["25-34", "35-44"], ["45-54", "55-64"], [">64"]])
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response	
		elif message == "I'm a FEMALE":
			saveGender(cur, db, user_id, "female")
			response = "To what age category do you belong?"
			keyboard = keyboardmake([["<18", "18-24"], ["25-34", "35-44"], ["45-54", "55-64"], [">64"]])
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response
		else:
			response = "Please select your gender:"
			keyboard = keyboardmake([["I'm a MALE", "I'm a FEMALE"]])
			return keyboard, response
	  	
	elif userProfileStep == 3:
		if stringIsAgeCategory(message):
			saveAge(cur, db, user_id, message)
			response = "And what is your country of residence?"
			keyboard = None
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response
		else:
			response = "How old are you? Please select one of the categories:"
			keyboard = keyboardmake([["<18", "18-24"], ["25-34", "35-44"], ["45-54", "55-64"], [">64"]])
			return keyboard, response

	elif userProfileStep == 4:
		saveCountry(cur, db, user_id, message)
		response = "Do you like to visit a museum during your stay?"
		keyboard = keyboardmake([["Yes", "No"]])
		incrementCurrentStep(cur, db, user_id)
		return keyboard, response
	  
	elif userProfileStep == 5:
		if message == "Yes" or message == "yes":
			saveMuseumPreference(cur, db, user_id, 1)
			response = "Finally, how many days are you staying?"
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response
		
		elif message == "No" or message == "no":
			saveMuseumPreference(cur, db, user_id, 0)
			response = "Finally, how many days are you staying?"
			incrementCurrentStep(cur, db, user_id)
			return keyboard, response
		else:
			response = "Museums, yes or no?"
			keyboard = keyboardmake([["Yes", "No"]])
			return keyboard, response
		

	elif userProfileStep == 6:
		try:
			message = int(message)
			saveDaysStaying(cur, db, user_id, message)
			incrementCurrentStep(cur, db, user_id)
			keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
			response = "Awesome, how can I help?"
			return keyboard, response
		except ValueError:
			response = "Please fill in a number, how many days are you staying?"
			keyboard = None
			return keyboard, response
			
		


def stringIsAgeCategory(ageCategory):
	if ageCategory == "<18" or ageCategory == "18-24" or ageCategory == "25-34" or ageCategory == "35-44" or ageCategory == "45-54" or ageCategory == "55-64" or ageCategory == "65+":
		return True
	else:
		return False

def regularConversation(cur, db, user_id, message):
	
	keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
	response = "Awesome, how can I help?"
	
	if message == "What is a fun thing to do in Amsterdam?":
		id = getRandomAttractionId(cur)
		
		while checkUserAttractionTypeMatch(cur, user_id, id) == False:
			id = getRandomAttractionId(cur)
		
		title = getAttractionTitle(cur, id)
		description = getAttractionShortDescription(cur, id)
		websites = getAttractionWebsites(cur, id)
		
		response = title + ": " + description
		
		if websites != "":
			response = response + " For more info visit: " + websites
		
	
	elif message == "I have another question about Amsterdam!":
		response = "Sure, ask your question!"
		keyboard = None
	
	elif message == "/start":
		response = "Welcome back " + getFirstName(cur, user_id)  + ". How can I help?"
	
	elif message == "/deleteme":
		deleteUser(db, cur, user_id)
		response = "Your account has been reset."
		keyboard = None
	
	else:
		answerTitle, answerText, answerConfidence = getAnswerDetails(message)
		
		if answerTitle != "" and answerConfidence > 20:
			response = answerText + " I am " + str(answerConfidence) + "% sure that this answers your question."
		else:
			response = "I'm sorry, I don't have an answer for you. Please try a different question."
	
	return keyboard, response

def checkUserAttractionTypeMatch(cur, user_id, attraction_id):
	attraction_type = getAttractionType(cur, attraction_id)
	museum_preference = userHasPreference(cur, user_id, "museum_preference")
	print attraction_type
	print str(museum_preference)
	
	if museum_preference == False and attraction_type == "Museum":
		return False
	else:
		return True
	
def getAnswerDetails(question):
	answerTitle = ""
	answerText = ""
	answerConfidence = 0
	
	url = 'https://dal09-gateway.watsonplatform.net/instance/568/deepqa/v1/question'
	data = {
                "question" : {
                  "questionText" : question
                    }
            }
	headers = {'content-type': 'application/json', 'Accept':' application/json', 'Cache-Control':'no-cache', 'X-SyncTimeout':'30'}
	r = requests.post(url, data=json.dumps(data), headers=headers, auth=HTTPBasicAuth('vua_student9', 'Spx1fkVd'))
	
	
	if 'question' in r.json():
		if len(r.json()['question']['evidencelist'][0]) != 0:
			answerTitle = r.json()['question']['evidencelist'][0]['title']
			answerText = r.json()['question']['evidencelist'][0]['text']
			answerConfidence = r.json()['question']['evidencelist'][0]['value']
			answerConfidence = int(float(answerConfidence)*100)
	

	return answerTitle, answerText, answerConfidence
    
def getRandomQuestion():
	questions = ('What is the biggest lake of Amsterdam?', 'How do I rent a bike in Amsterdam?', 'Whats a fun way to go around the city?', 'Can you swim in the canals?', 'Is there a zoo in Amsterdam?', 'Where can I find cheese markets outside of Amsterdam?', 'What are the busy months of the Rijksmuseum?', 'Can I park my car in the city centre?', 'What is the largest park of Amsterdam?', 'When is a good time to enjoy festivals?', 'Where can I see the Amsterdam letters?', 'What can I see at the city archives?', 'What to do in Amsterdam for free', 'Where can I buy cheap concert, or theatre tickets?', 'What are some vintage shops in Amsterdam?', 'Where can I get a short-stay apartment?', 'How to get to Amsterdam Noord?', 'Does Amsterdam have a beach?', 'What are the traditional Dutch foods during...', 'What is the largest shopping area?')
	
	randomNumber = random.randrange(0, len(questions)-1, 1)
	
	return questions[randomNumber]

if __name__ == '__main__':
    main()