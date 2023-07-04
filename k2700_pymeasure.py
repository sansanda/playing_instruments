from pymeasure.instruments.keithley import Keithley2700


def main():
    keithley = Keithley2700("GPIB::1")


if __name__ == "__main__":
    main()
