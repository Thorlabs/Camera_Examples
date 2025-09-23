''''
Gather the Aerodiode and Status class:
   -> Aerodiode enables Python to drive any Aerodiode's device
   -> Status enables Python to manage the warning errors
'''


#Importations
import serial #library for the UART tranmission
from enum import Enum #requires for the error management
import struct #requires for the error management
import time

#Déclaration de la classe
class Aerodiode():
   """
       Base Aerodiode's device communication.
       An instance of :class:'Aerodiode' uses a serial port and is used by multiple :class:'CCS','SHAPER','CCM' etc... .
       Aerodiode enables:
       - the connection by the UART, open and close the port
       - the send of query and the reception of response
       -        
   """
   VERSION = "1.1.0"
   #Constant
   CONST_MAX_LENGHT_QUERY     = 0xFA
   DEFAULT_TIMEOUT            = 0.5

   #Commands
   COMMAND_GET_ADD            = 0x01
   COMMAND_READ_PROTOCOLE     = 0x02
   COMMAND_READERR            = 0x03
   COMMAND_WRITE              = 0x10
   COMMAND_READ_INSTRUCTIONS  = 0x11
   COMMAND_APPLY_ALL          = 0x12
   COMMAND_SAVE_ALL           = 0x13
   COMMAND_READ_MEASURE       = 0x14

   #xnn value
   OFF                        = 0x00
   ON                         = 0x01

   INTERNAL                   = 0x00
   EXTERNAL                   = 0x01

   DISABLE                    = 0x00
   ENABLE                     = 0x01

   MANUAL                     = 0x00
   AUTOMATIC                  = 0x01

   INT_INT                    = 0x00
   EXT_INT                    = 0x01

   NONE                       = 0x00
   SOFT                       = 0x01

   ANALOG                     = 0x00
   NUMERIC                    = 0x01

   EXTERNAL_TTL_LVTTL_PULSE   = 0x00
   EXTERNAL_LVDS_PULSE        = 0x01
   INTERNAL_PULSE             = 0x02
   
   #Opened port list
   PORTS                      = []
   

   #Methods   
   def __init__(self, port, address = -1):     
      """
         Open serial device.
         :param port: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      self.checkPorts(port)
      if(address == -1):
         self._add = self.get_addr() #get the adress
      else:
         self._add = address #get the adress

   def __del__(self):
      """
        Destructor automatically called at each end of script.
        Close the serial port.
      """
      if hasattr(self,'ser'):   
        self.ser.close()
   
   def checkPorts(self, port):
      """
        Checks if the port is already used
      """
      alreadyOpened = False
      for i in range (len(Aerodiode.PORTS)) :
         if(Aerodiode.PORTS[i].port == port) :
            if not Aerodiode.PORTS[i].is_open:
               self.ser.open()
            self.ser = Aerodiode.PORTS[i]
            alreadyOpened = True

      if not alreadyOpened :
         self.ser = serial.Serial(port, baudrate=125000, timeout=Aerodiode.DEFAULT_TIMEOUT) #open serial port   
         Aerodiode.PORTS.append(self.ser) 
         self.ser.name  
         
   def open(self):    
      """
         Open the serial port.
         :param port: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      if not self.ser.is_open:
               self.ser.open()

   def close(self):
      """
         Close the serial port.
      """
      self.ser.close()
      
   def checksum(self, mess):
      """
        Calculate the checksum of some data.
        :param data: Input data bytes.
        :return: Checksum byte value.
      """
      chk = 0
      for byte in mess:
         chk ^= byte #xor
      return (chk-1)%256 #result < 255 chk is on 8 bit

   def receive_response(self):
      """
        Receive a response. Verify the status and checksum.
        :return: Received data, without header and checksum.
      """
      # Get length byte.
      data = self.ser.read(1)
      # Length byte must be at least 3 for responses (length byte, status
      # byte and checksum byte).
      if len(data) == 0:   
        raise Timeout()     
      if data[0] < 3:
         raise ProtocolError()
      # Fetch all the bytes of the command
      data += self.ser.read(data[0]-1)

      #print("answer = ",data.hex("\\")) #debug

      # Verify the checksum
      if self.checksum(data[:-1]) != data[-1]:
          raise ChecksumError()
      # Verify the status
      if data[1] != 0x00:
          raise StatusError(data[1])
      return data[1:-1]

   def send_query(self, address, command, data = [], timeout=0.0):
      """
        Transmit a command to the laser source. This method automatically add
        the length and checksum bytes.
        :param address: Device address.
        :param command: An instance of Command define.
        :param data: Data bytes.
        :param address: Device address override.
      """
      data = bytearray(data)
      length = 4 + len(data)
      if length > self.CONST_MAX_LENGHT_QUERY: 
         raise ValueError('data too long.')
      frame = bytearray([length, address, command]) + data
      frame.append(self.checksum(frame))

      #print("request = ", frame.hex("\\")) #debug

      self.ser.write(frame)

      if timeout == -1:
        self.ser.timeout = None
      elif timeout != 0.0 :
        self.ser.timeout = timeout
            
      res = self.receive_response()
      self.ser.timeout = Aerodiode.DEFAULT_TIMEOUT
      return res

   def write(self, consign_id, xnnvalue = [0], timeout = 0.0): #not usefull
      """
         write instruction such as laser on
      """

      consign_id1 = consign_id//0xFF
      consign_id0 = consign_id - (consign_id//0xFF)*0xFF
      return self.send_query(self._add, self.COMMAND_WRITE, [consign_id1, consign_id0] + xnnvalue,timeout)
      

   def get_addr(self):
      """
         Get the adress of the card.
         :return: the adress of the card
      """
      answer = self.send_query(0x00, self.COMMAND_GET_ADD)
      if self.status(answer) != 0:
         return self.status
      return int(answer[1]) #peut'être défaut si la carte à une adress >9 à vérifier

   def save_all(self, timeout = 0.0):
      """
         Save instructions
      """
      return self.send_query(self._add, self.COMMAND_SAVE_ALL, [], timeout)

   def apply_all(self, timeout = 0.0):
      """
         Apply all the set in the card
      """
      return self.send_query(self._add, self.COMMAND_APPLY_ALL, [], timeout) #used the timeout with the shaper 

   def status(self, answer):
      if (answer[0] == 0):
         return 0
      else:
         return answer[0]
     

   def read_float_instruction(self, instruction): #vérifier que ce la s'adapte à tout type de meusure
      """
         Get an instruction value from a specific consign.
         :param consign:
         :return: measure in float type
      """
      data = self.send_query(self._add, self.COMMAND_READ_INSTRUCTIONS, [0x00,  instruction]) #Read
      return round(struct.unpack('>f', bytes(data[1::]))[0],10)
      
   def set_float_instruction(self, instruction, value = 0.0):

      """
         Set a float value.
         :param instruction:
         :param value:
      """

      if isinstance(value, float) == False and isinstance(value, int) == False:
         return -2 #A améliorer

      value = float(value)
      
      size = len(self.send_query(self._add, self.COMMAND_READ_INSTRUCTIONS, [0x00,  instruction])) - 1
      tab_value = []
      data = struct.pack('>f',value)

      for i in range(0, size):
            tab_value.append(data[i])
            
      return self.send_query(self._add, self.COMMAND_WRITE, [0x00, instruction]+tab_value)


   def read_current_instruction(self, instruction):
      return self.read_float_instruction(instruction)

   def set_current_instruction(self, instruction, value=0.0):
      return self.set_float_instruction(instruction, value)
      
   def read_voltage_instruction(self, instruction):
      return self.read_float_instruction(instruction)

   def set_voltage_instruction(self, instruction, value=0):
      return self.set_float_instruction(instruction, value)

   def read_temperature_instruction(self, instruction):
      return self.read_float_instruction(instruction)

   def set_temperature_instruction(self, instruction, value = 0.0):
      return self.set_float_instruction(instruction, value)

   def read_percent_instruction(self, instruction):
      return self.read_float_instruction(instruction)

   def set_percent_instruction(self, instruction, value = 0.0):
      return self.set_float_instruction(instruction, value)

   def read_power_instruction(self, instruction):
      return self.read_float_instruction(instruction)

   def set_power_instruction(self, instruction, value = 0.0):
      return self.read_float_instruction(instruction)
   

   def read_integer_instruction(self, instruction):
      """
         Get an integer value from a specific consign.
         :param instruction:
         :return: value in integer type
      """
      return int.from_bytes(self.send_query(self._add, self.COMMAND_READ_INSTRUCTIONS, [0x00,  instruction]), byteorder = 'big', signed=False)

   def set_integer_instruction(self, instruction, value = 0):
      """
         Set an integer value.
         :param instruction:
         :param: value
      """

      if isinstance(value, int) == False and isinstance(value, float):
         return -1 #A améliorer

      value = int(value)

      size = len(self.send_query(self._add, self.COMMAND_READ_INSTRUCTIONS, [0x00,  instruction])) - 1
      tab_value = []
      data = value.to_bytes(size, 'big')
      for i in range(0, size):
            tab_value.append(data[i])
      return self.send_query(self._add, self.COMMAND_WRITE, [0x00, instruction]+tab_value)
      
   def read_status_instruction(self, instruction):
      return self.read_integer_instruction(instruction)
         
   def set_status_instruction(self, instruction, value = 0):
      return self.set_integer_instruction(instruction, value)

   def read_time_instruction(self, instruction):
      return self.read_integer_instruction(instruction)

   def set_time_instruction(self, instruction, value = 0):
      return self.set_integer_instruction(instruction, value)

   def read_freq_instruction(self, instruction, value = 0):
      return self.read_integer_instruction(instruction)

   def set_freq_instruction(self, instruction, value = 0):
      return self.set_integer_instruction(instruction, value)

   def read_step_instruction(self, instruction):
      return self.read_integer_instruction(instruction)

   def set_step_instruction(self, instruction, value = 0):
      return self.set_integer_instruction(instruction, value)

   def measure(self, measureid, typ = 0):
      '''
         Get a measure
         :param measureid:
         :param typ: data type int( = 0) or float( = 1)
      '''
      if typ == 0:
         return int.from_bytes(self.send_query(self._add, self.COMMAND_READ_MEASURE, [0x00,  measureid]), byteorder = 'big', signed=False)
      else:
         data = self.send_query(self._add, self.COMMAND_READ_MEASURE, [0x00,  measureid]) #Read 
         return round(struct.unpack('>f', bytes(data[1::]))[0],10)

   




#Status-----------------------------------------------------------------------------
      
class Status(Enum):
   """ Response status from the Aerodiode device. """
   OK = 0x00
   TIMEOUT = 0x01
   UNKNOWN_COMMAND = 0x02
   QUERY_ERROR = 0x04
   BAD_LENGTH = 0x08
   CHECKSUM_ERROR = 0x10

class StatusError(Exception):
    """
    Thrown when an Aerodiode device did not respond with 'OK' status to the last
    command.
    """
    def __init__(self, status):
        """
        :param status: Status code. int.
        """
        super().__init__()
        self.status = status

    def __str__(self):
        return str(Status(self.status))

class ChecksumError(Exception):
    """ Thrown if a communication checksum error is detected. """
    # AL pass
    def __str__(self):              
        return 'ChecksumError'


class ProtocolError(Exception):
    """ Thrown if an unexpected response from the device is received. """
    # AL pass
    def __str__(self):              
        return 'ProtocolError'


class ConnectionFailure(Exception):
    # AL pass
    def __str__(self):              
        return 'ConnectionFailure'


class ProtocolVersionNotSupported(Exception):
    """
    Thrown when a PDM protocol version is not (yet) supported by the library.
    """
    def __init__(self, version):
        """
        :param version: Version string.
        """
        super().__init__()
        self.version = version

    def __str__(self):
        return self.version


class Timeout(Exception):              
    def __str__(self):
        return 'Timeout'
