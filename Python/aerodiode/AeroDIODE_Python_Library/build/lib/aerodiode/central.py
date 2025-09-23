#CCM
import serial
from enum import Enum
from aerodiode import Aerodiode
import csv
import struct

class Central(Aerodiode):
    VERSION = "1.1.0"
    
    INSTRUCT_LASER_ACTIVATION                        = 0x0A #ok
    INSTRUCT_ALIGNEMENT_DIODE_ACTIVATION             = 0x0F #ok
    INSTRUCT_TRIGGER_FREQUENCY                       = 0x14 #ok
    INSTRUCT_DELAY_MODE                              = 0x15 #ok
    INSTRUCT_DELAY                                   = 0x16 #ok
    INSTRUCT_SECURITY_COEFF_MODE                     = 0x17 #ok
    INSTRUCT_SECURITY_COEFF                          = 0x18 #ok
    INSTRUCT_CURRENT_SLOPE_MODE                      = 0x19 #ok 
    INSTRUCT_CURRENT_SLOPE                           = 0x1A #ok
    INSTRUCT_EM_GATE                                 = 0x1B #ok
    INSTRUCT_AUX_OFF                                 = 0x1C #ok
    INSTRUCT_LASER_POWER_MODE                        = 0x1D #ok
    INSTRUCT_TRIGGER_MODE                            = 0x1E #ok

    ###????###                              #ok
    INSTRUCT_WATCHDOG_PD_PULSE_PHOTO                 = 0x1F

    ##SMD1 LASER DIODE CONTROL              #ok
    INSTRUCT_SMD1_TEMPERATURE                        = 0x28
    INSTRUCT_SMD1_VALIM                              = 0x29
    INSTRUCT_SMD1_MODE                               = 0x2B
    INSTRUCT_SMD1_CURRENT                            = 0x2C
    INSTRUCT_SMD1_POWER                              = 0x2D
    INSTRUCT_SMD1_MAX_CURRENT                        = 0x2E
    INSTRUCT_SMD1_CURRENT_RATIO                      = 0x2F

    ##SMD2 LASER DIODE CONTROL              #ok
    INSTRUCT_SMD2_TEMPERATURE                        = 0x32
    INSTRUCT_SMD2_PULSED_MODE                        = 0x33
    INSTRUCT_SMD2_PULSE_WIDTH                        = 0x34
    INSTRUCT_SMD2_CURRENT                            = 0x35
    INSTRUCT_SMD2_OFFSET_CURRENT                     = 0x36
    INSTRUCT_SMD2_MAX_AVERAGE_CURRENT                = 0x37
    INSTRUCT_SMD2_MAX_PEAK_CURRENT                   = 0x38
    INSTRUCT_SMD2_OPERATING_MODE                     = 0x39
    #INSTRUCT_OPERATING_MODE

    ##MMD                                   #ok
    INSTRUCT_MMD1_LASER_ACTIVATION                   = 0x3C
    INSTRUCT_MMD2_LASER_ACTIVATION                   = 0x3D
    INSTRUCT_MMD3_LASER_ACTIVATION                   = 0x3E
    INSTRUCT_MMD_LASER_DIODE_CURRENT                 = 0x3F
    
    

    ##ALARMS
    #SMD1_MAX_TEMPERATURE                    = 0x46
    #SMD1_MAX_TEMPERATURE                    = 0x47
    #MIN_TEMPERATURE                         = 0x48
    #MAX_TEMPERATURE                         = 0x49
    #LOW_PD_IN_LASER_POWER_THRESHOLD         = 0x4A
    #LOW_PD_OUT_LASER_POWER_THRESHOLD        = 0x4B
    #LOW_PD_CRI_LASER_POWER_THRESHOLD        = 0x4C
    #SMD2_AVERAGE_CURRENT_THRESHOLD          = 0x4D
    #HIGH_POWER_LASER_RETURN_ALARM           = 0x4E
    INSTRUCT_ALARM_ACTIVATION                        = 0x4F
    INSTRUCT_INTERLOCK_IF_ALARM                      = 0x50
    INSTRUCT_DISABLE_1S_IF_ALARM                     = 0x51
    INSTRUCT_ALARM_HISTORY                           = 0x52

    ##PHOTODIODE                            #ok
    INSTRUCT_CALIBRATION_PD_IN                       = 0x5A
    INSTRUCT_CALIBRATION_PD_INTER_CW                 = 0x5B
    INSTRUCT_CALIBRATION_PD_OUT_CW                   = 0x5C
    INSTRUCT_CALIBRATION_PD_CRI_CW                   = 0x5D
    INSTRUCT_CALIBRATION_PD_BRA_CW                   = 0x5E
    INSTRUCT_PD_APC_MODE                             = 0x5F
    INSTRUCT_MODE_PD_OUT_CRI                         = 0x60
    INSTRUCT_MAX_ACC_TIME_BEFORE_PD_OUT              = 0x61
    INSTRUCT_MAX_ACC_TIME_BEFORE_PD_CRI               = 0x62
    INSTRUCT_PD_IN_PULSE_ALARM_TRIGGER_THRESHOLD     = 0x63

    ##PULSE PICKER CONTROL                  #ok
    INSTRUCT_OPERATING_MODE                          = 0x8C
    INSTRUCT_PULSE_IN_SOURCE                         = 0x8D
    INSTRUCT_DELAY_PULSE_IN                          = 0x8E
    INSTRUCT_DIVIDER_PULSE_IN                        = 0x8F
    INSTRUCT_DELAY_PULSE_OUT                         = 0x90#
    INSTRUCT_WIDTH_PULSE_OUT                         = 0x91#
    INSTRUCT_PULSE_OUT_MODE                          = 0x92
    INSTRUCT_ACTIVATION_DELAY                        = 0x93
    INSTRUCT_ACTIVATION_PULSE_WIDTH                  = 0x94

    #MEASURE ID
    M_MAIN_V_MON                              = 0
    M_HK_V_MON                                = 1
    M_RED_GUIDE_VMON                          = 2
    M_SMD1_T                                  = 3
    M_SMD2_T                                  = 4
    M_CASE_T                                  = 5
    M_SMD1_CURRENT                            = 6
    M_PD_OUT_POWER                            = 7
    M_PD_BRA_POWER                            = 8
    M_PD_IN_CW_POWER                          = 9
    M_PD_INTER_POWER                          = 10
    M_PD_CRI_POWER                            = 11
    M_PD_IN_PULSE_FREQUENCY                   = 12
    M_EXTERNAL_SYNC_FREQUENCY                 = 13
    M_LATCHED_INTERLOCKED_ALARMS              = 15
    M_TIME_SINCE_ALARM_TRIGGERED              = 16
    M_ALARM_ACTIVATED                         = 14
    M_PD_OUT_PULSE_ACC_TIME                   = 17
    M_PD_CRI_PULSE_ACC_TIME                   = 18
    M_FSM_CURRENT_STATE                       = 19
    M_ANALOGIC_SPARE_KK0                      = 20
    M_ANALOGIC_SPARE_KK1                      = 21
    
    #VALUE
    SOFTWARE = 0
    DB25 = 1
    NONE = 2
    
    DIRECT_TRIG = 0
    INTENRAL = 1
    
    DCC = 0
    DPC = 1
    
    PD_OUT = 0
    PD_CRI = 1
    
    PULSED = 0 
    CW = 1
    
    POS_LOGIC = 0
    NEG_LOGIC = 1
    
    NO_MODE = 0
    PULSE_PICKER = 1
    HIGH = 2
    SYNC = 3
    
    PD_PULSE = 0
    INT_SMD2 = 1
    EXT_SMD2 = 2


    

    def __init__(self, port, address = -1):
      """
        Open serial device.
        :param dev: Serial device path. For instance '/dev/ttyUSB0' on linux, 'COM0' on Windows.
      """
      #Connection
      Aerodiode.__init__(self,port,address)

      #Alarm length = 11
      self.alarm_enable = dict(ALIM_VMAIN = 1, ALIM_HK = 1, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0)
      self.alarm_behavior1 = dict(ALIM_VMAIN = 1, ALIM_HK = 1, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0) #Interlock if alarm
      self.alarm_behavior2 = dict(ALIM_VMAIN = 1, ALIM_HK = 1, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0) #Disable 1s if alarm
      self.alarm_status = dict(ALIM_VMAIN = 1, ALIM_HK = 1, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0)
      self.alarm_history = dict(ALIM_VMAIN = 1, ALIM_HK = 1, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0)
      self.time_since_alarm_triggered = dict(ALIM_VMAIN = 0, ALIM_HK = 0, LASER_ALIGNEMENT = 0, T_SMD1 = 0, T_SMD2 = 0, MEAN_CURRENT_SMD2 = 0,
                               T_CASE = 0, BAD_START_SEQ = 0, CASE_OPEN = 0, EXT_SHUTDOWN = 0, PD_IN_LOW = 0)


    def read_alarm(self, alarm_id, alarm_dict, typ = 0):
      '''
         Read alarm
         :param alarm_id:
         :param alarm_dict: data dictionnary which contains the alarm data
         :param typ: Read Intruction(0)/Measure(1)
      '''
      
      if typ == 0: #read instruction
         alarm_status_bit = "{0:018b}".format(self.read_integer_instruction(alarm_id))[::-1] #str type
      else: #read measure
         alarm_status_bit = "{0:018b}".format(self.measure(alarm_id))[::-1] #str type

      #print("alarm_status_bit = ", alarm_status_bit)

      j = 0;
      for i in alarm_dict:
         alarm_dict[i] = alarm_status_bit[j]
         j += 1
      return alarm_dict;

    def set_alarm(self, alarm_id, alarm_dict):
      '''
         Set alarm instructions only
         :param alarm_id:
         :param alarm_dict: data dictionnary which contains the alarm data
      '''
      data = [0x00, alarm_id]
      value_int = 0
      cmp = 0
      for i in alarm_dict:
         value_int += int(alarm_dict[i])*2**cmp
         cmp += 1
      v = value_int.to_bytes(4, 'big') #U32 Conversion
      data.append(v[0]);data.append(v[1]);data.append(v[2]);data.append(v[3])#send U32 one by one
      return self.send_query(self._add, self.COMMAND_WRITE, data)
      
    #Watchdog
    def read_watchdog_pd_pulse_photo(self):
        res         = self.send_query(self._add, self.COMMAND_READ_INSTRUCTIONS, [0x00,  self.WATCHDOG_PD_PULSE_PHOTO])
        max_period  = res[0:4]
        min_period  = res[4:8]
        return  int.from_bytes(max_period,byteorder = 'big', signed=False),  int.from_bytes(min_period,byteorder = 'big', signed=False)

    #Alarm manadgement
    def read_alarm_enable(self):
        return self.read_alarm(self.ALARM_ACTIVATION, self.alarm_enable)

    def read_alarm_behavior1(self):
        return self.read_alarm(self.INTERLOCK_IF_ALARM, self.alarm_behavior1)

    def read_alarm_behavior2(self):
        return self.read_alarm(self.DISABLE_1S_IF_ALARM, self.alarm_behavior2)

    def read_alarm_history(self):
        return self.read_alarm(self.ALARM_HISTORY, self.alarm_behavior2)

    def read_alarm_status(self):
        return self.read_alarm(self.M_ALARM_ACTIVATED, self.alarm_status, 1)

    def set_alarm_enable(self):
        return self.set_alarm(self.ALARM_ACTIVATION, self.alarm_enable)

    def set_alarm_behavior1(self):
        return self.set_alarm(self.INTERLOCK_IF_ALARM, self.alarm_behavior1)

    def set_alarm_behavior2(self):
        return self.set_alarm(self.DISABLE_1S_IF_ALARM, self.alarm_behavior2)

    def set_alarm_history(self):
        return self.set_alarm(self.ALARM_HISTORY, self.alarm_behavior2)
    
    #Measure    
    def measure_main_v_mon(self):
        return self.measure(self.M_MAIN_V_MON, 1)

    def measure_hk_v_mon(self):
        return self.measure(self.M_HK_V_MON, 1)

    def measure_red_guide_v_mon(self):
        return self.measure(self.M_RED_GUIDE_VMON, 1)

    def measure_smd1_t(self):
        return self.measure(self.M_SMD1_T, 1)

    def measure_smd2_t(self):
        return self.measure(self.M_SMD2_T, 1)

    def measure_case_t(self):
        return self.measure(self.M_CASE_T, 1)

    def measure_smd1_current(self):
        return self.measure(self.M_SMD1_CURRENT, 1)

    def measure_pd_out_power(self):
        return self.measure(self.M_PD_OUT_POWER, 1)

    def measure_pd_bra_power(self):
        return self.measure(self.M_PD_BRA_POWER, 1)

    def measure_pd_in_cw_power(self):
        return self.measure(self.M_PD_IN_CW_POWER, 1)

    def measure_pd_inter_power(self):
        return self.measure(self.M_PD_INTER_POWER, 1)

    def measure_pd_cri_power(self):
        return self.measure(self.M_PD_CRI_POWER, 1)
        
    def measure_pd_in_pulse_frequency(self):
        return self.measure(self.M_PD_IN_PULSE_FREQUENCY)
        
    def measure_ext_sync_freq(self):
        return self.measure(self.M_EXTERNAL_SYNC_FREQUENCY)

    def measure_latched_interlocked_alarm(self):
        return self.measure(self.M_LATCHED_INTERLOCKED_ALARMS)

    def measure_time_alarm_since_alarm_triggered(self):
        table = self.send_query(self._add, self.COMMAND_READ_MEASURE, [0x00,  self.M_TIME_SINCE_ALARM_TRIGGERED])
        cmp = 0
        for i in self.time_since_alarm_triggered:
         self.time_since_alarm_triggered[i] = int.from_bytes(table[cmp:cmp+4], byteorder = 'big', signed=False)
         cmp += 1
        return self.time_since_alarm_triggered

    def measure_pd_out_pulse_acc_time(self):
        return self.measure(self.M_PD_OUT_PULSE_ACC_TIME, 1)

    def measure_pd_cri_pulse_acc_time(self):
        return self.measure(self.M_PD_CRI_PULSE_ACC_TIME, 1)

    def measure_fsm_current_state(self):
        return self.measure(self.M_FSM_CURRENT_STATE)

    def measure_analog_spare_kk0(self):
        return self.measure(self.M_ANALOGIC_SPARE_KK0, 1)

    def measure_analog_spare_kk1(self):
        return self.measure(self.M_ANALOGIC_SPARE_KK1, 1)
        

    


    
      
      


      
    
    
    
    
    
    
    
