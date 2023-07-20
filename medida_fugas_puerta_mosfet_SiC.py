import math
from time import sleep
from datetime import date, datetime

import matplotlib.colors
import matplotlib.pyplot as plt
import pyvisa


def init_instrument(resource_manager, resource_name, write_termination='\n', read_termination='\n'):
    instrument = resource_manager.open_resource(resource_name)
    instrument.write_termination = write_termination
    instrument.read_termination = read_termination
    print(instrument.query('*IDN?'), '\n')
    sleep(0.5)
    instrument.write('*RST')
    sleep(1)
    return instrument


def config_instrument_as_v_source_measure_i(instrument, voltage_range, voltage_level, i_compliance,
                                            i_range, i_nplc):
    instrument.write(":FORMat:ELEMents VOLTage, CURRent")
    instrument.write(":SOURce:FUNCtion:MODE VOLTage")
    instrument.write(":SOURce:VOLTage:MODE FIXed")
    instrument.write(":SOURce:VOLTage:RANGe " + str(voltage_range))
    instrument.write(":SOURce:VOLTage:LEVel " + str(voltage_level))
    instrument.write(":SENSe:FUNCtion 'CURRent'")
    instrument.write(":SENSe:CURRent:PROTection " + str(i_compliance))
    instrument.write(":SENSe:CURRent:RANGe " + str(i_range))
    instrument.write(":SENSe:CURRent:NPLCycles " + str(i_nplc))


def config_instrument_as_dc_volmeter(instrument, voltmeter_channels, voltage_range, nplc=10,
                                     a_zero=True):
    instrument.write(':ROUTe:CHANnel:OPEN:ALL')
    for voltmeter_channel in voltmeter_channels:
        voltmeter_channel_str = '(@' + str(voltmeter_channel) + ')'
        instrument.write(':SENS:FUNC "VOLTage:DC",' + str(voltmeter_channel_str))
        instrument.write('SENS:VOLTage:DC:NPLC ' + str(nplc) + ',' + str(voltmeter_channel_str))
        instrument.write(
            'SENS:VOLTage:DC:RANGE ' + str(voltage_range) + ',' + str(voltmeter_channel_str))
        if a_zero:
            instrument.write('SENS:VOLTage:DC:AZER ON,' + str(voltmeter_channel_str))
        else:
            instrument.write('SENS:VOLTage:DC:AZER OFF,' + str(voltmeter_channel_str))


def adjust_voltage_at_dut_gate(
        source_meter, voltmeter, voltmeter_channel, desired_voltage_at_gate,
        delay=0.5, max_source_meter_voltage=35.05, voltage_step=1E-3, max_delta_i=200E-6,
        i_compliance=1E-3):
    # Query voltage and current at the source_meter
    query_resp = source_meter.query("READ?")
    source_meter_voltage = float(query_resp.split(",")[0])
    source_meter_initial_current = float(query_resp.split(",")[1])
    if source_meter_initial_current > i_compliance:
        raise "Source_Meter current is above the compliance....Exiting"
    # Query voltage shunt at voltmeter channel
    voltmeter_channel_str = '(@' + str(voltmeter_channel) + ')'
    voltmeter.write(':ROUTe:CHANnel:CLOSe ' + voltmeter_channel_str)
    voltage_at_shunt = float(voltmeter.query("READ?"))  # read measurement
    voltage_at_gate = source_meter_voltage - voltage_at_shunt
    # print("voltage_at_gate: ", voltage_at_gate)
    # print("source_meter_voltage: ", source_meter_voltage)
    # print("voltage_at_shunt: ", voltage_at_shunt)
    new_source_meter_voltage = source_meter_voltage

    while not math.isclose(desired_voltage_at_gate, voltage_at_gate, abs_tol=0.001):
        # Adjust (increment) the source_meter voltage
        new_source_meter_voltage = new_source_meter_voltage + voltage_step
        source_meter.write(":SOURce:VOLTage:LEVel " + str(new_source_meter_voltage))
        # Query voltage and current at the source_meter
        query_resp = source_meter.query("READ?")
        source_meter_voltage = float(query_resp.split(",")[0])
        source_meter_current = float(query_resp.split(",")[1])
        if source_meter_voltage > max_source_meter_voltage:
            raise "Source_Meter Max voltage reached something went wrong....Exiting"
        if source_meter_current > i_compliance:
            raise "Source_Meter current is above the compliance....Exiting"
        if (source_meter_current - source_meter_initial_current) > max_delta_i:
            raise "Delta current is above the max delta....Exiting"
        source_meter_initial_current = source_meter_current
        # Query voltage shunt at voltmeter channel
        voltmeter_channel_str = '(@' + str(voltmeter_channel) + ')'
        voltmeter.write(':ROUTe:CHANnel:CLOSe ' + voltmeter_channel_str)
        voltage_at_shunt = float(voltmeter.query("READ?"))  # read measurement
        voltage_at_gate = source_meter_voltage - voltage_at_shunt
        # print("voltage_at_gate: ", voltage_at_gate)
        # print("source_meter_voltage: ", source_meter_voltage)
        # print("voltage_at_shunt: ", voltage_at_shunt)
        sleep(delay)


