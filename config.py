### Caution: Python is sensitive for indentation. Do use "Space" insted of "Tab".

dV = 50 # (V) Minimum volgage step, which must be a dvisor for holding voltages.
dt_meas = 1 #(s) measurement interval
dt_op = 1 # (s) time per step for Ve change


# List of [Voltage (V), holding time(s)]
DT = 300 # (s) time per step for time-dependence measurement
SEQ = [[3000, DT],\
        [3250, DT],\
        [3500, DT],\
        [3750, DT],\
        [4000, DT],\
        [4250, DT],\
        [4500, DT],\
        [4750, DT],\
        [5000, 3600]]
