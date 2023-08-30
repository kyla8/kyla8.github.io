#!/usr/bin/env python
# coding: utf-8

# # PRODUCT DESCRIPTION:
#     1. reads data from 2 PAM files
#         a. pull information needed from the header, disregard the rest
#     2. read cell data into Cell class
#     3. percentage():
#         a. observefilter()
#         b. datetimefilter()
#     4. timeUntilNextClosure():
#         a. datetimefilter()
#     5. polarheatplot():
#         a. taking in location and value data, print heatmap

# ### LIMITATION:
#     only can read 2 files JDAY 314 2022 nov 10

# ### Import Libraries

# In[2]:


# Import the pandas library
import pandas as pd

# Import the datetime library
import datetime

import time as times

#Import the numpy library
import numpy as np

#Import the matplotlib library
import matplotlib.pyplot as plt

import os

from IPython.display import display, clear_output

# Define global variables
mission_st = None
mission_end = None
numTarget = 0
endpoint = 0


# ### Cell Class

# In[3]:


class Cell:
    # Function Name: __init__
    # Description: In class Cell: Represents a cell with observation data.
    # Parameters: 
    #      day (str): the day associated with the observation data.
    #      mission_st (datetime): the mission start time. 
    #      mission_end (datetime): the mission end time.
    #      az (tuple): the azimuth range for the observation.
    #      alt (tuple): the altitude range for the observation.
    #      df (DataFrame): the observation data as a panda DataFrame.
    # Returns: None
    def __init__(self, day, mission_st, mission_end, az, alt, df, raw_df):
        self.day = day
        self.missionstart = mission_st
        self.missionstop = mission_end
        self.az = az
        self.alt = alt
        self.df = df
        self.raw_df = raw_df

    # Function Name: observefilter()
    # Description: In class Cell: Filters the observation data based on the 
    #      required total duration of observation. 
    # Parameters: None
    # Returns: filtered_df (DataFrame) : the new filtered dataframe. 
    def observefilter(self, val):
        #print("### OBSERVEFILTER() ###")
        filtered_df = self.df[self.df["Duration (sec)"] >= val]
        if filtered_df.empty:
            #print("No observations with the required total duration found.")
            return filtered_df
        else:
            #print("Observations with the required total duration or more:")
            self.df = filtered_df
            return(self.df)
        
    # Function Name: datetimefilter()
    # Description: In class Cell: Filters the observation data based on the 
    #      specified date and time range. 
    # Parameters: 
    #      start_date (str): the start date and time in the format 
    #          'YYYY-MM-DD HH:MM:SS'.
    #      end_date (str): the end date and time in the format
    #          'YYYY-MM-DD HH:MM:SS'.
    # Returns: filtered_df (DataFrame) : the new filtered dataframe. 
    def datetimefilter(self, start_date=mission_st, end_date=mission_end):
        #global mission_st, mission_end  # Declare df as a global variable
        #df = self.df
        #print("### DATETIMEFILTER() ###")
        #print(start_date)
        #print(end_date)
        # Convert mission start and end dates to strings
        filtered_df = self.df[(self.df["Start Time"] <= end_date) & (self.df["End Time"] >= start_date)]
        if filtered_df.empty:
            #print("No observations within the specified date and time range found.")
            return(filtered_df)
        else:
            #print("Observations within the specified date and time range:")
            self.df = filtered_df
            return(self.df)

    # Function Name: percentage()
    # Description: In class Cell: Calculates the percentage of observaton time based on
    #      the minimum duration and ideal start and end times. 
    # Parameters: None
    # Returns: percent (float): the percentage of observation time. 
    def percentage(self, val):
        #global mission_st, mission_end
        #print("### PERCENTAGE() ###")
        # Call the observefilter() function to return the data with the minimum duration needed to observe
        filtered_df = self.observefilter(val)
        if filtered_df.empty:
                percent = 0.0
                return(percent)
        # Call the datetimefilter() function to return the data with ideal start and end times
        filtered_df = self.datetimefilter(self.missionstart, self.missionstop)
        if filtered_df.empty:
                percent = 0.0
                return(percent)
        mission_dur = (self.missionstop - self.missionstart).total_seconds()
        filtered_dur = filtered_df["Duration (sec)"].sum()
        percent = (filtered_dur / mission_dur) * 100
        return(percent)

    # Function Name: timeUntilClosure()
    # Description: In class Cell: Filters the observation data based on the
    #      specified ideal start and end times. 
    # Parameters: None
    # Returns: filtered_df (DataFrame): Filtred observation data within the 
    #      ideal start and end times.
    def timeUntilClosure(self, given_time):
        #print("### TIMEUNTILCLOSURE() ###")
        #Call the datetimefilter() function to return the data with ideal start and end times
        filtered_df = self.datetimefilter(self.missionstart, self.missionstop)
        
        filtered_df = self.df
        #Find the next closure after the given time
        
        for index, row in filtered_df.iterrows():
            start_time = row["Start Time"]
            end_time = row["End Time"]
            if start_time <= given_time <= end_time:
                difference = end_time - given_time
                #print(difference.total_seconds())
                return difference.total_seconds() #Return the time difference in secs
        return 0 #If no closrue is found after the given time
    
    # Function Name: binaryTimeUntilClosure()
    # Description: In class Cell: Is the cell open during this time? Yes or no
    # Parameters: given_time
    # Returns: difference (in seconds)
    def binaryTimeUntilClosure(self, given_time):
        #print("### BINARYTIMEUNTILCLOSURE() ###")
        filtered_df = self.datetimefilter(self.missionstart, self.missionstop)
        
        filtered_df = self.df
        #Find the next closure after the given time
        
        for index, row in filtered_df.iterrows():
            start_time = row["Start Time"]
            end_time = row["End Time"]
            if start_time <= given_time <= end_time:
                return 1
        return 0 #If no closrue is found after the given time


