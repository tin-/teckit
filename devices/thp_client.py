# http://www.binarytides.com/python-socket-programming-tutorial/
#Socket client example in python
# Modified from original code by Todd Micallef

# Error codes
# 0 = no error (yay!)
# 1 = Socket Creation Failed
# 2 = Failed Sending Data
# 3 = Socket Connection Timeout
# 4 = Error Splitting Returned Data (returned string does not have the correct number of values)
# 5 = Error closing connection
# 6 = Receive error. Could be caused by server terminating connection
 
import socket #for sockets
import sys    #for exit
import signal # for timeout
 
class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()


class THP_socket():
  def __init__(self,host,port):
    self.host = host
    self.port = port

  def connect(self):
    #Connect to remote server
    try:
      with Timeout(5):
        self.s.connect((self.host , self.port))
    except Timeout.Timeout:
      # Socket connection timeout exception
      return 3
    #print 'Socket Connected to ' + self.host + ' on port ' + str(self.port)
    return 0


  def create_socket(self):
    #create an INET, STREAMing socket
    try:
      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
      # Socket creation failed
      return 1

    return 0

  def close_connection(self):
    try:
      self.s.close()
    except socket.error:
      return 5

    return 0

  def send_data_THP(self):
    #Send some data to remote server
    message = "READ?3"
 
    try :
      #Set the whole string
      self.s.sendall(message)
    except socket.error:
      #Send failed
      return 2

    return 0

  def send_data_TH(self):
    #Send some data to remote server
    message = "READ?1"
 
    try :
      #Set the whole string
      self.s.sendall(message)
    except socket.error:
      #Send failed
      return 2

    return 0

  def receive_data(self):
    #Now receive data
    try :
      self.reply = self.s.recv(4096)
      self.s.close()
    except socket.error:
      # Receive failed. Could be connection is closed
      return 6

    return 0

  def getTHP(self):
    error = 0
    error = self.create_socket()
    if (error == 0):
      error = self.connect()
      if (error == 0):
        error = self.send_data_THP()
        if (error == 0):
          self.receive_data()
          ssplit = self.reply.split(',')
          if (len(ssplit) == 3):
            self.exttemp = ssplit[0]
            self.rh = ssplit[1]
            self.press = ssplit[2]
          else:
            error = 4
    return (error,self.exttemp,self.rh,self.press)


  def getTH(self):
    error = 0
    error = self.create_socket()
    if (error == 0):
      error = self.connect()
      if (error == 0):
        error = self.send_data_TH()
        if (error == 0):
          self.receive_data()
          ssplit = self.reply.split(',')
          if (len(ssplit) == 2):
            self.exttemp = ssplit[0]
            self.rh = ssplit[1]
          else:
            error = 4
    return (error,self.exttemp,self.rh)

# Example usage
#thp = THP_socket('192.168.100.151',10001) 
#error,temp,rh,press = thp.getTHP()
#print 'getTHP called... Error = ' + str(error) + ' : Temp = ' + str(temp) + ' : RH = ' + str(rh) + ' : Pressure = ' + str(press)
#error,temp,rh = thp.getTH()
#print 'getTH called... Error = ' + str(error) + ' : Temp = ' + str(temp) + ' : RH = ' + str(rh)

