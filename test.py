from PySmartlink import *


smartlink = Smartlink('192.168.1.64')

if smartlink.is_up():
    print(" [+] Smartlink is up")
else:
    print(" [-] Smartlink is not up")
    exit(0)

if smartlink.login() == SmartlinkResponse.success:
    print(" [+] Login is ok")
else:
    print(" [-] Login is not ok")
    exit(0)

time.sleep(2)

if smartlink.change_name('SM-B2EI-2') == SmartlinkResponse.success:
    print(" [+] Change name is ok")
else:
    print(" [-] Change name is not ok")

time.sleep(2)

devices = smartlink.get_device()
if devices != SmartlinkResponse.error:
    print(" [+] Registered device: ")
    for device in devices:
        print(device.to_string("\t"))
else:
    print(" [-] Can't get registered device")
time.sleep(2)


print(" [+] Starting device discovering for device from %s to %s" % (11, 20))
discovered_devices = smartlink.discover(11, 20, lambda completion: print("\tCompletion: %s%%" % completion))
if discovered_devices != SmartlinkResponse.error:
    print(" [+] Device discovered: ")
    for device in discovered_devices:
        print(device.to_string("\t"))
else:
    print(" [-] Error during device discovering")

time.sleep(2)

data = smartlink.identification()
if data == SmartlinkResponse.error:
    print(" [-] Can't get device identification")
else:
    print(" [+] Device identification: ")
    for key, value in data.items():
        print("\t%s: %s" % (key, value))

time.sleep(2)

response = smartlink.add_way(0, 3, 'test', 'test', SmartlinkEquipments.OFSD24, SmartlinkUsages.Lighting)
if response == SmartlinkResponse.success:
    print(" [+] New way added")
elif response == SmartlinkResponse.conflict:
    print(" [+] New way create conflict with an other way")
else:
    print(" [-] Can\'t add new way")

time.sleep(2)

if smartlink.logout() == SmartlinkResponse.success:
    print(" [+] Logout is ok")
else:
    print(" [-] Logout is not ok")
    exit(0)
