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

def insertNewUser(db, cur, userId):
    query = "insert into users (id, current_step) values (" + str(user_id) + ", 1)"
    cur.execute(query)
    db.commit()

def getArtPreference(cur, userId):
    query = "select preference from users where id = " +str(userId)
    cur.execute(query)
    preference = cur.fetchone()[0]
    return preference

def updateCurrentStep(cur, db, userId):
    query = "update users set current_step = current_step + 1 where id =" + str(userId)
    cur.execute(query)
    pass

def returnCurrentStep(cur, userId):
    query = "select current_step from users where id = " + str(userId)
    cur.execute(query)
    currentStep = cur.fetchone()[0]
    return currentStep

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

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    

    while True:
        
        try:
            update_id = echo(bot, update_id)
        
        
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


def echo(bot, update_id):
    # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text
        print "received message: " + message
        responseMessage = getAnswer(message)
        print "response: " + responseMessage

        if message:
            # Reply to the message
            bot.sendMessage(chat_id=chat_id,
                            text = responseMessage)
            
    return update_id


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
