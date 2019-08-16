# Import the requests library to send http request to coinbase.com
import requests

# Import json library for reading json data returned by the http request
import json 

# Import the configparser library used for reading and writing to let_there_be_light.ini 
import configparser

# Import some funtions from TkInter
from tkinter import *
import tkinter.font
import tkinter.ttk

# Import some functions from Pillow
from PIL import ImageTk, Image

# Import the PyQRCode library
import pyqrcode

# Imports some Python Date/Time functions
import time
import datetime

# Imports the PyOTA library
from iota import Iota
from iota import Address

# Define the Exit function
def exitGUI():

    root.destroy()


# Seed used for generating addresses and collecting funds.
# IMPORTANT!!! Replace with your own seed
MySeed = b"WRITE9YOUR9OWN9SEED9HERE9....................."


# URL to IOTA fullnode used when checking balance
iotaNode = "https://nodes.thetangle.org:443"

# Create an IOTA object
api = Iota(iotaNode, MySeed)

# Define main form as root 
root = Tk()

# Set the form background to white
root.config(background="white")

# TkInter font to be used in GUI
myFont = tkinter.font.Font(family = 'Helvetica', size = 12, weight = "bold")

# Set main form to full screen
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.focus_set()  # <-- move focus to this widget
root.bind("<Escape>", lambda e: e.widget.quit())


# Define mainFrame
mainFrame = tkinter.Frame(root)
mainFrame.config(background="white")
mainFrame.place(relx=0.5, rely=0.5, anchor=CENTER)


# Create and render the QR code
qrframe = tkinter.Frame(mainFrame)
qrframe.grid(row=0,column=0,rowspan=3)
code = pyqrcode.create('')
code_xbm = code.xbm(scale=3)
code_bmp = tkinter.BitmapImage(data=code_xbm)
code_bmp.config(background="white")
qrcode = tkinter.Label(qrframe, image=code_bmp, borderwidth = 0)
qrcode.grid(row=0, column=0)


# Create and render logo
# Make sure you download and place the "iota_logo75.jpg" file in the same folder as your python file.
# The logofile can be dowloaded from: https://github.com/huggre/pay_the_light_gui/blob/master/iota_logo75.jpg
path = "iota_logo75.jpg"
img = ImageTk.PhotoImage(Image.open(path))
iotalogo = tkinter.Label(mainFrame, image = img, borderwidth = 0)
iotalogo.grid(row=0,column=1)


# Create and render timer
timeText = tkinter.Label(mainFrame, text="", font=("Helvetica", 50))
timeText.config(background='white')
timeText.grid(row=1,column=1)


# Create and render Exit button
exitButton = Button(mainFrame, text='Exit', font=myFont, command=exitGUI, bg='white', height=1, width=10)
exitButton.grid(row=2,column=1)


# Create and render price text
priceTextFrame = tkinter.Frame(mainFrame)
priceTextFrame.grid(row=3,column=0,columnspan=2)
priceText = tkinter.Label(priceTextFrame, text="Here comes price", font=("Helvetica", 12))
priceText.config(background='white')
priceText.grid(row=3,column=0)


# Create and render progress bar
progFrame = tkinter.Frame(mainFrame)
progFrame.grid(row=4,column=0,columnspan=2)
mpb = tkinter.ttk.Progressbar(progFrame,orient ="horizontal",length = 435, mode ="determinate")
mpb.grid(row=4,column=0)
mpb["maximum"] = 30
mpb["value"] = 0


# Create and render payment status  text
paymentStatusFrame = tkinter.Frame(mainFrame)
paymentStatusFrame.grid(row=5,column=0,columnspan=2)
paymentStatusText = tkinter.Label(paymentStatusFrame, text="Waiting for new transactions", font=("Helvetica", 9))
paymentStatusText.config(background='white')
paymentStatusText.grid(row=5,column=0)


# Create and render light status text
statusTextFrame = tkinter.Frame(mainFrame)
statusTextFrame.grid(row=6,column=0,columnspan=2)
statusText = tkinter.Label(statusTextFrame, text="Light is OFF", font=("Helvetica", 9))
statusText.config(background='white')
statusText.grid(row=6,column=0)


# Define function to update QR code based on new address
def updateQRcode(QRaddr):
    code = pyqrcode.create(QRaddr)
    code_xbm = code.xbm(scale=3)
    code_bmp = tkinter.BitmapImage(data=code_xbm)
    code_bmp.config(background="white")
    qrcode.configure(image=code_bmp)
    qrcode.image = code_bmp


