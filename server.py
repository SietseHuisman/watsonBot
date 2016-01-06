import telegram
from time import sleep
import json, requests
from requests.auth import HTTPBasicAuth
from decimal import Decimal
import MySQLdb

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2



def returnDBCursor(host = "localhost", user = "root", password = "" , db = "watsonbot"):
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
    query = "insert into users (id, first_name, last_name, current_step) values (" + str(userId) + ", '" + firstName + "', '" + lastName + "',0)"
    cur.execute(query)
    db.commit()

def getArtPreference(cur, userId):
    query = "select preference from users where id = " +str(userId)
    cur.execute(query)
    preference = cur.fetchone()[0]
    return preference

def saveGender(cur, db, userId, gender):
    query = "update users set gender = '" + gender + "' where id = "+ str(userId)
    cur.execute(query)    
    pass

def saveAge(cur, db, userId, age):
    query = "update users set age = '" + age + "' where id = "+ str(userId)
    cur.execute(query)    
    pass

def saveCountry(cur, db, userId, country):
    query = "update users set country = '" + country + "' where id = "+ str(userId)
    cur.execute(query)    
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
    query = "update users set current_step = 5 where id =" + str(userId)
    cur.execute(query)
    db.commit()

def main():
    
    # Telegram Bot Authorization Token
    bot = telegram.Bot('178800175:AAF0skUmAYjSI60CezycyVcrm9QKSJFz7Bk')

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
        
        keyboard = None
        responseMessage = ""
        print user_id 
        keyboard, responseMessage = generateResponse(cur, db,  user_id, message, update.message.chat)
        
        print "received message: " + message
        print "response: " + responseMessage

        if message:
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
  if userProfileStep < 6:
   keyboard, response = introductionConversation(cur, db, user_id, message, userProfileStep)
  else:
   keyboard, response = regularConversation(cur, user_id, messsage)
 else:
  insertNewUser(db, cur, user_id, update)
  keyboard = None
  response = "test"
 return keyboard, response
  
def introductionConversation(cur, db, user_id, message, userProfileStep):
 keyboard = None
 response = ""
 print userProfileStep
 if userProfileStep == 0:
  response = "Hi there, can I ask you some questions about yourself?"
  keyboard = keyboardmake([["Yes", "No"]])
  incrementCurrentStep(cur, db, user_id)
  
  return keyboard, response
  
 elif userProfileStep == 1:
  if message == "Yes":
   print 'the message is yes'
   response = "What is your gender?"
   keyboard = keyboardmake([["I'm a MALE", "I'm a FEMALE"]])
   incrementCurrentStep(cur, db, user_id)
   return keyboard, response
   
  elif message == "No":
   response = "Don't worry, I can still answer your questions about Amsterdam! I can't give your personalized suggestions."
   setLastProfileStep(cur, db, user_id)
   
   return keyboard, response

  else:
   reponse = "Please click yes or no."
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
   
  elif userProfileStep == 3:
    saveAge(cur, db, user_id, message)
    response = "What is your country of residence?"
    incrementCurrentStep(cur, db, user_id)
    
    return keyboard, response

  elif userProfileStep == 4:
    saveCountry(cur, db, user_id, message)
    response = "What kind of art do you like most?"
    keyboard = keyboardmake([["Modern", "Classic"]])
    incrementCurrentStep(cur, db, user_id)
    return keyboard, response

  elif userProfileStep == 5:
      saveArtPreference(user_id, message)
      incrementCurrentStep(cur, db, user_id)
      keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],["Random specific question"],["I have another question about Amsterdam!"]])
      response = "Awesome, how can I help?"
      return keyboard, response


def getAnswer(question):
    url = 'https://dal09-gateway.watsonplatform.net/instance/568/deepqa/v1/question'
    data = {
                "question" : {
                  "questionText" : question
                    }
            }
    headers = {'content-type': 'application/json', 'Accept':' application/json', 'Cache-Control':'no-cache', 'X-SyncTimeout':'30'}
    r = requests.post(url, data=json.dumps(data), headers=headers, auth=HTTPBasicAuth('vua_student9', 'Spx1fkVd'))
    
    #print Decimal(r.json()['question']['evidencelist'][0]['value']) < Decimal(0.6)
    #if Decimal(r.json()['question']['evidencelist'][0]['value']) < Decimal(0.6):
     #   return "I'm not sure, I'm sorry :("
    #else:
    return r.json()['question']['evidencelist'][0]['title'] + ", i am " + str(r.json()['question']['evidencelist'][0]['value']) + " out of 1 confident about this"  
    
    

if __name__ == '__main__':
    main()
