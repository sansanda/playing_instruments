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
    voltage_channel_13 = "(@113)"
    voltage_channel_14 = "(@114)"
    voltage_channel_15 = "(@115)"
    voltage_channel_16 = "(@116)"

    print(myDAQ6510.query('*IDN?'))
    myDAQ6510.write('*RST')
    sleep(1)
    myDAQ6510.write(':ROUTe:CHANnel:OPEN:ALL')
    sleep(1)

    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + current_channel)
    sleep(1)

    myDAQ6510.write(':SENS:FUNC "CURRent:DC",' + current_channel)
    myDAQ6510.write('CURR:NPLC 10,' + current_channel)
    myDAQ6510.write('CURR:RANGE 1E-3,' + current_channel)
    myDAQ6510.write('CURR:AZER OFF,' + current_channel)

    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + voltage_channel_12)
    sleep(0.2)
    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe (@124)')
    sleep(1)

    current = float(myDAQ6510.query('READ?'))  # read measurement
    print(current)
    sleep(1)

    myDAQ6510.write(':SENS:FUNC "VOLTage:DC",' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:NPLC 10,' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:RANGE 1E+2,' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:AZER OFF,' + voltage_channel_12)

    # voltage = 0
    # voltage = float(myDAQ6510.query('READ?'))  # read measurement
    # print(voltage)
    # sleep(1)

if __name__ == "__main__":
    main()
