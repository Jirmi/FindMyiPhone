import fmiplib, getpass
from termcolor import cprint

# Vars
username = ""
password = ""
device_dict = {}

def main():
    username = raw_input("Username: ")
    password = getpass.getpass()
    device_dict = fmiplib.get_devices(username, password)
    for i in range(0, len(device_dict)):
        print "Device %s: %s" % (i, device_dict[i]["name"])

    dev_index = input("Enter the number of the device you wish to track: ")
    if dev_index in range(0, len(device_dict)):
        # Main loop
        while True:
            device_dict = fmiplib.get_devices(username, password)
            tracked_device = device_dict[dev_index] # Save bytes. This is code golf now
            print "%s is located at: %s. Data sent at %s." % (tracked_device["name"], fmiplib.get_address_from_coords(tracked_device["location"]["latitude"], tracked_device["location"]["longitude"]), fmiplib.convert_time(tracked_device["location"]["timeStamp"]))
    else:
        cprint("Device not found.", "red")
