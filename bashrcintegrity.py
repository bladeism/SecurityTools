import difflib
from email.MIMEText import MIMEText
import getpass
import hashlib
import os
import requests
import shutil
import smtplib
import urllib2

def calculateOriginalValues(fileUrl, tempFile):
    r = requests.get(fileUrl)
    with open(tempFile, "w") as f:
        f.write(r.content)
        f.close()
    with open(tempFile, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
    
def compareHashes(originalHash, originalFile):
    # Calculate MD5 of .bashrc
    with open(".bashrc", "rb") as f:
        calculated_md5 = hashlib.md5(f.read()).hexdigest()

    # Compare original MD5 hash with calculated MD5 hash
    if originalHash == calculated_md5:
        print "MD5 verified."
        return None
    else:
        print "MD5 verification failed!"
        
        file1 = open(".bashrc", "rb").readlines()
        file2 = open(originalFile, "rb").readlines()

        diff = difflib.ndiff(file1, file2)

        if not os.path.exists("modified"):
            os.makedirs("modified")
        else:
            shutil.rmtree("modified")
            os.makedirs("modified")

        os.rename(".bashrc", "modified/.bashrc_modified")
        os.rename(originalFile, ".bashrc")

        differences = ""
        
        try:
            while 1:
                diff_string = diff.next()
                if not (diff_string[0] == " "):
                    differences += diff_string + "\r\n"
            if diff is None:
                pass
        except:
            pass
        return differences

def sendEmail(configFile, diffString):
    config = {}
    execfile(configFile, config) 

    sender = config["sender"]
    recipient = config["recipient"]
    subject = config["subject"]
    body = diffString

    headers = ["From: " + sender,
           "Subject: " + subject,
           "To: " + recipient,
           "MIME-Version: 1.0",
           "Content-Type: text/plain"]
    headers = "\r\n".join(headers)

    server = smtplib.SMTP(config["server"], config["serverPort"])
    server.ehlo()
    server.starttls()
    server.ehlo()
    password = getpass.getpass("Enter the password for " + sender + ": ")
    server.login(sender, password)
    server.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
    server.close()

def main():
    fileUrl = ("https://raw.githubusercontent.com/"
               "doyler/BashrcIntegrity/master/.bashrc")
    tempFile = "temp.txt"
    
    originalHash = calculateOriginalValues(fileUrl, tempFile)
    diffString = compareHashes(originalHash, tempFile)
    if diffString is not None:
        sendEmail("email.conf", diffString)
    else:
        if os.path.isfile(tempFile):
            os.remove(tempFile)

if __name__ == '__main__':
    main()
