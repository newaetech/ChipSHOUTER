'''
    Shouter_API will allow you to connect / get options / set options

    The High voltage pulses can be up to 500 volts and triggered at as low as 20ns.
    The Unit needs to be armed before any triggering of the high voltage by the user.

    The Unit can be Armed by:

    1. User pressing the Arm button.
    2. User sending the arm command through the computer.
    3. User toggling the enable IO on the DB9 Connector. (Unit configuration must have this enabled)

    The voltage and timing are configurable through the computer interface. This give the user the ability
    to fine tune the device to find the optimum settings to corrupt the target.

    Example
    =======
    Below is an example of arming / pulse and then disarm.

    >>> import time
    >>> from shouter.shouter_api import Shouter_API
    >>>
    >>> s = Shouter_API()
    >>> s.ctl_connect('COM10')
    >>> # Arming
    >>> s.cmd_arm()
    >>> time.sleep(3)
    >>> # Trigger
    >>> s.cmd_pulse()
    >>> # Disarm
    >>> s.cmd_disarm()
    >>> # Disconnect
    >>> s.ctl_disconnect()
    >>> # Done

'''
from collections import OrderedDict
#from shouter_api import Shouter_API
from com_tools import Bin_API

class DisableNewAttr(object):
    """Provides an ability to disable setting new attributes in a class, useful to prevent typos.

    Usage:
    1. Make a class that inherits this class:
    >>> class MyClass(DisableNewAttr):
    >>>     # Your class definition here

    2. After setting up all attributes that your object needs, call disable_newattr():
    >>>     def __init__(self):
    >>>         self.my_attr = 123
    >>>         self.disable_newattr()

    3. Subclasses raise an AttributeError when trying to make a new attribute:
    >>> obj = MyClass()
    >>> #obj.my_new_attr = 456   <-- Raises AttributeError

    """

    def __init__(self):
        self.disable_newattr()

    def disable_newattr(self):
        self._new_attributes_disabled = True

    def __does_attr_exist(self, obj, var):
        y = getattr(obj, var, None)
        if y is not None:
            return True
        else:
            return False

    def enable_newattr(self):
        self._new_attributes_disabled = False

    def __setattr__(self, name, value):
        if hasattr(self, '_new_attributes_disabled') and self._new_attributes_disabled and not hasattr(self, name):  # would this create a new attribute?
            raise AttributeError("Attempt to set unknown attribute in %s"%self.__class__, name)
        super(DisableNewAttr, self).__setattr__(name, value)

#-----------------------------------------------------------------------------------------
# Below is another way of catching the attribute error without throwing away the exception
# - Does not work wit type of 'None' it assumes that it means it does not exist.
#-----------------------------------------------------------------------------------------
#    def __setattr__(self, name, value):
#        if self.__does_attr_exist(self, '_new_attributes_disabled') and self._new_attributes_disabled and not self.__does_attr_exist(self, name):  # would this create a new attribute?
#            raise AttributeError("Attempt to set unknown attribute in %s"%self.__class__, name)
#        super(DisableNewAttr, self).__setattr__(name, value)


def dict_to_str(input_dict, indent=""):
    """Turn a dictionary of attributes/status values into a pretty-printed
    string for use on the command line. Recursively pretty-prints dictionaries.

    This function is most useful with OrderedDicts as it keeps the same
    printing order.

    """

    # Find minimum width that fits all names
    min_width = 0
    for n in input_dict:
        min_width = max(min_width, len(str(n)))

    # Build string
    ret = ""
    for n in input_dict:
        if type(input_dict[n]) in (dict, OrderedDict):
            ret += indent + str(n) + ' = '
            ret += '\n' + dict_to_str(input_dict[n], indent+"    ")
        else:
            ret += indent + str(n).ljust(min_width) + ' = '
            ret += str(input_dict[n]) + '\n'

    return ret


