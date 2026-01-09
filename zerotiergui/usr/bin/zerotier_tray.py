import os
import sys
import subprocess
from PIL import Image
import pystray
from pystray import MenuItem, Icon, Menu
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

def create_image(width, height):
    return Image.open("/usr/share/icons/hicolor/ZT-Icon.png")#"/usr/share/icons/hicolor/ZT-Icon.png"

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


def prompt_for_network_id():
    network_id = simpledialog.askstring("Input", "Enter the Network ID:")
    return network_id

def get_networks():
    process = subprocess.Popen(['pkexec', 'sudo', 'zerotier-cli', 'listnetworks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode('utf-8').split("\n")
    error = stderr.decode('utf-8')
    aux_out = output[0].split(" ")
    networks = []
    if aux_out[0] == "200":
        for line in output[1:]:
            networks.append(line) 
    #line> '200', 'listnetworks', '<nwid>', '<name>', '<mac>', '<status>', '<type>', '<dev>', '<ZT', 'assigned', 'ips>

    return networks


def show_networks():
    networks = get_networks()
    if networks:
        #Create a new window for the network table
        table_window = tk.Tk()
        table_window.title("Available Networks")
    
        # Create a Treeview widget for displaying network information
        tree = ttk.Treeview(table_window, columns=("ID", "Name", "Status", "IP"), show='headings')
        tree.heading("ID", text="Network ID")
        tree.heading("Name", text="Network Name")
        tree.heading("Status", text="Status")
        tree.heading("IP", text="IP")
    
        # Insert network data into the Treeview
        for network in networks:
            aux_net= network.split(" ")
            if len(aux_net) >= 9:
                tree.insert("", "end", values=(aux_net[2], aux_net[3], aux_net[5], aux_net[8]))  # Assuming columns are Network ID, Name, Status
    
        tree.pack(padx=10, pady=10)


        def copy_to_clipboard():
            selected_item = tree.selection()
            if selected_item:
                item_text = tree.item(selected_item)["values"][0]
                table_window.clipboard_clear()  # Clear the clipboard
                table_window.clipboard_append(item_text)  # Append the selected text to clipboard
                messagebox.showinfo("", f"Copied ID: {item_text}")
            else:
                messagebox.showwarning("Selection Error", "No item selected!")


        # Create Copy Button
        copy_button = tk.Button(table_window, text="Copy to Clipboard", command=copy_to_clipboard)
        copy_button.pack()

        # Add a button to close the window
        close_button = tk.Button(table_window, text="Close", command=table_window.destroy)
        close_button.pack(pady=(0, 10))
        

        table_window.mainloop()
    else:
        icon.notify("Failed to retrieve networks", "ZeroTier Error!.")
        #messagebox.showinfo("Available Networks", "No networks found.")

def join_network():
    network_id =prompt_for_network_id()
    if network_id:
        process = subprocess.Popen(['pkexec', 'sudo', 'zerotier-cli', 'join', network_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode('utf-8')
        error = stderr.decode('utf-8')
        messagebox.showinfo("", f"{output}")

def leave_network():
    network_id =prompt_for_network_id()
    if network_id:
        process = subprocess.Popen(['pkexec', 'sudo', 'zerotier-cli', 'leave', network_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode('utf-8')
        error = stderr.decode('utf-8')
        messagebox.showinfo("", f"{output}")



separator = MenuItem('────────────', lambda x: None, enabled=False)

icon = Icon("ZeroTier")
icon.icon = create_image(64, 64)
icon.title = "ZeroTier Control"
icon.menu = pystray.Menu(
    MenuItem("Join Network", join_network),
    MenuItem("Leave Network", leave_network),
    MenuItem("Show Networks", show_networks),
    separator,
    MenuItem("Start", start_service),
    MenuItem("Stop", stop_service),
    separator,
    MenuItem("Status", show_status),
    separator,
    MenuItem("Quit", on_quit)
)

icon.run(setup)

