import telegram
import json
import random
from time import sleep

#test rogier

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

def main():
    
    # Telegram Bot Authorization Token
    #bot = telegram.Bot('178800175:AAF0skUmAYjSI60CezycyVcrm9QKSJFz7Bk')
    
    # Telegram Bot Authorization Token (@DamskoBot (IamsterdamBot))
    bot = telegram.Bot('168907006:AAH66rNTBg2Pj9gS9ZWvH708inJFPcTcwUU')
    
    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    counter = 0
    while counter < 4:
        print update_id
        print "counter: " + str(counter)
        try:
            
            for update in bot.getUpdates(offset=update_id, timeout=10):
                print "i just received the message: " + str(update.message.text) + ", and my counter = " + str(counter)
                user_id = update.message.chat.id
                if counter == 0:
                    print "sending message"
                    response = "Hi there, WOULD YOU LIKE TO PARTY TONIGHT????"
                    keyboard = keyboardmake([["YES", "nope"]])
                    bot.sendMessage(chat_id=user_id,
                        text = response,
                        reply_markup=keyboard)
                    counter +=1
                elif counter == 1:
                    print "sending second message"
                    if update.message.text == "YES":
                        response = "COOL! Do you like awesome clubs?"
                        keyboard = keyboardmake([["YES", "nope"]])
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                        counter +=1
                    elif update.message.text == "nope":
                        response = "fk u"
                        keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                        counter  = 0
                    else:
                        response = "Sorry, didnt catch that. Please use one of the two options below!"
                        keyboard = keyboardmake([["YES", "nope"]])                            
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                elif counter == 2:
                    if update.message.text == "YES":
                        response = "COOL! Then come to Paradiso tonight! Find more information and buy tickets at www.paradiso.nl"
                        keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                        counter =0
                    elif update.message.text == "nope":
                        response = "fk u"
                        keyboard = keyboardmake([["What is a fun thing to do in Amsterdam?"],[getRandomQuestion()],["I have another question about Amsterdam!"]])
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                        counter =0
                    else:
                        response = "Sorry, didnt catch that. Please use one of the two options below!"
                        keyboard = keyboardmake([["YES", "nope"]])                            
                        bot.sendMessage(chat_id=user_id,
                            text = response,
                            reply_markup=keyboard)
                    
                            
                        

                print update_id
                update_id = update.update_id +1
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


def getRandomQuestion():
	questions = ('What is the biggest lake of Amsterdam?', 'How do I rent a bike in Amsterdam?', 'Whats a fun way to go around the city?', 'Can you swim in the canals?', 'Is there a zoo in Amsterdam?', 'Where can I find cheese markets outside of Amsterdam?', 'What are the busy months of the Rijksmuseum?', 'Can I park my car in the city centre?', 'What is the largest park of Amsterdam?', 'When is a good time to enjoy festivals?', 'Where can I see the Amsterdam letters?', 'What can I see at the city archives?', 'What to do in Amsterdam for free', 'Where can I buy cheap concert, or theatre tickets?', 'What are some vintage shops in Amsterdam?', 'Where can I get a short-stay apartment?', 'How to get to Amsterdam Noord?', 'Does Amsterdam have a beach?', 'What are the traditional Dutch foods during...', 'What is the largest shopping area?')
	
	randomNumber = random.randrange(0, len(questions)-1, 1)
	
	return questions[randomNumber]

main()