# ### Header

# In[4]:


# Function Name: header()
# Description: Reads the header information from the file and sets the 
#      mission start time, mission end time, and the total number of target cells
# Parameters: None
# Returns: None
def header(lines):
    global mission_st, mission_end, numTarget, endpoint
    mission_st, mission_end, numTarget, endpoint = None, None, None, 0
    #print("HEADER")
    
    
    for line in lines:
        endpoint = endpoint + 1
        if "Mission Start Date/Time" in line:
            datetime_str = " ".join(line.split()[4:8])
            mission_st = datetime.datetime.strptime(datetime_str, '%Y %b %d %H:%M:%S')

        if "Mission Stop  Date/Time" in line:
            datetime_str = " ".join(line.split()[4:8])
            mission_end = datetime.datetime.strptime(datetime_str, '%Y %b %d %H:%M:%S')

        if "Number of Targets" in line:
            numTarget = int(line.split()[-1])
            break  # Exit the loop when number of targets is found
            
    # Skip lines until the start of the observation data section
    for x, line in enumerate(lines):
        if "YYYY MMM dd (DDD) HHMM SS" in line:
            endpoint = x + 2  # Skip the header line and the separator line
            break


# ### getOneCellDateTime

# In[5]:


# Function Name: getOneCellDateTime()
# Description: Reads the data from the file for a single cell and extracts
#      the data and time information.
# Parameters: 
#      cell (Cell): the cell objec to store the observation data.
#      lines (list): the list of lines containing the observation data.
# Global Variables: endpoint (int): the index of the line where the observation data ends.
# Returns: df (DateFrame): the observation data as a pandas DataFrame.
def getOneCellDateTime(cell, lines):
    #print("### GETONECELLDATETIME() ###")
    
    global endpoint
    # Initialize variables for azimuth and altitude ranges
    az_min = 0.0
    az_max = 0.0
    alt_min = 0.0
    alt_max = 0.0

    table = []
    #Process each line and split the data
    #read the remaining lines into a list
      
    
    
    for x in range(endpoint, len(lines)):
        
        line = lines[x]
        
        #stop at blank line
        #if the next line is NOT blank
        if line.strip():
            #Extract the required info
            
            year1, month1, day1, jday1, hm1, s1, year2, month2, day2, jday2, hm2, s2, dur = line.strip().split()
       
            #Convert the data and time strings to pandas DateTime Objects
            stdatetime = pd.to_datetime(f"{year1} {month1} {day1} {jday1} {hm1} {s1}", format="%Y %b %d (%j) %H%M %S")
            #print(stdatetime)
            enddatetime = pd.to_datetime(f"{year2} {month2} {day2} {jday2} {hm2} {s2}", format="%Y %b %d (%j) %H%M %S")
            #print(enddatetime)
    
            #Calculate the duration in minutes and seconds of each instance
            minutes, seconds = dur.split(':')
            #print(dur)
            total_duration = int(minutes) * 60 + int(seconds)
            #print(total_duration)
    
            #Append the data to the table
            table.append([stdatetime, enddatetime, total_duration])
        else:
            #collect the Azimuth and Alt ranges
            #skip footer lines --> resume back at Azimuth range and elevation range
            x = x + 13

            #copy the range of azimuth degrees (az_min & az_max)
            az = lines[x].split()
            az_min = az[2]
            az_max = az[4]

            #copy the range of altitude degrees (alt_min & alt_max)
            x = x + 1
            alt = lines[x].split()
            alt_min = alt[2]
            alt_max = alt[4]
            x = x + 4
            endpoint = x
            break
    
    cell.az = [float(az_min), float(az_max)]
    cell.alt = [float(alt_min), float(alt_max)]
    #print(alt_min)
    #print(alt_max)
    #print(az_min)
    #print(az_max)
    cell.missionstart = mission_st
    cell.missionstop = mission_end
    cell.day = cell.missionstart.strftime("%B %d, %Y")
  
    #Convert the table into a pandas DataFrame
    df = pd.DataFrame(table, columns=["Start Time", "End Time", "Duration (sec)"])
    cell.df = df
    #print(df)
    return df


