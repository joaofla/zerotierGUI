import os
import sys
import subprocess
from PIL import Image
import pystray
from pystray import MenuItem, Icon

def create_image(width, height):
    return Image.open("/usr/share/icons/hicolor/ZT-Icon.png")

def start_service(icon, item):
    subprocess.run(['systemctl', 'start', 'zerotier-one'])
    icon.update_menu()

def stop_service(icon, item):
    subprocess.run(['systemctl', 'stop', 'zerotier-one'])
    icon.update_menu()

def on_quit(icon, item):
    icon.stop()

def setup(icon):
    icon.visible = True

def get_status():
    result = subprocess.run(['systemctl', 'is-active', 'zerotier-one'], capture_output=True, text=True)
    return result.stdout.strip()  # Returns 'active' or 'inactive'
    
def get_status_info():
    process = subprocess.Popen(['pkexec', 'sudo', 'zerotier-cli', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    info = stdout.decode('utf-8').split(' ')
    error = stderr.decode('utf-8')
    return info  # Returns machine ID and other info

def show_status(icon, item):
    status = get_status()
    if status == "active":
        info = get_status_info()
        icon.notify("ZeroTier Status ONLINE, ID:" + info[2], "ZeroTier is running.")
    else:
        icon.notify("ZeroTier Status OFFLINE", "ZeroTier is not Running.")

# Missing:
# join or leave network
# show peers and networks

icon = Icon("ZeroTier")
icon.icon = create_image(64, 64)
icon.title = "ZeroTier Control"
icon.menu = pystray.Menu(
    MenuItem("Start ZeroTier", start_service),
    MenuItem("Stop ZeroTier", stop_service),
    MenuItem("Check Status", show_status),
    MenuItem("Quit", on_quit)
)

icon.run(setup)

