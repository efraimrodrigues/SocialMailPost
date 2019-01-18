#!/usr/bin/env python3

import sys
import imaplib
import getpass
import email
import email.header
import time
from datetime import datetime

from fbchat import Client
from fbchat.models import *



EMAIL_ACCOUNT = "YOUR@MAIL.COM"

# Use 'INBOX' to read inbox.  Note that whatever folder is specified, 
# after successfully running this script all emails in that folder 
# will be marked as read.
#EMAIL_FOLDER = '"Erros SI3"'
EMAIL_FOLDER = 'INBOX'


def process_mailbox(M,client):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, 'UNSEEN')
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))

        subject = str(hdr)
        sender = msg['From']

        print(sender)
        print('Message %s: %s' % (num, subject))
        print('Raw Date:', msg['Date'])
        client.send(Message(text= 'New email message: *_' + sender + '_*: ' + subject), thread_id=client.uid, thread_type=ThreadType.USER)
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            print ("Local Date:", \
                local_date.strftime("%a, %d %b %Y %H:%M:%S"))


#imap.gmail.com
M = imaplib.IMAP4_SSL('IMAP.SERVER.COM')

try:
    print("Logging into email account: " + EMAIL_ACCOUNT)
    rv, data = M.login(EMAIL_ACCOUNT, getpass.getpass())

    login = input("Facebook login: ")
    password = getpass.getpass()

    client = Client(login, password)
    print('Own id: {}'.format(client.uid))



except imaplib.IMAP4.error:
    print ("LOGIN FAILED!!! ")
    sys.exit(1)

print(rv, data)

rv, mailboxes = M.list()
if rv == 'OK':
    print("Mailboxes:")
    print(mailboxes)

rv, data = M.select(EMAIL_FOLDER)
if rv == 'OK':
    print('Starting mail monitor')
    while True:
        time.sleep(0.5)
        print("[" + str(datetime.now().strftime("%I:%M:%S")) + "]: Waiting for new messages!",end='')
        print('\r',end='')
        result = M.search(None,'UNSEEN')
        if result:
            process_mailbox(M,client)
        
        continue
else:
    print("ERROR: Unable to open mailbox ", rv)

M.logout()
client.logout()