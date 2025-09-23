'''
Classe TOMBAK
'''
import serial
from enum import Enum
from aerodiode import Aerodiode
import csv
import struct

class Tombak(Aerodiode):

    VERSION = "1.1.0"
    #Command--------------------------------------------
    COMMAND_WRITE_ADDRESS       = 0x00
    COMMAND_READ_EQUIPMENT      = 0x01
    COMMAND_WRITE_SHAPE_VALUE   = 0x16
    COMMAND_SAVE_SHAPE          = 0x17
    COMMAND_SOFT_TRIGG          = 0x18
    COMMAND_ENABLE_RESYNC       = 0x19

    #Instructions---------------------------------------
    INSTRUCT_FUNCTIONING_MODE          = 0x0A
    INSTRUCT_PULSE_IN_THRESHOLD        = 0x0B 
    INSTRUCT_PULSE_IN_DELAY            = 0x0C 
    INSTRUCT_PULSE_IN_SRC              = 0x0D 
    INSTRUCT_PULSE_IN_FREQUENCY_DIV_32 = 0x0F 
    INSTRUCT_PULSE_OUT_DELAY           = 0x10
    INSTRUCT_PULSE_OUT_WIDTH           = 0x11
    INSTRUCT_PULSE_BURST_SIZE          = 0x12
    INSTRUCT_TRIGGER_SRC               = 0x13
    INSTRUCT_INTERN_TRIGGER_FREQ       = 0x14
    INSTRUCT_SYNC_OUT_1_SRC            = 0x15
    INSTRUCT_GATE_CONTROL              = 0x16
    INSTRUCT_SYNC_OUT_2_SOURCE         = 0x17
    INSTRUCT_PULSE_OUT_INVERSION       = 0x18
    INSTRUCT_FINE_DELAY_ACTIVATION     = 0x1B
    INSTRUCT_EXTERNAL_GATE_SOURCE      = 0x1C
    INSTRUCT_RESYNC_DIVISION_32        = 0x1D
    INSTRUCT_SHAPE1_STEP_NUMBER        = 0x1E
    INSTRUCT_SHAPE1_STEP_SIZE          = 0x1F
    INSTRUCT_SHAPE2_STEP_NUMBER        = 0x20
    INSTRUCT_SHAPE2_STEP_SIZE          = 0x21
    INSTRUCT_SHAPE3_STEP_NUMBER        = 0x22
    INSTRUCT_SHAPE3_STEP_SIZE          = 0x23
    INSTRUCT_SHAPE4_STEP_NUMBER        = 0x24
    INSTRUCT_SHAPE4_STEP_SIZE          = 0x25
    INSTRUCT_DEFAULT_VALUE             = 0x26
    INSTRUCT_CLK_EXT_ACTIVATION        = 0x27
    INSTRUCT_PULSE_IN_FREQUENCY_DIV_64 = 0x28
    INSTRUCT_RESYNC_DIVISION_64        = 0x29
    
    #Measure ID---------------------------------------
    M_PULSE_IN_FREQ                  = 0x00
    SYNC_EXT_FREQ                    = 0x01

    #XNN Value----------------------------------------
    DIVIDER                          = 1
    PULSE_PICKER                     = 2
    PULSE_GENERATOR                  = 3
    PULSE_SHAPE_DIVIDER              = 4
    PULSE_SHAPE_PICKER               = 5
    PULSE_SHAPE_GENERATOR            = 6
    HIGH                             = 7

    DIRECT                           = 0
    DAISY_SYNC_IN                    = 1

    INT                              = 0
    EXT                              = 1

    SYNC                             = 0
    TRIGGER                          = 1
    DELAY                            = 2
    PULSE_OUT                        = 3

    NO_GATE                          = 0
    GATE                             = 1
    BURST_GATE                       = 2
    BURST_SERIAL                     = 3

    PULSE_DIRECT                     = 0
    NULL                             = 1

    POSITIVE_LOGIC                   = 0
    NEGATIVE_LOGIC                   = 1

    PULSE_FREQ                       = 200000000
    
    CLK_EXT_ON                       = 1
    CLK_EXT_OFF                      = 0
    
    FINE_DELAY_OFF                   = 0
    FINE_DELAY_ON                    = 1
    
    GATE_GATE_EXT                    = 0
    DAISY_SYNC_IN_2                  = 1

    #MEASURE--------------------------------------

    M_PULSE_IN_FREQUENCY            = 0
    M_SYNC_EXT_FREQUENCY              = 1 

    #Methods

    def __init__(self, port, address = -1):
      """
        Open serial device.
        :param dev: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      #Connection
      Aerodiode.__init__(self,port, address)

    def save_shape_data(self):
      return self.send_query(self._add, self.COMMAND_SAVE_SHAPE)

    def read_csv(self, csv_file):
      """
         Convert a csv file in list..
         :param csv_file: file path of your csv file
         :return: a table from your csv file
      """
      table_csv = []                      
      with open(csv_file) as file: #open csv as file variable
         read = csv.reader(file) #read file variable
         print('', end='\n') #??? but it works
         for line in read: #read line by line
              #convert a list of string to int
              int_line = "".join(line) #step 1 convert the list in a string
              int_line = int(int_line) #step 2 convert in int
              table_csv.append(int_line) #add to the end of the table
      return table_csv
   
    def send_csv(self, shape_id, table_csv):
      """
         Send a csv_table to the Shaper.
         :param shape id: bytes from 0x00 to 0x03 (4 shapes available)
         :param shape table_csv: table of integer
         :no return 
      """
      """
      if table_csv[0]>4000:
         raise ValueError('data must be inferior to 4000.')
      """
      
      
      table_csv.pop(0)
      if len(table_csv)>4000:
         raise ValueError('data must be inferior to 4000.')
      csv_output = [table_csv[i:i +60] for i in range(0, len(table_csv), 60)] #tableau 2D contenant des tableaux 1D qui sont les découpes de table_csv par pacquet de 60.

      for i in range(0, len(csv_output)):

         start = [0x00, 0x00] #Always start at the offset 0 which is declared on two bytes
         if (i>0):
            length = (0x3C)*i #=(60)*i because the card receive the data 60 by 60 values
            if (length < 0xFF):#verify if the new offset could be represented on one or two bytes
               start[0] = length&0xFF
            else:
               start[0] = length&0xFF #first byte of the offset 
               start[1] = (length>>8)&0xFF #second byte of the offset

         csv_send = []
         for j in range(0,len(csv_output[i])):
            value1 = csv_output[i][j]//(0x100) 
            value0 = csv_output[i][j] - (csv_output[i][j]//0x100)*0x100
            #value 1 and 0 enable to represent each data on two bytes
            csv_send.append(value1)
            csv_send.append(value0)
             
         data = [shape_id, start[1], start[0]] + csv_send #concatenate the data
        
         self.send_query(self._add, self.COMMAND_WRITE_SHAPE_VALUE, data) #send the csv_send

    def software_trigger(self):
        return self.send_query(self._add, self.COMMAND_SOFT_TRIGG)

    def measure_pulse_in_frequency(self):
        return self.measure(self.M_PULSE_IN_FREQUENCY)

    def measure_sync_ext_frequency(self):
        return self.measure(self.M_SYNC_EXT_FREQUENCY)

        
    def enable_resync(self):
        return self.send_query(self._add, self.COMMAND_ENABLE_RESYNC)

    
   
