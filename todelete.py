from datetime import date


def main():

    # Experiment data#########################################
    vcc = 35  # volts
    experiment_date = date(2023, 7, 18)
    t_amb = 25  # celsius
    n_duts = 7
    volmeter_model = "DAQ6510_2"
    source_meter_model = "K2400_4"
    first_channel = 101
    ##########################################################

    r_shunts = [0] * n_duts  # Ohms
    v_shunts = [0] * n_duts  # Volts
    i_shunts = [0] * n_duts  # Amps
    voltmeter_channels = [first_channel + n for n in range(n_duts)]

    # Init r_shunts_values####################################
    r_shunts_file_name = "r_shunt_values.txt"
    with open(r_shunts_file_name, 'r') as file:
        for i, r in enumerate(r_shunts):
            r_shunts[i] = float(file.readline())
    ##########################################################

    print(r_shunts)


if __name__ == "__main__":
    main()
