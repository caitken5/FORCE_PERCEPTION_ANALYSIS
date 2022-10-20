# Code for force perception analysis.

# Import desired libraries.
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import xlsxwriter
import header as h


# Set constants for saving information.
data_source_folder = "C:/Users/carol/OneDrive/Desktop/FP_Analysis"  # source folder for data files for each trial, specifically answers.
demo_source_file = "C:/Users/carol/OneDrive/Desktop/FP_Analysis/FP_Demographics.xls"  # source folder for demographic data file.
results_folder = ""  # Folder for saving the Excel file containing results to be used for statistical analysis.
graph_folder = ""  # Folder for saving graphs of results for each Answers file.
workbook_name = 'FORCE_PERCEPTION_ANALYSIS.xlsx'

testing_plots = True
saving_plots = True

if __name__ == '__main__':
    workbook_path = results_folder + '/' + workbook_name
    workbook = xlsxwriter.Workbook(workbook_path)
    # Load in the demographic data as pandas.
    demo = pd.read_excel(demo_source_file)
    # Create an empty list to which to append all relevant data to analysis.
    data_to_print = []
    # All files will be saved as text files. Need to make sure no other text files get saved there.
    for file in os.listdir(data_source_folder):
        if file.endswith('.txt'):
            print(file)
            data_demo = h.get_data_demo(file)
            print(data_demo)
            data = np.loadtxt(file, comments='#', delimiter=',', unpack=False)
            # TODO: Determine why the above line does not recognize that the file exists.
            # Extract relevant data.
            forces = data[:, h.data_header.index("Left_Force"):h.data_header.index("Right_Force") + 1]
            my_len = forces.shape[0]

            # Get the higher force, since one of the cubes is always == ref_force.
            higher_force = h.get_higher_force(forces)

            # Compute the differences along the series to begin the look for reversals in direction.
            force_diff = h.get_force_diff(higher_force)
            staircase_dir = h.get_staircase_dir(force_diff)
            reversal = h.get_reversal(staircase_dir)

            # Compute the logarithmic differences between the two presented force stimuli.
            force_delta = h.get_force_delta(higher_force)
            log10_delta = h.get_log10(force_delta)

            # Extract the log10_deltas associated with the reversal marks.
            reversal_vals = h.get_reversal_vals(reversal, log10_delta)
            relevant_reversal_vals = h.get_relevant_reversal_vals(reversal_vals)

            # Get the average of these values and compute the Weber fraction.
            if relevant_reversal_vals.shape[0] < h.num_reversals - h.num_remove:
                log_threshold = relevant_reversal_vals[-1]
                print("Exited early. Minimum threshold applied.")
            else:
                log_threshold = np.mean(relevant_reversal_vals)
            absolute_threshold = 10 ** log_threshold
            Weber_fraction = absolute_threshold / h.ref_force
            data_demo.append(Weber_fraction)  # Append the calculated value.
            data_to_print.append(data_demo)  # Append this line of data to

    # TODO: Identify what data I want to print to the file for analysis.
    # TODO: In the column for hand used, change convention to 0 and 1 instead of right and left.
    #  Also change cohort and med state.

    print(data_to_print)