def main():
    # Experiment data#########################################
    output_data_file_name = "output1.txt"
    vcc = 35  # volts
    experiment_date = datetime.now()
    t_amb = 25  # celsius
    n_duts = 2  # max 10
    voltmeter_model = "DAQ6510_1"
    multiplexer_card_model = "K7700_4"
    source_meter_model = "K2400_4"
    first_channel = 101
    delay_between_measure_series = 1  # secs
    delay_between_measure_devices = 0.0  # secs
    delay_after_close_channel = 0.0  # secs
    plot_colors = ['red', 'green', 'blue', 'pink', 'brown', 'yellow', 'black', 'lime', 'violet', 'navy']
    ##########################################################
    n_measure_series = list()
    duts_references = [''] * n_duts
    r_shunts = [0] * n_duts  # Ohms
    current_at_shunts_evolution = [list() for i in range(n_duts)]  # Amps
    voltmeter_channels = [first_channel + n for n in range(n_duts)]
    # Init duts_references####################################
    duts_references_file_name = "duts_references.txt"
    with open(duts_references_file_name, 'r') as file:
        for i, r in enumerate(duts_references):
            duts_references[i] = str(file.readline()).removesuffix('\n')
    ##########################################################
    # Init r_shunts_values####################################
    r_shunts_file_name = "r_shunt_values.txt"
    with open(r_shunts_file_name, 'r') as file:
        for i, r in enumerate(r_shunts):
            r_shunts[i] = float(file.readline())
    ##########################################################
    rm = pyvisa.ResourceManager()
    # Init instruments########################################
    daq6510 = init_instrument(rm, 'TCPIP0::169.254.199.70::5025::SOCKET', '\n', '\n')
    k2400 = init_instrument(rm, 'ASRL5::INSTR', '\n', '\n')
    ##########################################################
    # Config the 2400 for V-Source, Measure-I#################
    config_instrument_as_v_source_measure_i(k2400, 200, 35, 10E-6, 10E-6, 10)
    ##########################################################
    # Config the DAQ6510 for measuring voltage at channels##
    config_instrument_as_dc_volmeter(daq6510, voltmeter_channels, 10E-3, nplc=12, a_zero=True)
    ##########################################################
    # config file to write the test###########################
    index = 0
    separator = ","
    header = "I_leakage test through a SiC Mosfets gate.\n"
    header += "Applied voltage: " + str(vcc) + "(V).\n"
    header += "Experiment date: " + str(experiment_date) + "\n"
    header += "Number of DUTS: " + str(n_duts) + ".\n"
    header += "TAmb: " + str(t_amb) + " celsius.\n"
    header += "Voltmeter model: " + voltmeter_model + ".\n"
    header += "Multiplexer Card model: " + multiplexer_card_model + ".\n"
    header += "Source Meter model: " + source_meter_model + ".\n"
    header += "First channel: " + str(first_channel) + ".\n"

    with open(output_data_file_name, 'w') as file:
        file.writelines(header)
        file.writelines("*" * 30 + "\n")
        file.writelines("index" + separator)
        for i, ref in enumerate(duts_references):
            if i == (len(duts_references) - 1):
                separator = ""
            file.writelines("i@" + ref + "(Amps)" + separator)
        file.writelines("\n")
    ##########################################################
    k2400.write(":OUTPut ON")
    # Adjust voltage at gate##################################
    adjust_voltage_at_dut_gate(k2400, daq6510, 101, 35)
    ##########################################################
    # Configure graph#########################################
    plt.autoscale(enable=True, axis='y')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.title("Mosfet leakage test over time")
    plt.ylabel("Leakage Current in Amps")
    plt.xlabel("Seconds")
    ##########################################################
    # MEASURE LOOP############################################
    n_measure = 1
    while True:
        separator = ","
        sleep(delay_between_measure_series)
        for index, voltmeter_channel in enumerate(voltmeter_channels):
            voltmeter_channel_str = '(@' + str(voltmeter_channel) + ')'
            sleep(delay_between_measure_devices)
            daq6510.write(':ROUTe:CHANnel:CLOSe ' + voltmeter_channel_str)
            sleep(delay_after_close_channel)
            voltage_at_shunt = float(daq6510.query("READ?"))  # read measurement
            current_at_shunt = voltage_at_shunt / r_shunts[index]
            with open(output_data_file_name, 'a') as file:
                if index == 0:
                    file.writelines(str(n_measure) + separator)
                if index == (len(voltmeter_channels) - 1):
                    separator = "\n"
                file.writelines(str(current_at_shunt) + separator)
            current_at_shunts_evolution[index].append(current_at_shunt)
            sleep(delay_between_measure_devices)
            # daq6510.write(':ROUTe:CHANnel:OPEN ' + voltmeter_channel_str)
        n_measure_series.append(n_measure)
        n_measure = n_measure + 1

        # Update graph########################################
        for i_color, currents in enumerate(current_at_shunts_evolution):
            plt.plot(n_measure_series, currents, color=plot_colors[i_color])
        plt.show(block=False)
        plt.pause(0.1)
        ######################################################
    ##########################################################


if __name__ == "__main__":
    main()
