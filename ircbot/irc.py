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
        time.sleep(0.5)
        print self.irc.recv ( 256 )
        time.sleep(0.1)
        self.irc.send('NICK ' + botnick + "\r\n")
        self.irc.send('USER %s %s %s :botnick\r\n' % (botnick, botnick, botnick))
        self.irc.send('PASS %s\r\n' % password)
        self.irc.send(str.encode(':JOIN %s\r\n' % channel))
        self.irc.send('PRIVMSG :%s\r\n' % "Hello world")
        
    def write_text(self, chan, msg):
        self.irc.send('PRIVMSG #%s :%s\r\n' % (chan, msg))
        
    def get_text(self):
        text=self.irc.recv(256)   # Receive the text
        time.sleep(0.05)
 
        if text.find('PING') != -1:
            self.irc.send('PONG ' + text.split() [1] + '\n'),
        if text.find ( '!TECkit quit' ) != -1:
            self.irc.send ( 'PRIVMSG :Fine, if you dont want me\r\n' )
            self.irc.send ( 'QUIT\r\n' )
            quit()
        if text.find ( 'TECKit *IDN?' ) != -1:
            self.irc.send ( 'PRIVMSG #xDevs.com :Im TECKit snake ver. -0.00 ...\r\n' )
        return text
