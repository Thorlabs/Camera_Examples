#CCM
import serial
from enum import Enum
from aerodiode import Aerodiode
import csv
import struct

class Mmd(Aerodiode):
    """
        Class to command one MMD Aerodiode's product
    """
    VERSION = "1.1.0"
    
    #Instruct
    INSTRUCT_LASER_MAX_CURRENT          = 0x0A 
    INSTRUCT_DIODE_CURRENT              = 0x0B 
    INSTRUCT_CURRENT_SOURCE             = 0x0C 
    INSTRUCT_LASER_SLOPE                = 0x0D 
    INSTRUCT_LASER_ACTIVATION           = 0x0E
    INSTRUCT_LASER_TEMPERATURE          = 0x0F 
    INSTRUCT_DC_VOLTAGE                 = 0x11 
    INSTRUCT_DC_VOLTAGE_MODE            = 0x16 
    INSTRUCT_APC_MODE                   = 0x17 
    INSTRUCT_DC_MAX_VOLTAGE             = 0x1D 
    INSTRUCT_TEC_MODE                   = 0x1F 
    INSTRUCT_FUNCTIONMENT_MODE          = 0x22 
    INSTRUCT_PULSE_FREQUENCY            = 0x23 
    INSTRUCT_PULSE_WIDTH                = 0x24 
    INSTRUCT_PULSE_LASER_MODE           = 0x25 
    INSTRUCT_PULSE_GATE_MODE            = 0x26 
    INSTRUCT_BURST_COUNT                = 0x27 
       
    #Measure ID
    M_LASER_CURRENT                     = 0x00 
    M_LASER_DIODE_VOLTAGE               = 0x01 
    M_TEC_CURRENT                       = 0x02 
    M_TEC_VOLTAGE                       = 0x03 
    M_TEC_TEMPERATURE                   = 0x04 
    M_CASE_TEMPERATURE                  = 0x05 
    M_PD_EXT_1_INPUT                    = 0x06 
    M_PD_EXT_2_INPUT                    = 0x07 
    M_ALARM_STATE                       = 0x08 

    #ALARM
    

    def __init__(self, port, address = -1):
      """
        Open serial device.
        :param dev: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      #Connection
      Aerodiode.__init__(self,port,address)

      #Alarm Status
      self.alarm_status = dict(EXT_Alarm = 0, VPWR_Alarm = 0, Diode_Volatge_Alarm = 0, Case_Max_T_Alarm = 0,
                               Laser_Max_T_Alarm = 0,CPU_Alarm = 0, PD_EXT1_Alarm = 0, Spare = 0)
      


    def measure_laser_current(self):
        return self.measure(self.M_LASER_CURRENT, 1)
    def measure_laser_diode_voltage(self):
        return self.measure(self.M_LASER_DIODE_VOLTAGE, 1)
    def measure_tec_current(self):
        return self.measure(self.M_TEC_CURRENT, 1)
    def measure_tec_volatge(self):
        return self.measure(self.M_TEC_VOLTAGE, 1)
    def measure_case_temperature(self):
        return self.measure(self.M_CASE_TEMPERATURE, 1)
    def measure_pd_ext1_input(self):
        return self.measure(self.M_PD_EXT_1_INPUT, 1)
    def measure_pd_ext2_input(self):
        return self.measure(self.M_PD_EXT_2_INPUT, 1)

    def read_alarm_status(self):
        alarm_status_bit = "{0:08b}".format(self.measure(self.M_ALARM_STATE)) #str type
        print(alarm_status_bit)
        alarm_status_bit = alarm_status_bit[::-1]
        
        if int(alarm_status_bit,2) == 0xFFFFFFC0:
            self.alarm_status['Spare'] = 1

        j = 0 
        for i in self.alarm_status:
            if i != 'Spare':
                self.alarm_status[i] = int(alarm_status_bit[j],2)
                j += 1
                
        return self.alarm_status
    
       

   
   
   
    
   
