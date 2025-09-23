#ccsv5
import serial
from enum import Enum
from aerodiode import Aerodiode
import csv
import struct


class Pdmv5(Aerodiode):
    """
        Class to command one Ccs CW Aerodiode's product
    """
    #Command
    VERSION = "1.1.0"
    
    COMMAND_READ_CW_OR_PULSE                    = 0x20

    #Instruction
    INSTRUCT_TEMPERATURE_SET_POINT              = 0x16 
    INSTRUCT_COMPLIANCE_VOLTAGE                 = 0x1E 
    INSTRUCT_MAX_AVERAGE_CURRENT                = 0x1F     
    INSTRUCT_LASER_ACTIVATION                   = 0x20 
    INSTRUCT_PEAK_CURRENT_SETPOINT_SRC          = 0x29 
    INSTRUCT_MAX_PEAK_CURRENT_SETPOINT          = 0x2A 
    INSTRUCT_PEAK_CURRENT_SETPOINT              = 0x2B 
    INSTRUCT_SYNC                               = 0x2C 
    INSTRUCT_SYNC_FREQUENCY                     = 0x2E 
    INSTRUCT_PULSE_WIDTH                        = 0x2F 
    INSTRUCT_PULSE_IN_THRESHOLD                 = 0x31 
    INSTRUCT_CW_CURRENT_SETPOINT_SRC            = 0x3D 
    INSTRUCT_CW_MAX_CURRENT                     = 0x3E 
    INSTRUCT_CURRENT_SETPOINT                   = 0x3F 
    INSTRUCT_FUNCTIONING_MODE                   = 0x41 
    INSTRUCT_MODULATION_ACTIVATION              = 0x46 
    INSTRUCT_CURRENT_MODULATION_MAX             = 0x47 
    INSTRUCT_CURRENT_MODULATION_SETPOINT        = 0x48 
    INSTRUCT_INTERNAL_MODULATION_TYPE           = 0x49 
    INSTRUCT_MODULATION_FREQUENCY               = 0x4A 
    INSTRUCT_GAIN_EXT_MODULATION                = 0x4B 
    INSTRUCT_BFM_GAIN                           = 0x50 
    INSTRUCT_PD_EXT_GAIN                        = 0x51 
    INSTRUCT_BFM_CONVERSION                     = 0x53
    INSTRUCT_PD_EXT_CONVERSION                  = 0x54
    INSTRUCT_INTER_TIME_MEASURE_LIV             = 0x5A 
    INSTRUCT_LIVE_MEASURE_COUNT_AVERAGE         = 0x5B 
    INSTRUCT_LIV_CURRENT_STEP                   = 0x5C 
    INSTRUCT_LIV_CURRENT_MIN                    = 0x5D 
    INSTRUCT_LIV_CURRENT_MAX                    = 0x5E 
    INSTRUCT_LIV_PHOTODIODE                     = 0x5F 
    INSTRUCT_PULSE_WIDTH_LIV                    = 0x60 
    INSTRUCT_VCOMP_POTAR                        = 0x6F

    #Measure
    M_EXT_INTERLOCK_STATE                       = 0x02
    M_LIV_MEASURE                               = 0x03
    M_PEAK_CURRENT_SETPOINT                     = 0x0A
    M_CW_CURRENT_SETPOINT                       = 0x0B
    M_T_SETPOINT                                = 0x0C
    M_T_DIODE                                   = 0x14
    M_TEC_VREF                                  = 0x15
    M_TEC_CURRENT                               = 0x16
    M_T_EXT_CTN                                 = 0X17
    M_T_MOS                                     = 0x18
    M_TEC_VOLTAGE                               = 0x19
    M_DIODE_VOLTAGE                             = 0x1E
    M_CW_CURRENT                                = 0x1F
    M_AVERAGE_CURRENT                           = 0x20
    M_PULSED_CURRENT                            = 0x21
    M_BFM_CURRENT                               = 0x28
    M_PD_EXT_CURRENT                            = 0x29
    M_BFM_POWER                                 = 0x2A
    M_PD_EXT_POWER                              = 0x2B
    M_ALARM_STATE                               = 0x46
    M_PICO_V_COMP                               = 0x36
    M_PICO_I_MON                                = 0x35
    M_VOLTAGE_IN                                = 0x3C
    M_VOLTAGE_COMPLIANCE                        = 0x3D
    M_VOLTAGE_5V                                = 0x3E
    M_VOLTAGE_3V3                               = 0x3F
    M_VOLTAGE_2V5                               = 0x40
    M_VOLTAGE_1V3                               = 0x41
    M_VOLTAGE_NEG_5V                            = 0x42


    #XNN Value
    INTERNAL                                    = 0x00
    POTENTIOMETER                               = 0x01
    EXTERNAL                                    = 0x02

    BFM                                         = 0x00
    PD_EXT                                      = 0x01

    ACC                                         = 0x00
    APC                                         = 0x01
    
    SINUS                                       = 0x01
    TRIANGLE                                    = 0x02
    SQUARED                                     = 0x03

    
    
    
    

    def __init__(self, port, address = -1):
      """
        Open serial device.
        :param dev: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      #Connection
      Aerodiode.__init__(self,port, address)

      #Alarm status (dict type)
      self.alarm_status = dict(INTERLOCK = 0, PWR = 0, DIODE_TEMPERATURE = 0, TEMPERATURE_MOS = 0,
                               TEC_EXT = 0, BNC_INTERLOCK = 0, EXT_INTERLOCK = 0, INTERLOCK_KEY = 0, MOS_CW = 0, RESERVED = 0, OPEN_CICUIT = 0)

    def read_cw_or_pulse(self):
        self.send_query(self._add, self.COMMAND_READ_CW_OR_PULSE, data = [])
    
    def set_vcomp_patch(self, instruction, value = 0):
        return self.set_integer_instruction(instruction, value)
        
    def measure_interlock(self):
        return self.measure(self.M_EXT_INTERLOCK_STATE, 0)

    def measure_liv_measure(self):
        return self.measure(self.M_LIV_MEASURE, 0)

    def measure_peak_current_setpoint(self):
        return self.measure(self.M_PEAK_CURRENT_SETPOINT, 1)

    def measure_cw_current_setpoint(self):
        return self.measure(self.M_PEAK_CURRENT_SETPOINT, 1)

    def measure_temperature_setpoint(self):
        return self.measure(self.M_T_SETPOINT, 1)

    def measure_temperature_diode(self):
        return self.measure(self.M_T_DIODE , 1)

    def measure_tec_vref(self):
        return self.measure(self.M_TEC_VREF , 1)

    def measure_tec_current(self):
        return self.measure(self.M_TEC_CURRENT, 1)

    def measure_diode_voltage(self):
        return self.measure(self.M_DIODE_VOLTAGE , 1)

    def measure_cw_current(self):
        return self.measure(self.M_CW_CURRENT , 1)

    def measure_average_current(self):
        return self.measure(self.M_AVERAGE_CURRENT , 1)

    def measure_pulsed_current(self):
        return self.measure(self.M_PULSED_CURRENT , 1)

    def measure_bfm_current(self):
        return self.measure(self.M_BFM_CURRENT, 1)

    def measure_pd_ext_current(self):
        return self.measure(self.M_PD_EXT_CURRENT, 1)

    def measure_voltage_5v(self):
        return self.measure(self.M_VOLTAGE_5V, 1)

    def measure_voltage_3v3(self):
        return self.measure(self.M_VOLTAGE_3V3, 1)

    def measure_voltage_2v5(self):
        return self.measure(self.M_VOLTAGE_2V5, 1)

    def measure_voltage_1v3(self):
        return self.measure(self.M_VOLTAGE_1V3, 1)
    
    def measure_vcomp(self):
        return self.measure(self.M_PICO_V_COMP, 1)

    def read_alarm_status(self):
        alarm_status_bit = "{0:011b}".format(self.measure(self.M_ALARM_STATE)) #str type
        alarm_status_bit = alarm_status_bit[::-1]
        if int(alarm_status_bit,2) == 0xFFFFFFC0:
            self.alarm_status['Spare'] = 1

        j = 0 
        for i in self.alarm_status:
            if i != 'Spare':
                self.alarm_status[i] = int(alarm_status_bit[j],2)
                j += 1
                
        return self.alarm_status
        

    