# ### polarheatplot

# In[6]:


# Function Name: polarheatplot()
# Description: Prints the data to a polar heat plot.
# Parameters: 
#      cells (Cell): the array of all the cells.
#      value (array): the array of the values to be graphed.
# Returns: prints the polar heatmap
def polarheatplot(cells, value, time):
    # Define the cell ranges using Cell.alt and Cell.az
    cell_ranges = [{"alt": cell.alt, "az": cell.az, "value": value[i]} for i, cell in enumerate(cells)]

    # Create a meshgrid of azimuth and altitude values
    azimuth_deg = np.linspace(0, 360, 360)
    altitude_deg = np.linspace(0, 90, 100)
    azimuth_mesh, altitude_mesh = np.meshgrid(np.radians(azimuth_deg), altitude_deg)

    # Initialize the data array
    data = np.zeros_like(azimuth_mesh)

    # Populate the data array based on the cell ranges and percentage
    for cell_range in cell_ranges:
        alt_min, alt_max = cell_range["alt"]
        azimuth_min, azimuth_max = cell_range["az"]
        value = cell_range["value"]
        mask = (
            (azimuth_mesh >= np.radians(azimuth_min)) & (azimuth_mesh <= np.radians(azimuth_max)) &
            (altitude_mesh >= alt_min) & (altitude_mesh <= alt_max)
        )
        data[mask] = value
        
    #print(cell_ranges)
    # Plot the polar heatmap with color based on percentage
    plt.figure(figsize=(10, 10))
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    cmap = plt.get_cmap('magma')
    cmap.set_under('green')
    
    # Plot the data with the customized colormap
    cax = ax.pcolormesh(azimuth_mesh, altitude_mesh, data, cmap=cmap, shading='auto', vmin=0.01)
    ax.set_theta_zero_location("N")
    ax.set_rlim(90, 11, 1)
    ax.set_yticklabels([])
    #ax.grid(True)
    cbar = fig.colorbar(cax)
    ax.set_title(f"Polar Heatmap{time}")
    plt.show()
    fig.savefig('Polar Heatmap' + time + '.png')
    #plt.close(fig)
    
    
    # Clear the cell_ranges list again if needed
    cell_ranges = []  # Assign an empty list to clear the list