# Define function to replace QR code with hourglass icon
# Make sure you download and place the "hourglass.xbm" file in the same folder as your python file.
# The hourglass icon file can be dowloaded from: https://gist.github.com/huggre/c126863786991b49c2965d42b12f6b3d
def showXBM():
    xbm_img = tkinter.BitmapImage(file="hourglass.xbm")
    xbm_img.config(background="white")
    qrcode.configure(image=xbm_img)
    qrcode.image = xbm_img


# Define function to generate new IOTA address
def generateNewAddress(addrIndexCount):
    result = api.get_new_addresses(index=addrIndexCount, count=1, security_level=2)
    addresses = result['addresses']
    QRaddr=str(addresses[0].with_valid_checksum())
    updateQRcode(QRaddr)
    address = [addresses[0]]
    return(address)
    

# Define function for checking address balance on the IOTA tangle. 
def checkbalance(addr):
    gb_result = api.get_balances(addr)
    balance = gb_result['balances']
    return (balance[0])


# Define Function to displays payment status in GUI
def updatePaymentStatus(paymentStatus):
    paymentText="Payment Status: " + paymentStatus
    paymentStatusText.configure(text=paymentText)


# Define function to return light price in IOTA's based on market value on marketcap.com
def getLightPriceIOTA():
    r = requests.get('https://api.coinmarketcap.com/v1/ticker/iota/')
    for coin in r.json():
        fprice = float(coin["price_usd"])
        lightprice_IOTA = fprice * lightprice_USD
        return (lightprice_IOTA)


# Define function to display price in GUI
def displayprice():
    sprice = "PRICE: " + str(lightprice_USD) + " USD / " + str(round(getLightPriceIOTA(),3)) + " MIOTA pr. minute"
    priceText.configure(text=sprice)


# Define function to check for existing address transactions
def getTransExist(addr):
        result = api.find_transactions(addresses=addr)
        myhashes = result['hashes']
        if len(myhashes) > 0:
            transFound = True
        else:
            transFound = False
        return(transFound)

# Define function for reading and storing address indexes
# Make sure you download and place the "let_there_be_light.ini" file in the same folder as your python file.
# The let_there_be_light.ini file can be dowloaded from: https://gist.github.com/huggre/c5185df916ca00d2e1d12943a9d9d03a
def getNewIndex():
    config = configparser.ConfigParser()
    config.read('let_there_be_light.ini')
    oldIndex = config.getint('IndexCounter', 'addrIndexCount')
    newIndex = oldIndex +1
    config.set('IndexCounter', 'addrIndexCount', str(newIndex))
    with open('let_there_be_light.ini', 'w') as configfile:
        config.write(configfile)
    return(newIndex)


# Define some variables
lightbalance = 0
balcheckcount = 0
lightstatus = False
addrfound = False
transFound = False

# The price of the service in USD pr. minute. Change at will
lightprice_USD = 0.01

# Function that returns next index used by the generateNewAddress function
addrIndex = getNewIndex()

# Generate new payment address
addr = generateNewAddress(addrIndex)

# Display price in GUI
displayprice()

# Display payment status in GUI
updatePaymentStatus("Waiting for new transactions")

# Main loop that executes every 1 second
def maintask(balcheckcount, lightbalance, lightstatus, transFound, addr, addrIndex):


    # Check for new funds and add to lightbalance when found.
    if balcheckcount == 30:

        # Check if address has any transactions   
        if transFound == False:
            transFound = getTransExist(addr)
            if transFound == True:
                showXBM()
                updatePaymentStatus("New transaction found, please wait while transaction is confirmed")

        # If new transactions has been found, check for positive balance and add to lightbalance
        if transFound == True:
            balance = checkbalance(addr)
            if int(balance) > 0:
                lightbalance = lightbalance + int(((balance/1000000) * 60) / (getLightPriceIOTA()))
                addrIndex = getNewIndex()
                addr = generateNewAddress(addrIndex)
                updatePaymentStatus("Waiting for new transactions")
                transFound = False

        balcheckcount = 0

    # Manage light balance and light ON/OFF
    if lightbalance > 0:
        if lightstatus == False:
            statusText.config(text="Light is ON")
            lightstatus=True
        lightbalance = lightbalance -1       
    else:
        if lightstatus == True:
            statusText.config(text="Light is OFF")
            lightstatus=False

    # Print remaining light balance     
    strlightbalance = datetime.timedelta(seconds=lightbalance)
    timeText.config(text=strlightbalance)


    # Increase balance check counter
    balcheckcount = balcheckcount +1


    # Update progress bar
    mpb["value"] = balcheckcount


    # Run maintask function after 1 sec.
    root.after(1000, maintask, balcheckcount, lightbalance, lightstatus, transFound, addr, addrIndex)


# Run maintask function after 1 sec.
root.after(1000, maintask, balcheckcount, lightbalance, lightstatus, transFound, addr, addrIndex)


root.mainloop()