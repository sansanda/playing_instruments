from time import sleep

import pyvisa

from pymeasure.instruments.keithley import Keithley2700


def main():
    # k6510 = Keithley2700("TCPIP0::169.254.199.70::inst0::INSTR",
    #                      write_termination="\n",
    #                      read_termination="\n")
    # k6510.beep(1000, 1)

    rm = pyvisa.ResourceManager()
    myDAQ6510 = rm.open_resource('TCPIP0::169.254.199.70::5025::SOCKET')
    myDAQ6510.write_termination = '\n'
    myDAQ6510.read_termination = '\n'
    current_channel = "(@122)"
    voltage_channel_12 = "(@112)"
    myDAQ6510.write('*RST')
    sleep(1)
    myDAQ6510.write(':ROUTe:CHANnel:OPEN:ALL')
    sleep(1)
    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + current_channel)
    sleep(1)
    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + voltage_channel_12)
    sleep(1.0)

if __name__ == "__main__":
    main()
