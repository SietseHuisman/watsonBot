import logging
import telegram
from time import sleep
import pycurl, json, requests
from requests.auth import HTTPBasicAuth
from decimal import Decimal
import re
import urllib
import json 

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

   
    

def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
       return not bool(search(strg))

def main():
    
    # Telegram Bot Authorization Token (@FritsBot (MirrorBot))
    bot = telegram.Bot('128563933:AAHFw_m88dS_zloaSXQ0JOgj5myGgEvMQPI')

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
       	user_id = update.message.chat.id
        
        if userHasProfilePicture(bot, user_id):
        	profilepicture_file_id = getProfilePictureFileID(bot, user_id)
        	profilepicture_url =  bot.getFile(profilepicture_file_id).file_path
       		face_object = analyzeFace(profilepicture_url)
       		
       		if faceRecognized(face_object):
       			age_range = getAgeRange(face_object)
       			gender = getGender(face_object)
       		
       			responseMessage = "I think you are a "  + gender.lower() + " between the ages of " + age_range + "."
       		else:
       			responseMessage = "My analysis didn't work on your profile picture. Please try a different one."
       	else:
       		responseMessage = "Please insert a profile picture!"
        
        
        message = update.message.text
        
        print "received message: " + message
        print "response: " + responseMessage

        if message:
            # Reply to the message
            bot.sendMessage(chat_id=chat_id,
                            text = responseMessage)
            
    return update_id

def faceRecognized(face_object):
	if len(face_object['imageFaces']) != 0:
		return True
	else: 
		return False

def getAgeRange(face_object):
	if faceRecognized(face_object):
		age_range = face_object['imageFaces'][0]['age']['ageRange']
		return str(age_range)
	else:
		return "unknown"

def getGender(face_object):
	if faceRecognized(face_object):
		gender = face_object['imageFaces'][0]['gender']['gender']
		return str(gender)
	else:
		return "unknown"


def analyzeFace(photo_url):
#returns information about a face in a json object, including the age, gender and race of a given picture URL.
	
	print "Photo URL: " + photo_url
	
	#first we encode the URL, turning slashes (/) into %2f etc
	encoded_url = urllib.quote(photo_url, safe='')
	
	
	#IBM Alchemy Server:
	face_detect_api_url = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedImageFaceTags?url=" + encoded_url + "&apikey=95f6961a0f30623949a3bbe81010cfae7ee4329d&outputMode=json"
	
	
	r = urlopen(face_detect_api_url)
	data = str(r.read())
	face_info = json.loads(data)
	
	return face_info 
	

def getProfilePictureFileID(bot, user_id):
#returns the file_id of the first (and biggest) profile picture for a given user
	
	user_profile_photos = bot.getUserProfilePhotos(user_id)
	for i in user_profile_photos.photos[0]:
		file_id = i.file_id
	
	return file_id

def userHasProfilePicture(bot, user_id):
#returns true when the user has a profile picture
	
	user_profile_photos = bot.getUserProfilePhotos(user_id)
	total_user_profile_photos = user_profile_photos['total_count']
	
	if total_user_profile_photos > 0:
		return True
	else:
		return False


if __name__ == '__main__':
	main()