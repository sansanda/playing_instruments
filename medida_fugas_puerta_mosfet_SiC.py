from time import sleep

import pyvisa

from pymeasure.instruments.keithley import Keithley2700


def main():
    # k6510 = Keithley2700("TCPIP0::169.254.199.70::inst0::INSTR",
    #                      write_termination="\n",
    #                      read_termination="\n")
    # k6510.beep(1000, 1)

    r_shunt = 1430.155  # Ohms
    vcc = 35  # volts

    rm = pyvisa.ResourceManager()

    myDAQ6510 = rm.open_resource('TCPIP0::169.254.199.70::5025::SOCKET')
    my2400 = rm.open_resource('GPIB0::24::INSTR')

    myDAQ6510.write_termination = '\n'
    myDAQ6510.read_termination = '\n'
    my2400.write_termination = '\n'
    my2400.read_termination = '\n'

    print(myDAQ6510.query('*IDN?'))
    myDAQ6510.write('*RST')
    sleep(1)

    print(my2400.query('*IDN?'))
    my2400.write('*RST')
    sleep(1)

    current_at_2400 = float()
    voltage_at_shunt = float()
    current_at_shunt = float()
    index = 1

    # Config the 2400 for V-Source, Measure-I
    my2400.write(":FORMat:ELEMents CURRent")
    my2400.write(":SOURce:FUNCtion:MODE VOLTage")
    my2400.write(":SOURce:VOLTage:MODE FIXed")
    my2400.write(":SOURce:VOLTage:RANGe 200")
    my2400.write(":SOURce:VOLTage:LEVel 35")
    my2400.write(":SENSe:FUNCtion 'CURRent'")
    my2400.write(":SENSe:CURRent:PROTection 10E-6")
    my2400.write(":SENSe:CURRent:RANGe 10E-6")
    my2400.write(":SENSe:CURRent:NPLCycles 10")
    my2400.write(":OUTPut ON")

    # Config the DAQ6510 for measuring voltage at channel 12
    voltage_channel_12 = "(@112)"
    myDAQ6510.write(':ROUTe:CHANnel:OPEN:ALL')
    sleep(1)
    myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + voltage_channel_12)
    sleep(1.0)
    myDAQ6510.write(':SENS:FUNC "VOLTage:DC",' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:NPLC 12,' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:RANGE 100E-3,' + voltage_channel_12)
    myDAQ6510.write('SENS:VOLTage:DC:AZER OFF,' + voltage_channel_12)

    # config file to write the test
    file_name = "test1.txt"
    separator = ","
    with open(file_name, 'w') as file:
        file.writelines(
            "Test for simulating the i_leakage through a SiC Mosfet gate.\n")
        file.writelines(
            "Applied 35v to a series resistor circuit with 1430.155 Ohms shunt and a 10M resistor.\n")
        file.writelines("index" + separator +
                        "i_2400 (Amps)" + separator +
                        "i_at_shunt (Amps)\n")

    while True:
        voltage_at_shunt = float(myDAQ6510.query('READ?'))  # read measurement
        current_at_shunt = voltage_at_shunt / r_shunt
        current_at_2400 = my2400.query(':READ?')
        print("current_at_2400: ", current_at_2400, " Amps")
        print("current_at_shunt: ", current_at_shunt, " Amps")
        sleep(1.0)
        with open(file_name, 'a') as file:
            file.writelines(str(index) + separator +
                            str(current_at_2400) + separator +
                            str(current_at_shunt) + "\n")
        index = index + 1

    # current_channel = "(@122)"
    # voltage_channel_12 = "(@112)"
    # voltage_channel_13 = "(@113)"
    # voltage_channel_14 = "(@114)"
    # voltage_channel_15 = "(@115)"
    # voltage_channel_16 = "(@116)"
    #
    #
    #
    # myDAQ6510.write(':ROUTe:CHANnel:OPEN:ALL')
    # sleep(1)
    # myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + current_channel)
    # sleep(1)
    # myDAQ6510.write(':SENS:FUNC "CURRent:DC",' + current_channel)
    # myDAQ6510.write('CURR:NPLC 10,' + current_channel)
    # myDAQ6510.write('CURR:RANGE 1E-3,' + current_channel)
    # myDAQ6510.write('CURR:AZER OFF,' + current_channel)
    #
    # current = float(myDAQ6510.query('READ?'))  # read measurement
    # print(current)
    # sleep(1)
    #
    #
    # myDAQ6510.write(':ROUTe:CHANnel:MULTiple:CLOSe ' + voltage_channel_12)
    # sleep(1.0)
    # myDAQ6510.write(':SENS:FUNC "VOLTage:DC",' + voltage_channel_12)
    # myDAQ6510.write('SENS:VOLTage:DC:NPLC 10,' + voltage_channel_12)
    # myDAQ6510.write('SENS:VOLTage:DC:RANGE 1E+2,' + voltage_channel_12)
    # myDAQ6510.write('SENS:VOLTage:DC:AZER OFF,' + voltage_channel_12)
    # voltage = float(myDAQ6510.query('READ?'))  # read measurement
    # print(voltage)
    # sleep(1)


if __name__ == "__main__":
    main()