class VoltageSettings(DisableNewAttr):

    def __init__(self, api):
        self.api = api
        self.disable_newattr()

    @property
    def set(self):
        """Requested capacitor bank voltage"""
        rval = self.api.get_voltage(5)
        return rval

    @set.setter
    def set(self, volt):
        rval = self.api.set_voltage(volt, 5)
        return rval

    @property
    def measured(self):
        """Measured capacitor bank voltage"""

        rval = self.api.get_voltage_measured(5)
        return rval

    def _dict_repr(self):
        dict = OrderedDict()
        dict['set'] = self.set
        dict['measured'] = self.measured
        return dict

    def __repr__(self):
        return dict_to_str(self._dict_repr())

    def __str__(self):
        return self.__repr__()


class PulseSettings(DisableNewAttr):
    """
    Pulse settings:

    """
    def __init__(self, api):
        self.api = api
        self.disable_newattr()

    @property
    def set(self):
        """Requested to see if the unit is pulsing. """
        rval = self.api.get_voltage(5)
        return rval

    @set.setter
    def set(self, state):
        """ Pulse the unit if the state is True """
        if state:
            self.api.cmd_pulse()

    @property
    def width(self):
        """ Width of the pulse"""
        rval = self.api.get_pulse_width(5)
        return rval

    @width.setter
    def width(self, width):
        rval = self.api.set_pulse_width(width)
        return rval

    @property
    def repeat(self):
        """This is amazing"""
        rval = self.api.get_pulse_repeat(5)
        return rval

    @property
    def measured(self):
        """ Get the Measured pulse width """

        rval = self.api.get_pulse_width_measured(1)
        return rval

    @repeat.setter
    def repeat(self, repeat):
        print 'Setting repeat!!'
        rval = self.api.set_pulse_repeat(repeat)
        return repeat

    @property
    def deadtime(self):
        """ Get the deadtime """
        rval = self.api.get_pulse_deadtime(5)
        return rval

    @deadtime.setter
    def deadtime(self, deadtime):
        #self.api.dosomething(repeat)
        rval = self.api.set_pulse_deadtime(deadtime)
        return rval

    def _dict_repr(self):
        dict = OrderedDict()
        dict['width']        = self.width
        dict['repeat']       = self.repeat
        dict['deadtime']     = self.deadtime
        dict['actual width'] = self.measured
        return dict

    def __repr__(self):
        return dict_to_str(self._dict_repr())

    def __str__(self):
        return self.__repr__()

