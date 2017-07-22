# FMIPv2.py
# Query for data about iDevices related to an Apple ID, then display it. Requires authentication.

import datetime, time, getpass, fmiplib
from termcolor import colored, cprint

# Variables
username = ""
password = ""
device_dict = {}

def main():
    username = raw_input("Username: ")
    password = getpass.getpass() # Unix-style password gathering (no display on screen)
    device_dict = fmiplib.get_devices(username, password)
    print "-------------------------------------------------------" # Formatting
    # Python kindly type-juggles everything in the device_dict when it's converted from a JSON payload to a native Python dictionary by requests in fmiplib.py, so we use the %s string substitution method for implicit casting to strings instead of having to call str() all the time
    for i in range(0, len(device_dict)):
        # List out the device info
        current_device = device_dict[i]
        print "Device %s: %s " % (i, current_device["name"])
        print "Model: %s" % current_device["deviceDisplayName"]
        if current_device["batteryStatus"] == "Unknown": # If this isn't Charging or NotCharging, then the device is probably offline
        #print str(current_device) # For debugging
            try:
                print "Coordinates: %s, %s" % (current_device["location"]["latitude"], current_device["location"]["longitude"])
                print "Address: %s" % fmiplib.get_address_from_coords(current_device["location"]["latitude"], current_device["location"]["longitude"])
                # Time calculations
                time_stamp = current_device["location"]["timeStamp"]
                print "Located at: %s" % fmiplib.convert_time(time_stamp)
            except TypeError as e:
                cprint("Looks like we couldn't get a GPS lock.", "red")
                cprint("Debug info for nerds: " + str(e), "cyan")
            # If anything else goes wrong just let it crash
            print "Battery level: %s" % int(float(current_device["batteryLevel"] * 100))
            print "Battery status: %s" % current_device["batteryStatus"]
        else:
            cprint("This device is probably offline.")
        print "-------------------------------------------------------" # More formatting

    # Playing sounds
    playSound = raw_input("Do you want to play a sound on a device? [y/n]")
    if playSound.lower() == "yes" or playSound.lower() == "y":
        cprint("Warning! This will send the user an email.", "yellow")
        proceed = raw_input("Are you sure you want to proceed? [y/n]")
        if proceed.lower() == "yes" or proceed.lower() == "y":
            device = 0
            while device != "exit":
                device = input("Which device do you want to play a sound on? " + str(range(0, len(device_dict)))
                if device_dict[device] != None:
                    message = raw_input("Enter a message to display on the device: ")
                    fmiplib.play_sound(device_dict[device][1]), base64.b64encode("%s:%s" % (username, password)), message)
                else:
                    cprint("Device number not found in dictionary.", "red")
    else:
        cprint("Exiting...", "cyan")

if __name__ == "__main__":
    main()
