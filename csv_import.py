import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# kilogram square meter
WHEEL_MOI = 0.0241857894

df = pd.read_csv('flywheel_data_blue_alternating.csv')

x = df['time'].to_numpy()/1000.0

y = df['velocity'].to_numpy() * (2*np.pi)/60

y_savgol = savgol_filter(y, 100, 3)

current = df['current'].to_numpy()/1000

current_savgol = savgol_filter(current, 100, 3)

velocity_poly = np.polyfit(x, y, 6)

print(f'velocity coefficients: {velocity_poly}')

acceleration_poly = np.polyder(velocity_poly)

acceleration_gradient = np.gradient(y_savgol)/0.01
acceleration_gradient_savgol = savgol_filter(acceleration_gradient, 200, 3)

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
plt.xlim(0,5)
plt.show()

plt.figure(2)
fig, ax1 = plt.subplots()
fig.set_size_inches(8, 5)
ax1.scatter(y_savgol*60/(2*np.pi)/6, acceleration_gradient_savgol*WHEEL_MOI, color='blue', label='Torque(Nm) (blue cart)', s=1)
ax1.scatter(y_savgol*60/(2*np.pi)/6, acceleration_gradient_savgol*WHEEL_MOI*6, color='orange', label='Torque(Nm) (simulated red cart)', s=1)
ax1.scatter(y_savgol*60/(2*np.pi)/6, current_savgol, color='green', label='Current (mA)', s=1)

ax1.set_xlabel('%max velocity')
ax1.set_ylabel('Torque (Nm)', color='tab:blue')
ax1.set_ylim(0, 3.5)
ax1.tick_params(axis='y', labelcolor='tab:blue')

#plt.scatter(y_savgol*60/(2*np.pi)/6, acceleration_gradient_savgol, color='green', label='Angular acceleration (radians/s^2)', s=1)
ax2 = ax1.twinx()
ax2.scatter(y_savgol*60/(2*np.pi)/6, acceleration_gradient_savgol*WHEEL_MOI*y_savgol, color='red', label="power", s=1)
ax2.set_ylabel('Power (W)', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')
ax2.set_ylim(0, 14)

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
