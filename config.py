### Caution: Python is sensitive for indentation. Do use "Space" insted of "Tab".

dV = 50 # (V) Minimum volgage step, which must be a dvisor for holding voltages.
dt_meas = 1 #(s) measurement interval
dt_op = 1 # (s) time per step for Ve change


# List of [Voltage (V), holding time(s)]
DT = 1800 # (s) time per step for time-dependence measurement
SEQ = [[5000, 360000]]    
# SEQ = [[2000, DT],\
#         [2100, DT],\
#         [2200, DT],\
#         [2300, DT],\
#         [2400, DT],\
#         [2500, DT],\
#         [2600, DT],\
#         [2700, DT],\
#         [2800, DT],\
#         [2900, DT],\
#         [3000, DT],\
#         [3100, DT],\
#         [3200, DT],\
#         [3300, DT],\
#         [3400, DT],\
#         [3500, DT],\
#         [3600, DT],\
#         [3700, DT],\
#         [3800, DT],\
#         [3900, DT],\
#         [4000, DT],\
#         [4100, DT],\
#         [4200, DT],\
#         [4300, DT],\
#         [4400, DT],\
#         [4500, DT],\
#         [4600, DT],\
#         [4700, DT],\
#         [4800, DT],\
#         [4900, DT],\
#         [5000, 360000]]