# ### jdaytoDate

# In[7]:


def jdaytoDate(jday, year):
    #Convert JDAY and year to a date object
    date_obj = datetime.datetime.fromordinal(datetime.datetime(year, 1, 1).toordinal() + jday - 1)

    return date_obj


# ### main

# In[8]:


# Create a dictionary to store cells by JDAY and year
cells_dict = {}

# Define the directory path where the PAM files are located
directory = "C:\\Users\\Kae_Lyn\\akamai\\PAM"

# Iterate over the files in the directory
for filename in os.listdir(directory):
    print(filename)
    
    # Check if the file is a PAM file
    if filename.endswith(".txt"):
        # Split the filename based on underscores
        filename_parts = filename.split("_")

        # Verify that the filename has enough parts to extract JDAY and year
        if len(filename_parts) >= 8:
            jday_part = filename_parts[7]
            if "JDAY" in jday_part:
                jday = jday_part.split("JDAY")[1]
            else:
                continue  # Skip this file as it doesn't contain JDAY
        else:
            continue  # Skip this file as it doesn't have the expected format

        # Extract the last 4 characters as the year
        year_part = filename_parts[5]
        year = year_part[-4:]

        # Create a key for the cells dictionary using JDAY and year
        key = (jday, year)

        # Check if the key exists in the dictionary
        if key in cells_dict:
            cells = cells_dict[key]
        else:
            cells = []

        # Open the text file
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            
            #print(mission_st)
            #print(mission_end)
            lines = file.readlines()
            header(lines)
            
            

            for i in range(numTarget):
                cell = Cell(None, None, None, None, None, None, None)
                cell.raw_df = getOneCellDateTime(cell, lines)  # Assign the DataFrame to cell.df
                cell.df = cell.raw_df
                #print(cell.df)
                cells.append(cell)

        file.close()
        # Update the cells dictionary with the new cells list
        #for i, cell in enumerate(cells):
         #   print(cell.df)
        cells_dict[key] = cells
        #print(cells)
        
        
        
sorted_cells_dict = dict(sorted(cells_dict.items(), key=lambda item: (item[0][1], item[0][0])))
#print(sorted_cells_dict)


# ##### Percentage graph

# In[9]:


# Create a dictionary to store percentages for each day
avg_percentages = {}

# Iterate over the cells in the dictionary
for key, cells in sorted_cells_dict.items():
    
    
    # Generate the polar heatmap using percentage
    percentages = [cell.percentage(120) for cell in cells]
    #print(percentages)
    # Calculate the average percentage for the current day
    
    avg_percentage = (sum(percentages)) / (len(percentages))
    print(avg_percentage)
    # Store the average percentage in the dictionary
    avg_percentages[key] = avg_percentage
    
    # Get the date corresponding to the JDAY key
    date = datetime.datetime.strptime(f"{key[0]} {key[1]}", "%j %Y").strftime("%Y-%m-%d")

    
    polarheatplot(cells, percentages, time = (f"- Percentage on {date} (jday {key[0]} {key[1]})"))
    #clear_output(wait = True)
    #plt.savefig(time + '.png')

print(avg_percentages)
    
    # Perform operations on each Cell object
  #  for i, cell in enumerate(cells):
   #     print("Cell:", i)
   #     print("Start Time:", cell.missionstart)
   #     print("End Time:", cell.missionstop)
   #     print("Azimuth Range:", cell.az)
   #     print("Altitude Range:", cell.alt)
   #     print("Percentage:", percentages[i])
   #     print("DataFrame:")
   #     print(cell.df)
   #     print()
    #print("Number of Cells:", len(cells))
    #print()


# ##### Timeline Percentage graph (DateTime x value)

# In[27]:


import matplotlib.pyplot as plt
from datetime import datetime

from pandas.plotting import register_matplotlib_converters  # Import the function

# Register matplotlib converters for pandas datetime data
register_matplotlib_converters()

