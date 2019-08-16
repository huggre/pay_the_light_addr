# Integrating physical devices with IOTA — Managing price and addresses

The 4th part in a series of beginner tutorials on integrating physical devices with the IOTA protocol.

![img](https://miro.medium.com/max/640/1*3z7eKcLh5ddpzj3JCgTXQA.jpeg)

## Introduction

This is the 4th part in a series of beginner tutorials on integrating physical devices with the IOTA protocol. In this tutorial we’ll be adding a couple of new features to our IOTA payment system. These features are related to how we manage the price of our service in a volatile IOTA market and how we deal with the IOTA one-time signature problem.

If you haven’t read the [first](https://medium.com/coinmonks/integrating-physical-devices-with-iota-83f4e00cc5bb) and the [third](https://medium.com/@hugogregersen/integrating-physical-devices-with-iota-83f4e00cc5bb) tutorial in this series, you should read them before continuing as they form the foundation for the project we are building on in this tutorial.

*Note!*
*This tutorial will be more software oriented compared to the previous tutorials in this series as we will not be adding any new hardware to our project.*

## The Use Case

Now that we have our LCD based user interface in place we should take a closer look at a couple of issues that was briefly touched upon in the [previous](https://medium.com/@hugogregersen/integrating-physical-devices-with-iota-83f4e00cc5bb) tutorial. Let’s start with the topic commonly referred to as *address reuse*.

**Address reuse**
Just to be clear, when i use the term “IOTA one-time signature problem”, i’m not referring to “problem” as in any error or bug in IOTA. The IOTA one-time signature scheme is a protection mechanism that was added to the IOTA protocol by design. Still, it’s something we need to be aware of, and deal with, when building applications on top of the IOTA protocol. As described in the previous tutorial “*as long as the hotel owner do not spend any funds from his refrigerator addresses they are completely safe, however, as soon as he spends any funds from one of the addresses, the address is no longer safe and must be replaced by a new IOTA payment address”.* What this actually means is that each time you spend funds from an IOTA address, a part of its private key is exposed, making it possible for a bad actor to forge it’s signature and steal it’s funds. So, how do we deal with this “problem”? We have to assume that the hotel owner wants to spend his hard earned IOTA’s at one point, right? Well, one option would be for him to just replace the old refrigerator payment address with a new address whenever he wants to spend from the old address. A better alternative might be to simply generate a new address for every payment so that we could ignore the address reuse problem all together. Now that we have our new LCD in place, we also have the practical means of implementing this solution.

**Price**
The second issue i want to discuss in this tutorial is how we manage the price of our refrigerator service with respect to the volatile IOTA market. Having a static IOTA price for our refrigerator service, say 1 MIOTA for 1 hour of service, might not be the best business model for our hotel owner. After all, the price he pays in USD for electricity and maintenance of his refrigerator service is pretty much static and decoupled from the day to day volatility of the IOTA market price. I think a more sustainable business model for our hotel owner would be to price his refrigerator service in USD, say 1 USD for 1 hour service, and instead convert the USD price to MIOTA at the beginning of each transaction. So how do we implement this feature? Again, our new LCD comes to the rescue. By using an API call to the popular coinmarketcap.com website we can lookup the current IOTA price in USD, convert our USD price to IOTA’s, and display the correct IOTA price on the LCD. Another issue that we need to take into account is that our price in USD also might change from time to time depending on external factors such as the price of electricity. So we have to make sure we have an easy method of updating the USD price, and at the same time make sure the guest get’s the time of service he paid for. This should all be possible with the use of some basic math.

*Note!*
*It should be noted that the new Trinity wallet already have a built in feature for converting fiat currency to IOTA. So in that sense it might be good enough to just display the refrigerator price in fiat currency, and have Trinity take care of the fiat to IOTA conversion.*

## The payment process

Next, lets see how a new payment process based on generating new addresses for each payment might look like.

![img](https://miro.medium.com/max/547/1*4NMSxE6I0L5Q5EvJRnKkVg.png)

1. **Generate new payment address**
   We start by using the *get_new_addresses()* function in PyOTA to generate a new payment address. Notice that we now have to provide a valid **seed** when creating our api object. This **seed** will be used by the function when generating addresses. Also notice that *get_new_addresses()* is a deterministic function, meaning that we need to provide a unique index to the function each time to make sure we don’t generate the same address twice. There may be different methods for providing a unique index to the function, such as timestamps etc. In my example, i simply use a counter that is incremented by 1 for each payment.
2. **Generate and display new QR code**
   Next, we take the new address and send it to our QR code generator. Notice that when making IOTA payments we have to include a checksum with the payment address. So before sending our address to the QR code generator we add the checksum to the address by using the *with_valid_checksum()* function.
3. **Check address for transactions**
   Next, we start looking for incoming payments to our address. As soon as a new transaction has been added to our address, we know that an incoming payment is on the way.
4. **Hide QR code**
   Next, we hide the QR code from our GUI to prevent new payments being sent to the same address while the first transaction is waiting to be confirmed. In my example i’m replacing the QR code with a message indicating that a new payment has been detected and that we are waiting for the payment to be confirmed.
5. **Get address balance**
   Next, we start checking our address for a positive balance, meaning that the transaction (payment) detected in step 3 has been confirmed.
6. **Add time to lightbalance**
   As soon as a positive balance has been detected, we take the new IOTA balance and convert it to time according to the current time/USD price. We finally add the calculated time to our current light balance and the process repeats itself.

## Components

There are no additional components required with respect to the [previous](https://medium.com/coinmonks/integrating-physical-devices-with-iota-adding-a-user-interface-2fb028a8fee1) tutorial.

------

## Required Software and libraries

There are no additional software or libraries required with respect to the [previous](https://medium.com/coinmonks/integrating-physical-devices-with-iota-adding-a-user-interface-2fb028a8fee1) tutorial.

------

## The Python Code

Now let’s have a look at some of the new functions that has been added to the Python code since the [previous](https://medium.com/coinmonks/integrating-physical-devices-with-iota-adding-a-user-interface-2fb028a8fee1) tutorial.

**The Seed**
The most important change is of course that we no longer have a fixed payment address where all of our payments are collected. Instead we generate a new address for each payment. For this reason we now have to provide a **seed** to the IOTA address generator. So make sure you replace the **seed** in the Python code with your own **seed**. See [here](https://blog.iota.org/the-secret-to-security-is-secrecy-d32b5b7f25ef) to learn more about creating IOTA seeds.

**The index counter**
A new read/write index counter function has been added to make sure we keep track of the latest address index used in case of a power failure etc. The index counter function uses the Python *configparser* library that stores data as a text file with the **.ini** format. Make sure you download and place the “let_there_be_light.ini“ file in the same folder as your Python program, otherwise you will get an error. You can download the file from [here](https://gist.github.com/huggre/c5185df916ca00d2e1d12943a9d9d03a).

**The waiting icon**
To prevent the user from making multiple payments to the same IOTA address, we temporarily replace our QR code with an hourglass icon as soon as a new payment has been detected. Notice that the pyQRcode library uses the TkInter BitmapImage function when rendering our QR code to the GUI. This function uses a special graphics file format called XBM, meaning that we can not use our typical graphics formats such as bmp, jpg, png etc. However, in case you want to create your own icon, there are applications and online services that allows you to convert your typical graphics formats to XBM. To prevent any errors when using my Python example code, make sure you download and place the “hourglass.xbm” file in the same folder as your Python program. You can download the file from [here](https://gist.github.com/huggre/c126863786991b49c2965d42b12f6b3d).

**The price**
As discussed earlier, we want to have the flexibility of easily changing the price of our service whenever appropriate. For this reason i have created the lightprice_USD variable that is read at startup of our Python program. The lightprice_USD variable is also used when converting our USD service price to IOTA’s. To change the price of your service, simply update the lightprice_USD variable to whatever value matches the price of your service. Notice that lightprice_USD is a floating number and that the price is in USD pr. minute of service.

```python
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
```

You can download the Python source code from [here](https://gist.github.com/huggre/c0b4776d9430c02c07671be19c400210)

## Running the project

To run the project, you first need to save the code in the previous section as a text file on your Raspberry PI.

Notice that Python program files uses the .py extension, so let’s save the file as **let_there_be_light_addr.py** on the Raspberry PI.

To execute the program, simply start a new terminal window, navigate to the folder where you saved *let_there_be_light_addr.py* and type:

**python let_there_be_light_addr.py**

You should now see the GUI appear on your LCD/Monitor, showing a QR code for the automatically generated IOTA payment address. As soon as one payment has been confirmed, a new address will be generated and displayed in the GUI. To exit the Python program you simply press the Exit button.

*Note!
Make sure you download and place the “iota_logo75.jpg” file in the same folder as your python file before executing the program, otherwise you will get an error. The logo file can be downloaded from* [*here*](https://github.com/huggre/pay_the_light_gui/blob/master/iota_logo75.jpg)*.*

------

## Pay the light

To turn on the LED (or in my case, set the **Light is ON** status) you simply use your favorite mobile IOTA wallet, scan the QR code displayed in the GUI, and transfer some IOTA’s. As soon as the transaction is confirmed by the IOTA tangle, the LED should light up (or in my case, set the **Light is ON** status), and stay on until the light balance is empty, depending on the amount of IOTA’s you transferred.

------

## Donations

If you like this tutorial and want me to continue making others, feel free to make a small donation to the IOTA address shown below.

![img](https://miro.medium.com/max/400/1*kV_WUaltF4tbRRyqcz0DaA.png)

> GTZUHQSPRAQCTSQBZEEMLZPQUPAA9LPLGWCKFNEVKBINXEXZRACVKKKCYPWPKH9AWLGJHPLOZZOYTALAWOVSIJIYVZ
