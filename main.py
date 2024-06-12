import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
"""
This script isn't functional yet, its more of a proof of concept and a learning experience for me. I wanted to
experience what real world Aerospace Programmers might use python for. 

In theory: This code should Read telemetry data out of a CSV file -> Process the data from the file including 
time, position and velocity data. -> Create a visualization of the trajectory using matplotlib

panda lib for data handling, and matplotlib for 3D visualization

numpy lib Provides support for arrays and matrices, along with mathematical functions to operate on them. 
(we don't actually use numpy in this file, but future improvements and additions to this software would likely use numpy

matplotlib.pyplot is used here for plotting and visualization of the trajectory which makes this software super cool

scipy.integrate('cumtrapz') Provides numerical integration functions for computing the cumulative integral of 
an array using trapezoidal rule
"""
#Read Telemetry Data
def read_telemetry_data(file_path):
    df = pd.read_csv(file_path)
    return df       # Returns: A pandas.DataFrame containing the telemetry data.

#Process Data
def calculate_trajectory(df):
    # Extract time, position, and velocity
    time = df['time'].values
    x = df['x'].values
    y = df['y'].values
    z = df['z'].values
    vx = df['vx'].values
    vy = df['vy'].values
    vz = df['vz'].values



#Calculate Trajectory using numerical integration
    position_x = cumtrapz(vx, time, initial=0)
    position_y = cumtrapz(vy, time, initial=0)
    position_z = cumtrapz(vz, time, initial=0)

    return time, position_x, position_y, position_z



#Visualize Trajectory
def plot_trajectory(time, x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, label='Trajectory')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Z Position')
    ax.set_title('Spacecraft Trajectory')
    plt.legend()
    plt.show()



# Main function

def main():
    # Replace 'telemetry_data.csv' with the path to your telemetry data file
    file_path = 'telemetry_data.csv'
    df = read_telemetry_data(file_path)
    time, x, y, z = calculate_trajectory(df)
    plot_trajectory(time, x, y, z)

if __name__ == '__main__':
    main()





"""
Potential Problems:
Data Quality:
Ensure that the telemetry data is accurate and free of errors. Missing or incorrect data points can
lead to incorrect trajectory calculations

Numerical Integration Accuracy: Depending on the integration method and the nature of the velocity data,
numerical integration might introduce errors. Advanced methods like Rungue-kutta can be used for better accuracy.

Performance:
For large datasets, performance might be an issue. Efficient data handing and processing are essential.

"""