# Extract the days, years, and percentages from the avg_percentages dictionary
days_years = [datetime.strptime(f"{day} {year}", "%j %Y") for day, year in avg_percentages.keys()]
average_percentages = list(avg_percentages.values())
# Add the Starlink date when they opted out of Space Force Protection (DEC 3, 2022)
starlink_date = datetime.strptime("337 2022", "%j %Y")  # Convert Julian day to datetime

# Sort the data based on dates
sorted_data = sorted(zip(days_years, average_percentages))

# Extract sorted days_years and average_percentages
days_years, average_percentages = zip(*sorted_data)

# Plot the data
plt.figure(figsize=(12, 6))

plt.scatter(days_years, average_percentages, color='blue', marker='o', label='Average Percentage')
plt.plot(days_years, average_percentages, color='gray', linestyle='-', linewidth=2)
# Vertical dashed line for Starlink opt-out date
plt.vlines(x=starlink_date, ymin=0, ymax=100, color='red', linestyle='--', label='Starlink Opt Out (Dec 3, 2022)')

plt.xlabel('Date')
plt.ylabel('Average Percentage Per Day')
plt.title('Average Percentage for Each Day/Year')
plt.grid(True)

# Set the y-axis limits to 0 and 100
plt.ylim(72.5, 92)

# Add annotations for each data point
for i, percentage in enumerate(average_percentages):
    rounded_percentage = round(percentage, 2)  # Round to 2 decimal places
    plt.annotate(f"{rounded_percentage}%", (days_years[i], percentage), textcoords="offset points", xytext=(0, 10), ha='center')

plt.xticks(rotation=45, ha='right')

plt.legend()
plt.tight_layout()

# Show the graph
plt.show()


# ##### Timeline Percentage graph (stretched x axis)

# In[14]:


import matplotlib.pyplot as plt
from datetime import datetime

from pandas.plotting import register_matplotlib_converters  # Import the function

# Register matplotlib converters for pandas datetime data
register_matplotlib_converters()

# Extract the days, years, and percentages from the avg_percentages dictionary
days_years = [datetime.strptime(f"{day} {year}", "%j %Y") for day, year in avg_percentages.keys()]
average_percentages = list(avg_percentages.values())

# Sort the data based on dates
sorted_data = sorted(zip(days_years, average_percentages))

# Extract sorted days_years and average_percentages
days_years, average_percentages = zip(*sorted_data)

# Filter data to exclude months without data points
filtered_days_years = []
filtered_average_percentages = []
for i, date in enumerate(days_years):
    # Check if the month of the current date has data points
    if any(d.month == date.month for d in days_years):
        filtered_days_years.append(date)
        filtered_average_percentages.append(average_percentages[i])

# Plot the data
plt.figure(figsize=(14, 8))  # Increase the figure size

