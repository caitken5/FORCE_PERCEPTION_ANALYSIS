# Code for force perception analysis.

# Import desired libraries.
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import header as h
import gc

matplotlib.use('Agg')

# Set constants for saving information.
data_source_folder = "D:/FP_Analysis/Data"  # source folder for data files for each trial, specifically answers.
demo_source_file = "D:/FP_Analysis/Data/FP_Demographics.xls"  # source folder for demographic data file.
results_folder = "D:/FP_Analysis/Results"  # Folder for saving the Excel file containing results to be used for statistical analysis.
graph_folder = "D:/FP_Analysis/Graphs"  # Folder for saving graphs of results for each Answers file.
workbook_name = 'FORCE_PERCEPTION_ANALYSIS.xlsx'

testing_plots = True
saving_plots = True

if __name__ == '__main__':
    # Initialize labels to be used for the analysis.
    workbook_path = results_folder + '/' + workbook_name
    sheet_name = 'FP_ANALYSIS'
    # Load in the demographic data as pandas.
    demo_frame = pd.read_excel(demo_source_file)
    dob_array = demo_frame[['DOB_YEAR', 'DOB_MONTH', 'DOB_DAY']].copy().to_numpy()
    dov_array = demo_frame[['VISIT_YEAR', 'VISIT_MONTH', 'VISIT_DAY']].copy().to_numpy()
    ages = []
    for i in range(dob_array.shape[0]):
        dob = dob_array[i]
        dov = dov_array[i]
        age = h.get_age_at_assessment(dob, dov)
        ages.append(age)
    # Create an empty list to which to append all relevant data to analysis.
    demo_frame['AGE'] = ages
    data_to_print = []
    # All files will be saved as text files. Need to make sure no other text files get saved there.
    for file in os.listdir(data_source_folder):
        if file.endswith('.txt'):
            print(file)
            data_demo = h.get_data_demo(file)
            file_path = data_source_folder + "/" + file
            data = np.loadtxt(file_path, comments='#', delimiter=',', unpack=False)
            # Extract relevant data.
            forces = data[:, h.data_header.index("Left_Force"):h.data_header.index("Right_Force") + 1]
            my_len = forces.shape[0]

            # Get the higher force, since one of the cubes is always == ref_force.
            higher_force = h.get_higher_force(forces)

            # Compute the differences along the series to begin the look for reversals in direction.
            force_diff = h.get_force_diff(higher_force)
            staircase_dir = h.get_staircase_dir(force_diff)
            # Debugging section for FP_C_07_NA_L_Answers...
            if "FP_C_07_NA_L_Answers-2022-11-07-12-06-27.txt" in file:
                print("Stopping for check...")
            reversal = h.get_reversal(staircase_dir)

            # Compute the logarithmic differences between the two presented force stimuli.
            force_delta = h.get_force_delta(higher_force)
            log10_delta = h.get_log10(force_delta)

            # Extract the log10_deltas associated with the reversal marks.
            reversal_vals = h.get_reversal_vals(reversal, log10_delta)
            relevant_reversal_vals = h.get_relevant_reversal_vals(reversal_vals)

            # Get the average of these values and compute the Weber fraction.
            if relevant_reversal_vals.shape[0] < h.num_reversals - h.num_remove:
                log_threshold = log10_delta[-1]
                print("Exited early. Minimum threshold obtained.")
                # Here, we take the last value of log_threshold rather than relevant to account for case where no
                # reversals occur.
                # TODO: Determine if I should slightly change how this is achieved because someone can do better than
                #  this and still technically have not beaten it before? Look at graphs to figure out.
            else:
                log_threshold = np.mean(relevant_reversal_vals)
            absolute_threshold = 10 ** log_threshold
            Weber_fraction = np.round(absolute_threshold / h.ref_force, 4)
            data_demo.append(Weber_fraction)  # Append the calculated value.
            data_to_print.append(data_demo)  # Append this line of data to data_to_print array so that all of this
            # collected information can be concatenated with the data from the demographics file and saved together
            # for analysis.
            # Final thing is to print the graphs to the graphs folder.
            fig = plt.figure(num=1, dpi=100, facecolor='w', edgecolor='w')
            fig.set_size_inches(15, 8)
            ax = fig.add_subplot(111)
            # Create a new variable called condensed_reversal, that saves the index of where a reversal occurs.
            condensed_reversal = np.nonzero(reversal)[0]
            if condensed_reversal.shape[0] != 0:
                ax.axvline(x=condensed_reversal[0], label="Reversal Point", color='r')
                for i in range(1, len(condensed_reversal)):
                    ax.axvline(x=condensed_reversal[i], color='r')
            ax.plot(higher_force, label="Comparative Force", marker='o')
            ax.set_xlabel("Trial Number")
            ax.set_ylabel("Force (N)")
            my_title = data_demo[0] + "_MED-" + str(data_demo[3]) + "_SIDE-" + str(data_demo[4])
            ax.set_title(my_title + " Force vs. Trial Responses")
            ax.grid()
            ax.legend(loc='lower left')
            file_list = file.split('_')
            save_str = graph_folder + '/' + '_'.join(file_list[0:5])
            plt.savefig(fname=save_str)
            fig.clf()
            plt.close()
            gc.collect()

    # Convert data_to_print to a dataframe.
    data_frame = pd.DataFrame(np.asarray(data_to_print), columns=h.data_name_header)
    combo_frame = pd.merge(data_frame, demo_frame, how='left', on='ID_STRING')
    combo_frame = combo_frame.drop(columns=['COHORT_x', 'ID_x'])
    combo_frame = combo_frame.rename(columns={'COHORT_y': 'COHORT', 'ID_y': 'ID'})
    combo_frame.loc[combo_frame['MED_STATE'] == '0', ['DYSKINESIA', 'DYS_INTERFERE']] = '0'
    combo_frame = combo_frame.fillna(0)
    combo_frame = combo_frame.astype({'DYSKINESIA': 'int', 'DYS_INTERFERE': 'int'})
    # Save this information to a new Excel file.
    combo_frame.to_excel(workbook_path, sheet_name=sheet_name)
    print("Exiting the program.")
