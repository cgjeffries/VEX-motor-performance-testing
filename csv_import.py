import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# kilogram square meter
WHEEL_MOI = 0.0241857894

TICKS_PER_REV = 8192
MICROSECONDS_PER_MINUTE = 60 * 1_000_000


if False:
    MOTOR_TYPE = "11w blue"
    NUM_MOTORS = 1
    X_AXIS_SCALE = 1.0
    df = pd.read_csv('new_encoder_new_psu.csv')
else:
    MOTOR_TYPE = "5.5w"
    NUM_MOTORS = 2
    X_AXIS_SCALE = 0.75
    df = pd.read_csv('output_5.5w.csv')


VELOCITY_X_AXIS = "percentage"
# VELOCITY_X_AXIS = "absolute"


# Compute differences
df['delta_time_us'] = df['time_us'].diff()
df['delta_ticks'] = df['encoder_value'].diff()
df = df.dropna()

# Compute RPM
df['revolutions'] = df['delta_ticks'] / TICKS_PER_REV
df['delta_time_min'] = df['delta_time_us'] / MICROSECONDS_PER_MINUTE
df['rpm'] = df['revolutions'] / df['delta_time_min']



x = df['time_us'].to_numpy()/1000000.0

y = df['rpm'].to_numpy() * (2*np.pi)/60

y_savgol = savgol_filter(y, 40, 3)

# current = df['current'].to_numpy()/1000

# current_savgol = savgol_filter(current, 100, 3)

velocity_poly = np.polyfit(x, y, 6)

print(f'velocity coefficients: {velocity_poly}')

acceleration_poly = np.polyder(velocity_poly)

acceleration_gradient = np.gradient(y_savgol)/0.01
acceleration_gradient_savgol = savgol_filter(acceleration_gradient, 200, 3)

#multiply by number of motors TODO: change this as needed
acceleration_gradient_savgol = acceleration_gradient_savgol * NUM_MOTORS

print(f'acceleration coefficients: {acceleration_poly}')

# Create polynomial function
p1 = np.poly1d(velocity_poly)

p2 = np.poly1d(acceleration_poly)

def torque(x):
    return acceleration_gradient_savgol[int(x*100)] * WHEEL_MOI
    # return acceleration_gradient[int(x*100)]



torque_fun = np.vectorize(torque)

plt.scatter(x, y, label='rad/s vs time', s=1)
plt.scatter(x, y_savgol, color='red', label='y_savgol', s=1)
# plt.plot(x, p1(x), label='Polynomial Fit', color='red')
# plt.twinx().plot(x, p2(x), label='Acceleration', color='green')
plt.twinx().plot(x, acceleration_gradient_savgol, label='Acceleration gradient', color='green')
plt.legend()
# plt.xlim(0,5)
plt.show()

plt.figure(2)
fig, ax1 = plt.subplots()
fig.set_size_inches(8, 5)
ax1.set_title(f'{NUM_MOTORS}x {MOTOR_TYPE}')
if MOTOR_TYPE == "11w blue":
    if VELOCITY_X_AXIS == "percentage":
        ax1.scatter(y_savgol*60/(2*np.pi)/6 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI, color='blue', label='Torque(Nm) (blue cart)', s=1)
        ax1.scatter(y_savgol*60/(2*np.pi)/6 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI*6, color='orange', label='Torque(Nm) (simulated red cart)', s=1)
        ax1.scatter(y_savgol*60/(2*np.pi)/6 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI*3, color='green', label='Torque(Nm) (simulated green cart)', s=1)
    elif VELOCITY_X_AXIS == "absolute":
        ax1.scatter(y_savgol * 60 / (2 * np.pi) / 1 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI, color='blue',
                    label='Torque(Nm) (blue cart)', s=1)
        ax1.scatter(y_savgol * 60 / (2 * np.pi) / 1 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI * 6, color='orange',
                    label='Torque(Nm) (simulated red cart)', s=1)
        ax1.scatter(y_savgol*60/(2*np.pi)/1 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI*2, color='green', label='Torque(Nm) (simulated green cart)', s=1)

elif MOTOR_TYPE == "5.5w":
    if VELOCITY_X_AXIS == "percentage":
        ax1.scatter(y_savgol * 60 / (2 * np.pi) / 2 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI, color='blue', label='Torque(Nm)', s=1)
    elif VELOCITY_X_AXIS == "absolute":
        ax1.scatter(y_savgol * 60 / (2 * np.pi) / 1 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI, color='blue', label='Torque(Nm)', s=1)
# ax1.scatter(y_savgol*60/(2*np.pi)/6, current_savgol, color='green', label='Current (mA)', s=1)

if VELOCITY_X_AXIS == "percentage":
    ax1.set_xlabel('%max velocity')
    ax1.set_xlim(0, 160)
elif VELOCITY_X_AXIS == "absolute":
    ax1.set_xlabel('velocity (rpm)')



ax1.set_ylabel('Torque (Nm)', color='tab:blue')
if MOTOR_TYPE == "11w blue":
    ax1.set_ylim(0, 3.5)
elif MOTOR_TYPE == "5.5w":
    # ax1.set_ylim(0, 3)
    ax1.set_ylim(0, 3.5) #TODO: temp
ax1.tick_params(axis='y', labelcolor='tab:blue')

#plt.scatter(y_savgol*60/(2*np.pi)/6, acceleration_gradient_savgol, color='green', label='Angular acceleration (radians/s^2)', s=1)
ax2 = ax1.twinx()
if MOTOR_TYPE == "11w blue":
    if VELOCITY_X_AXIS == "percentage":
        ax2.scatter(y_savgol*60/(2*np.pi)/6 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI*y_savgol, color='red', label="power", s=1)
    elif VELOCITY_X_AXIS == "absolute":
        ax2.scatter(y_savgol * 60 / (2 * np.pi) / 1 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI * y_savgol, color='red',
                    label="power", s=1)
elif MOTOR_TYPE == "5.5w":
    if VELOCITY_X_AXIS == "percentage":
        ax2.scatter(y_savgol*60/(2*np.pi)/2 * X_AXIS_SCALE, acceleration_gradient_savgol*WHEEL_MOI*y_savgol, color='red', label="power", s=1)
    elif VELOCITY_X_AXIS == "absolute":
        ax2.scatter(y_savgol * 60 / (2 * np.pi) / 1 * X_AXIS_SCALE, acceleration_gradient_savgol * WHEEL_MOI * y_savgol, color='red',
                    label="power", s=1)

ax2.set_ylabel('Power (W)', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')
if MOTOR_TYPE == "11w blue":
    ax2.set_ylim(0, 14)
elif MOTOR_TYPE == "5.5w":
    # ax2.set_ylim(0, 6)
    ax2.set_ylim(0, 14) #TODO: temp

# plt.plot(p1(x), torque_fun(x), label='Torque(Nm) (blue cart)', color='blue')
# plt.plot(p1(x), torque_fun(x)*6, label='Torque(Nm) (simulated red cart)', color='red')
# plt.twinx().plot(p1(x), acceleration_gradient_savgol, label='Angular acceleration (radians/s^2)', color='green')


# plt.twinx().plot(p1(x), p2(x)*WHEEL_MOI, label='Torque (Nm)', color='blue')
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

plt.show()

plt.figure(3)
plt.plot(p1)