plt.scatter(filtered_days_years, filtered_average_percentages, color='blue', marker='o', label='Average Percentage')
plt.plot(filtered_days_years, filtered_average_percentages, color='gray', linestyle='-', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Average Percentage')
plt.title('Average Percentage for Each Day/Year')
plt.grid(True)

# Set the y-axis limits to 0 and 100, with some additional padding
#plt.ylim(0, 100)

# Add annotations for each data point
for i, percentage in enumerate(filtered_average_percentages):
    rounded_percentage = round(percentage, 2)  # Round to 2 decimal places
    plt.annotate(f"{rounded_percentage}%", (filtered_days_years[i], percentage), textcoords="offset points", xytext=(0, 10), ha='center')

plt.xticks(rotation=45, ha='right')

# Stretch the x-axis range wider for specific months (June and July 2023)
start_date = datetime(2023, 6, 1)
end_date = datetime(2023, 7, 31)
plt.xlim(start_date, end_date)

# Adjust margins
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

plt.legend()

# Show the graph
plt.show()


# ##### Time until closure graph (ANIMATION) 

# for key, cells in sorted_cells_dict.items():    
#     filterDate = jdaytoDate(int(key[0]), int(key[1]))
#     month = int(filterDate.strftime("%m"))
#     day = int(filterDate.strftime("%d"))
#     
#     # Generate the polar heatmap using timeUntilClosure
#     j = 6
#     for i in range(0, 61, 5):  # Loop from 0 to 60 with a step of 5
#         if i == 60:  # Reset i to 0 and increment j
#             i = 0
#             j += 1
#         given_time = datetime.datetime(int(key[1]), month, day, j, i)  # Example given time for JDAY in the specified year
#         timeUntilClosures = [cell.timeUntilClosure(given_time) for cell in cells]
#         #print(timeUntilClosures)
#         # print(cell.df)
#         time = (f"- Time until closure at {j:02d}:{i:02d}")
#         
#         polarheatplot(cells, timeUntilClosures, time)
#         
# 
#         # Clear the previous plot
#         clear_output(wait=True)
# 
#     i = 0

# ##### Time until closure graph (LISTED OUT)

# In[ ]:


for key, cells in sorted_cells_dict.items():    
    filterDate = jdaytoDate(int(key[0]), int(key[1]))
    month = int(filterDate.strftime("%m"))
    day = int(filterDate.strftime("%d"))
    
    # Generate the polar heatmap using timeUntilClosure
    j = 6
    for i in range(0, 61, 5):  # Loop from 0 to 60 with a step of 5
        if i == 60:  # Reset i to 0 and increment j
            i = 0
            j += 1
        given_time = datetime.datetime(int(key[1]), month, day, j, i)  # Example given time for JDAY in the specified year
        timeUntilClosures = [cell.timeUntilClosure(given_time) for cell in cells]
        #print(timeUntilClosures)
        # print(cell.df)
        
        # Get the date corresponding to the JDAY key
        date = datetime.datetime.strptime(f"{key[0]} {key[1]}", "%j %Y").strftime("%Y-%m-%d")
        
        time = (f"- Time until closure on {date} (jday {int(key[0])} {int(key[1])}) at {j:02d}:{i:02d}")
        
        polarheatplot(cells, timeUntilClosures, time)
    i = 0


# ### BINARY POLAR PLOT (animation)

# for key, cells in sorted_cells_dict.items():    
#     filterDate = jdaytoDate(int(key[0]), int(key[1]))
#     month = int(filterDate.strftime("%m"))
#     day = int(filterDate.strftime("%d"))
#     
#     # Generate the polar heatmap using timeUntilClosure
#     j = 6
#     for i in range(0, 61, 5):  # Loop from 0 to 60 with a step of 5
#         if i == 60:  # Reset i to 0 and increment j
#             i = 0
#             j += 1
#         given_time = datetime.datetime(int(key[1]), month, day, j, i)  # Example given time for JDAY in the specified year
#         binaryTimeUntilClosures = [cell.binaryTimeUntilClosure(given_time) for cell in cells]
#         #print(timeUntilClosures)
#         # print(cell.df)
#         time = (f"- Time until closure at {j:02d}:{i:02d} jday {key[0]} {key[1]}")
#         
#         polarheatplot(cells, binaryTimeUntilClosures, time)
#         
#         clear_output(wait = True)
#     i = 0

# ##### Binary Polar Plot

# In[ ]:


cells in sorted_cells_dict.items():    
    filterDate = jdaytoDate(int(key[0]), int(key[1]))
    month = int(filterDate.strftime("%m"))
    day = int(filterDate.strftime("%d"))
    
    # Generate the polar heatmap using timeUntilClosure
    j = 6
    for i in range(0, 61, 1):  # Loop from 0 to 60 with a step of 5
        if i == 60:  # Reset i to 0 and increment j
            i = 0
            j += 1
        given_time = datetime.datetime(int(key[1]), month, day, j, i)  # Example given time for JDAY in the specified year
        binaryTimeUntilClosures = [cell.binaryTimeUntilClosure(given_time) for cell in cells]
        #print(timeUntilClosures)
        # print(cell.df)
        time = (f"- Time until closure at {j:02d}:{i:02d} jday {key[0]} {key[1]}")
        
        polarheatplot(cells, binaryTimeUntilClosures, time)
        
        
    i = 0


# In[ ]:




