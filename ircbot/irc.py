import socket
import sys,  time
 
class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    def connect(self, server, channel, botnick, password):
        #defines the socket
        print "connecting to:"+server
        self.irc.connect((server, 6667))             # Connects to the IRC server
        print self.irc.recv ( 4096 )
        time.sleep(6)
        self.irc.send('NICK ' + botnick + "\r\n")
        self.irc.send('USER %s %s %s :Python IRC\r\n' % (botnick, botnick, botnick))
        self.irc.send('NickServ ID %s\r\n' % password)
        self.irc.send('JOIN :%s\r\n' % channel)
        self.irc.send('PRIVMSG :%s\r\n' % "Hello world")
        
    def write_text(self, chan, msg):
        self.irc.send('PRIVMSG #%s :%s\r\n' % (chan, msg))
        time.sleep(0.1)
        
    def get_text(self):
        text=self.irc.recv(4096)   # Receive the text
 
        if text.find('PING') != -1:
            self.irc.send('PONG ' + text.split() [1] + '\n'),
        if text.find ( '!TECkit quit' ) != -1:
            self.irc.send ( 'PRIVMSG :Fine, if you dont want me\r\n' )
            self.irc.send ( 'QUIT\r\n' )
            quit()
        if text.find ( 'TECKit *IDN?' ) != -1:
            self.irc.send ( 'PRIVMSG #xDevs.com :Im TECKit snake ver. -0.00 ...\r\n' )
        return text