class ChipSHOUTER(DisableNewAttr):
    """
    ChipSHOUTER object.

    The ChipSHOUTER will attempt to connect when initialzed.
    This Object will contain all the status of the chipshouter connected.
    You will be able probe for status and control the status of the shouter.

    :param comport: (String): The serial port that the ChipShouter is 
                              connected.

    """
    _name = "ChipSHOUTER"

    def __init__(self, comport):
        self.com_api = Bin_API('COM10')
        self.com_api.refresh()
        self.__connected = True

        #Example where we have multiple subsettings
        self._pulse = PulseSettings(self.com_api)

        #_voltage is used as this will be an odd example
        self._voltage = VoltageSettings(self.com_api)

        self.disable_newattr()

    def status(self):
        """ This will indicate the status of the connection to the chipshouter.

        :returns:    (bool):   True if connected successfully. False if not.

        """
        return self.__connected

    def disconnect(self):
        """ This will disconnect the connection from the chipshouter.

        :returns: (bool):  Status of the connection, True if connected 
                           successfully. False if not.

        """

        self.com_api.ctl_disconnect()

    #The following shows an "asymetric" setter, where we want to
    #make 'set' call some specific function
    @property
    def voltage(self):
        """ Sets the voltage or reads the voltage

        :param voltage: (int): The voltage level you wish to set.
                               *Note* This is between 150 and 500 Volts

        :returns: This will return both members of the voltage: set and measured.

        :Member: .set - This is the voltage that is targeted to be set.

            :returns: The set voltage

        :Member (Read only): .measured - This is the actual voltage that is
            put out of the chip shouter.

            :returns: The measured voltage

        :Example:

            >>> from API import ChipSHOUTER
            >>> cs = ChipSHOUTER('COM10')
            Serial Interface Started
            Shouter API Started
            >>> cs.voltage
            set      = 200
            measured = 209
            >>> cs.voltage.set
            200
            >>> cs.voltage.measured
            210
            >>>
            >>> cs.voltage = 300
            >>> cs.voltage
            set      = 300
            measured = 298

        """
        return self._voltage


    @voltage.setter
    def voltage(self, voltage):
        self._voltage.set = voltage
        return voltage

    @property
    def pulse(self):
        return self._pulse

    @pulse.setter
    def pulse(self, state):
        self._pulse.set = state 

    @property
    def faults_current(self):
        """
        This will get the current faults that are on the system.

        :Returns (list):  This will return a list of dictionaries containing
                          the list of faults. The list will be empty if none
                          exist.
        :param fault: (int): When 0 it will attempt to clear the faults.
                             Clearing the faults is need in order to arm after
                             a fault has occured during the arm period.

        :Types:
            - **probe**       - Probe connection is not connected properly.
            - **overtemp**    - One of the temperature sensors has gone over 90C
                                **Note:** *This will not recover until temperature
                                goes below 75C.*
            - **open**        - The case is open.
            - **highv**       - The high voltage circuit is off by way too much. 
            - **ramcrc**      - Noise has corrupted some internal ram of the shouter.
            - **eecrc**       - Noise has corrupted some internal eeprom of the shouter.
            - **gpio**        - Noise has corrupted some internal gpio registers.
            - **charge**      - Some faults with the high voltage circuitry.  
            - **trigger**     - Trigger occured while disarmed.
                            Trigger for too long (More than 10msec)
            - **hw**          - Hardware monitor detected faulty hardware.
            - **trig_g**      - Trigger has been glitched
            - **overvoltage** - Hardware reported overvoltage on charging. 
            - **temp_sensor** - Problems reading temperature sensor.

        :Example:
            >>> cs = ChipSHOUTER('COM10')     # Connect to shouter
            Serial Interface Started
            Shouter API Started
            >>> cs.state                      # Check the state of the shouter.
            'disarmed'
            >>> cs.armed = 1                  # Arm the shouter.
            >>> cs.state
            'armed'
            >>> cs.state                      # Cause fault... and check state.
            'fault'
            >>> cs.faults_current             # List the faults.
            [{'fault': 1, 'name': 'probe'}]
            >>> cs.faults_current = 0         # After fault fixed, Clear it.
            >>> cs.state                      # Check the state
            'disarmed'
            >>> 
        
        """
        return self.com_api.get_faults_current()

    @faults_current.setter
    def faults_current(self, value):
        if value == 0:
            self.com_api.cmd_clear_faults()

        return self.com_api.get_faults_current()

    @property
    def faults_latched(self):
        """
        This will get the latched faults that had occured on the system.
        An example of needing the finding issues when a fault occured for a
        short period of time, and is cleared by the time you look at the current
        faults.

        More information is documented with faults_current.

        :Returns (list):  This will return a list of dictionaries containing
                          the list of faults. The list will be empty if none
                          exist.
        :Example:
            >>> cs = ChipSHOUTER('COM10')     # Connect to shouter
            Serial Interface Started
            Shouter API Started
            >>> cs.state                      # Check the state of the shouter.
            'disarmed'                        # I heard an error tone 
            cs.faults_current                 # What was it???
            []                                # Funny nothing wrong here.
            >>> cs.faults_latched             # Anything latched???
            [{'fault': 1, 'name': 'trigger'}, {'fault': 1, 'name': 'trig_g'}]
            >>>                               # Ahhhh... flakey trigger.
        
        """
        return self.com_api.get_faults_latched()

    @property
    def state(self):
        rval = self.com_api.get_state(timeout = 3)
        return rval

    @property
    def trigger_safe(self):
        """
        This will let you know if it is safe to trigger. 
        If this is read and the system is safe it will allow triggering for 5 seconds
        without checking the temperature. External triggers without calling this first
        are not guaranteed to be successful. The unit could have a fault and abort triggering. 

        :Returns (bool): - True to indicat that it is safe to trigger. 
                         - False if the system is not armed or in fault.
                         
        """
        rval = self.com_api.get_trigger_safe(3)
            
        if(rval):
            return True
        else:
            return False

    @property
    def clr_armed(self):
        """
        This is the control of the armed status.

        :Returns (bool): - When read it will show True when armed, False if not. 

        :param state (bool): Attempt to arm when True is passed in.
                             Attempt to disarm when False is passed in.

        """
        state = self.com_api.get_state(3)
            
        if(state == 'armed'):
            return True
        else:
            return False

    @clr_armed.setter
    def clr_armed(self, status):
        if status:
            self.com_api.cmd_clear_arm()
        else:
            self.com_api.cmd_disarm()
        return status
    @property
    def armed(self):
        """
        This is the control of the armed status.

        :Returns (bool): - When read it will show True when armed, False if not. 

        :param state (bool): Attempt to arm when True is passed in.
                             Attempt to disarm when False is passed in.

        """
        state = self.com_api.get_state(3)
            
        if(state == 'armed'):
            return True
        else:
            return False

    @armed.setter
    def armed(self, status):
        if status:
            self.com_api.cmd_arm()
        else:
            self.com_api.cmd_disarm()
        return status

    @property
    def temperature_mosfet(self):
        """
        Read the temperature of the mosfet.
        """
        return self.com_api.get_temperature_mosfet()

    @property
    def temperature_diode(self):
        """
        Read the temperature of the diode.

        :Returns (int): temperature
        """
        return self.com_api.get_temperature_diode()

    @property
    def temperature_xformer(self):
        """
        Read the temperature of the Transformer.

        :Returns (int): temperature
        """
        return self.com_api.get_temperature_xformer()

    @property
    def id(self):
        """
        Read the board id. 

        :Returns (string): The string id of the Chip shouter. 
        """
        return self.com_api.get_id()

    @property
    def arm_timeout(self):
        """ Arm timeout 
        Because of safty reasons we will monitor the trigger when in the armed
        state. The trigger needs to be activated within the timeout programmed.
        Every trigger will reset the timer with every pulse.

        If the time out occurs, the shouter will disarm and disable the high
        voltage circuitry.

        The Arm timer will be reset on every trigger / internal or external.

        **NOTE** Valid range is between 1 - 60 minutes

        :param state: (int): time in minutes for the timeout. 

        :Returns (int): The arm timeout without triggering. 

        """
        return self.com_api.get_arm_timeout()

    @arm_timeout.setter
    def arm_timeout(self, value):
        """ Arm timeout setter """
        return self.com_api.set_arm_timeout(value)

    @property
    def hwtrig_term(self):
        return self.com_api.get_hwtrig_term()

    @hwtrig_term.setter
    def hwtrig_term(self, value):
        return self.com_api.set_hwtrig_term(value)

    @property
    def hwtrig_mode(self):
        return self.com_api.get_hwtrig_mode()

    @hwtrig_mode.setter
    def hwtrig_mode(self, value):
        return self.com_api.set_hwtrig_mode(value)

    @property
    def emode(self):
        """
        emode when set will enable the external arming of the system through
        the external IO.

        When the external IO is set to high it will attempt arm the system.
            **Note:**
            * The system may not be armed because of a fault.*
            * The status Led on the connector will indicate the arm status.*

        When the external IO is set to low it will disarm the system.

        The External IO reacts to the state change and not the static state.
        If the System fails to arm, to attempt again it needs to pull the line
        low and then high once again.

        :param state: (bool): True to enable False to disable. 

        :Returns: The state of the emode. 

        """
        return self.com_api.get_emode()

    @emode.setter
    def emode(self, value):
        return self.com_api.set_emode(value)

    @property
    def mute(self):
        """ mute when enabled will not give audio notification of the state or
        fault status. It is totally quiet.

        :param state: (bool): True to enable False to disable. 
        """
        return self.com_api.get_mute()

    @mute.setter
    def mute(self, value):
        return self.com_api.set_mute(value)

    @property
    def absentTemp(self):
        return self.com_api.get_absentTemp()

    @absentTemp.setter
    def absentTemp(self, value):
        return self.com_api.set_absentTemp(value)

    @property
    def pat_enable(self):
        return self.com_api.get_pat_enable()

    @pat_enable.setter
    def pat_enable(self, value):
        return self.com_api.set_pat_enable(value)

    @property
    def pat_wave(self):
        return self.com_api.get_pat_wave()

    @pat_wave.setter
    def pat_wave(self, value):
        return self.com_api.set_pat_wave(value)

    @property
    def reset(self):
        return 0
    @reset.setter
    def reset(self, value):
        if value:
            self.com_api.cmd_reset()
        return

    @property
    def boot_enable(self):
        return 0

    @boot_enable.setter
    def boot_enable(self, value):
        if value:
            self.com_api.set_boot_bits(0)
        return

    @property
    def reset_config(self):
        return 0

    @reset_config.setter
    def reset_config(self, value):
        if self.state == 'armed':
            raise ValueError('Error Cannot default when armed.') 
        if value:
            self.com_api.cmd_default_options()
        return

    @property
    def board_id(self):
        return self.com_api.get_board_id()

    def _dict_repr(self):
        dict = OrderedDict()
        dict['armed']               = self.armed
        dict['voltage']             = self.voltage._dict_repr()
        dict['pulse']               = self.pulse._dict_repr()
        dict['state']               = self.state
        dict['faults_current']      = self.faults_current
        dict['faults_latched']      = self.faults_latched
        dict['temperature_mosfet']  = self.temperature_mosfet
        dict['temperature_diode']   = self.temperature_diode
        dict['temperature_xformer'] = self.temperature_xformer

        dict['arm_timeout']         = self.arm_timeout
        dict['hwtrig_term']         = self.hwtrig_term
        dict['hwtrig_mode']         = self.hwtrig_mode
        dict['emode']               = self.emode
        dict['mute']                = self.mute

        dict['absentTemp']          = self.absentTemp
        dict['pat_enable']          = self.pat_enable
        dict['pat_wave']            = self.pat_wave
        dict['reset_config']        = self.reset_config
        dict['reset']               = self.reset
        dict['board_id']            = self.board_id
        dict['boot_enable']         = self.boot_enable
        return dict

    def __repr__(self):
        # Add some extra information about ChipWhisperer type here
        if self.__connected:
            return dict_to_str(self._dict_repr())
        else:
            ret = "ChipSHOUTER is not connected"
            return ret

    def __str__(self):
        return self.__repr__()

def main():
    import time
    """ This is the main entry for the console."""
    cs = ChipSHOUTER('COM10')
    print cs.status()
    print cs.voltage
    print 'Arming!'
    cs.armed = True
    print cs.voltage.set
    print cs.voltage.measured
    cs.armed = False 

#    if cs.status():
#        print cs.voltage
#        print '-'*40
#        print cs.voltage.set
#        print cs.voltage.measured
#
#        cs.voltage.set = 205
#        print 'And... ' + str(cs.voltage)
#        cs.voltage = 206
#        print cs.voltage.set
#        print cs.voltage
#    time.sleep(1)
    cs.disconnect()

################################################################################
if __name__ == "__main__":
    main()
