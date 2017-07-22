# Changes: we use requests over urllib2 and termcolor over ANSI color escape sequences
import base64, requests, json
from termcolor import colored, cprint

# parse_http_error(status_code)
# Better than crashing, and at least twice as pretty. Only covers the most likely error codes to receive.
# status_code: an int which represents the code you want to parse
# returns: some colored text with some information about what went down
def parse_http_error(status_code): 
    # 40X
    if status_code == 400:
        return colored("400 Bad Request. Check your sine-tacks.", "red")
    elif status_code == 401:
        return colored("401 Unauthorised. Try to spell your password correctly.", "red")
    elif status_code == 402:
        return colored("402 Payment Required. Did you exceed Google API usage?", "red")
    elif status_code == 403:
        return colored("403 Forbidden. No peeking.", "red")
    elif status_code == 404:
        return colored("404 Not Found. The service you're using might be down.", "red")
    elif status_code == 405:
        return colored("405 Method Not Allowed. Consult your nearest Python programmer for immediate bugfixing.", "red")
    elif status_code == 418:
        return colored("418 I'm A Teapot. The server you've sent a request to is actually a teapot.", "red")
    # 50X
    elif status_code == 500:
        return colored("500 Internal Server Error. You're fine, the server messed up.", "red")
    elif status_code == 502:
        return colored("502 Bad Gateway. Broken proxy server in connection chain.", "red")
    elif status_code == 503:
        return colored("503 Service Unavailable. Someone's being DDoSed. :P", "red")

#decide_type(user_id)
# Decides what kind of Apple authentication the user is using.
# user_id: whatever the user ID is
# returns: either "Forever" for an Apple FMIP token or "UserIDGuest" for anything else
def decide_type(user_id): # DRY
    try:
        int(user_id)
        return "Forever"
    except ValueError:
        return "UserIDGuest"

# get_devices(username, password)
# Used to both authenticate the user to Apple services and pull all of their device data.
# username: the user's Apple ID email address OR an Apple FMID token (whatever that is)
# password: the user's Apple ID password (regardless of username type, I assume)
# returns: a dictionary containing the device data, or an empty dictionary + an error message
def get_devices(username, password):
    auth_type = decide_type(username)

    url = "https://fmipmobile.icloud.com/fmipservice/device/%s/initClient" % username
    headers = { # Just some request headers required to make the request look legit
        "X-Apple-Realm-Support": "1.0", # Version?
        "Authorization": "Basic %s" % base64.b64encode("%s:%s" % (username, password)), # Actual auth
        "X-Apple-Find-API-Ver": "3.0", # Another version?
        "X-Apple-AuthScheme": "%s" % auth_type, # Auth type, obviously
        "User-Agent": "FindMyiPhone/500 CFNetwork/758.4.3 Darwin/15.5.0" # I think this makes it look like it's coming from a Mac
    } # Honestly I'm mostly just guessing at what these headers mean

    try: # Make the request
        r = requests.post(url, headers=headers)
        r.raise_for_status()
        cprint("Successfully got device data.", "green")
        return r.json()["content"] # Success, return the device dictionary
    except requests.exceptions.HTTPError: # Catch HTTP errors
        print parse_http_error(r.status_code) # If there is one, quip, then die
        return {}

# play_sound(dev_id, token, msg)
# Used to play a sound on an Apple device and display a message on the screen. Also sends the user an email at their Apple ID email, so be careful!
# dev_id: the device id assigned by Apple, found in a device dictionary
# token: used to authenticate to the API
# msg: the message to be displayed on the phone
# returns: a dictionary, containing either information about the device a sound was played on, or nothing if the attempt failed
def play_sound(dev_id, token, msg="Find My iPhone Alert"):
    dsid = base64.b64decode(token).split(":")[0]
    auth_type = decide_type(dsid)

    url = "https://fmipmobile.icloud.com/fmipservice/device/%s/playSound" % dsid
    headers = {
        "Accept": "*/*",
        "Authorization": "Basic %s" % token,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language":"en-us",
        "Content-Type":"application/json; charset=utf-8",
        "X-Apple-AuthScheme": auth_type
    }
    data = {
        "device": dev_id,
        "subject": msg
    }
    data = json.dumps(data) # Encode before you send
    try:
        r = requests.post(url, data=data, headers=headers)
        r.raise_for_status()
        cprint("Successfully played noise on " + r.json()[0]) # CHANGE THIS TO THE DEVICE NAME
        return r.json()
    except requests.exceptions.HTTPError:
        print parse_http_error(r.status_code)
        return {}

# get_address_from_coords(lat, lon)
# Uses the Google Geocoding API to convert a set of coordinates to an address. Usually accurate to the street level.
# lat, lon: the coordinates to geocode
# returns: a string containing the address returned, prettified, or an error message
def get_address_from_coords(lat, lon):
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s" % (lat, lon)
    try:
        r = requests.get(url)
        r.raise_for_status() # Crash and handle later if you error out
        googleJson = r.json()
        formatted_address = googleJson["results"][0]["formatted_address"]
    except requests.exceptions.HTTPError: # If the request fails, then
        print parse_http_error(r.status_code) # returns a colored(), so just print
    except ValueError:
        cprint("Couldn't deserialize JSON data.", "red")

    return formatted_address

# convert_time(time_stamp)
# Converts the time provided by Find My iPhone to a human-readable format
# time_stamp: The timestamp provided by Find My iPhone
# returns: A string containing the formatted time
def convert_time(time_stamp):
    time_stamp = time_stamp / 1000
    time_now = time.time()
    time_delta = time_now - time_stamp
    minutes, seconds = divmod(time_delta, 60)
    hours, minutes = divmod(minutes, 60)
    time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%A, %B %d at %I:%H:%S")
    if hours > 0:
        return "%s (%sh %sm %ss ago)" % (time_stamp, str(hours).split(".")[0], str(minutes).split(".")[0], str(seconds).split(".")[0])
    else:
        return "%s (%sm %ss ago)" % (time_stamp, str(minutes).split(".")[0], str(seconds).split(".")[0])

# Write code here to test your new functions. Don't push commits with your credentials in them.
