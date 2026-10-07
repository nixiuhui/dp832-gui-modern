
#Install pyvisa: pip install pyvisa
import pyvisa as visa

class DP832(object):
    def __init__(self):
        pass

    def conn(self, constr="USB0::0x1AB1::0x0E11::DPXXXXXXXXXXX::INSTR"):
        """Attempt to connect to instrument"""
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(constr)
        self.inst.timeout = 5000

    def identify(self):
        """Return identify string which has serial number"""
        return self.inst.query("*IDN?")

    def readings(self, channel="CH1"):
        """Read voltage/current/power from CH1/CH2/CH3"""       
        resp = self.inst.query("MEAS:ALL? %s"%channel)
        resp = resp.split(',')
        dr = {"v":float(resp[0]), "i":float(resp[1]), "p":float(resp[2])}
        return dr

    def _ch_num(self, channel="CH1"):
        """Convert 'CH1'/'CH2'/'CH3' to instrument select number 1/2/3"""
        return int(str(channel).upper().replace("CH", "").strip())

    def select_channel(self, channel="CH1"):
        """Select the active channel for subsequent VOLT/CURR/PROT commands"""
        self.inst.write(":INST:NSEL %d" % self._ch_num(channel))

    def set_voltage(self, value, channel="CH1"):
        """Set output voltage (e.g. 24 for 24V) on the given channel"""
        self.select_channel(channel)
        self.inst.write(":VOLT %s" % value)

    def set_current(self, value, channel="CH1"):
        """Set constant-current limit (e.g. 0.2 for 0.2A) on the given channel"""
        self.select_channel(channel)
        self.inst.write(":CURR %s" % value)

    def set_ocp(self, enabled, level=None, channel="CH1"):
        """Enable/disable Over-Current Protection. When enabled and the output
        current exceeds the level, the supply cuts off its output.
        level: trip current in Amps (defaults to device's current setting)."""
        self.select_channel(channel)
        if level is not None:
            self.inst.write(":CURR:PROT:LEV %s" % level)
        self.inst.write(":CURR:PROT:STAT %s" % ("ON" if enabled else "OFF"))

    def clear_protection(self, channel="CH1"):
        """Clear a tripped OCP state so the output can be re-enabled"""
        self.select_channel(channel)
        self.inst.write(":CURR:PROT:CLE")

    def dis(self):
        del self.inst

    def writing(self, command=""):
        self.inst.write(command)
        
if __name__ == '__main__':
    test = DP832()

    #Insert your serial number here / confirm via Ultra Sigma GUI
    test.conn("USB0::0x1AB1::0x0E11::DPXXXXXXXXXXX::INSTR")
    
    print(test.readings())
