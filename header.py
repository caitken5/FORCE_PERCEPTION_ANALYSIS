# This file holds all the data constants and functions.
import numpy as np

# CONSTANTS
# Time: Double. The time stamp associated with when in the recording the answer was measured.
# Left Force: Double. The force assigned to the left cube.
# Right Force: Double. The force assigned to the right cube.
# Left_Answer: Boolean. True if person selected left square as the correct answer, False otherwise.
# Right_Answer: Boolean.True if person selected right square as the correct answer, False otherwise.
# Left_Correct: Boolean. True if the left square contains the higher force, False otherwise.
# Right_Correct: Boolean. True if the right square contains the higher force, False otherwise.
import pandas as pd

data_header = ["Time", "Left_Force", "Right_Force", "Left_Answer", "Right_Answer", "Left_Correct", "Right_Correct"]
demo_header = ["STUDY", "COHORT", "ID", "MED_STATE", "ARM", "FILE_TYPE", "RECORDING_DATE"]

ref_force = 4.5
left = data_header.index("Left_Force")
right = data_header.index("Right_Force")
num_reversals = 10
num_remove = 2


def get_higher_force(forces):
    higher_force = np.zeros((forces.shape[0],))
    for i in range(forces.shape[0]):
        if forces[i, 0] > forces[i, 1]:
            higher_force[i] = forces[i, 0]
        else:
            higher_force[i] = forces[i, 1]
    return higher_force


def get_staircase_dir(force_diff):
    my_len = force_diff.shape[0]
    staircase_dir = np.zeros((my_len,))
    for i in range(my_len):
        if force_diff[i] > 0:
            staircase_dir[i] = 1
        elif force_diff[i] < 0:
            staircase_dir[i] = -1
        elif force_diff[i] == 0:
            staircase_dir[i] = staircase_dir[i - 1]
    return staircase_dir


def print_two_arrays(array_1, array_2):
    my_len = array_1.shape[0]
    if array_1.shape[0] == array_2.shape[0]:
        for i in range(my_len):
            print(round(array_1[i], 2), round(array_2[i], 2))
    else:
        print("Cannot print the arrays, lengths of arrays are not equal.")


def get_diff(array):
    return np.diff(array)


def get_force_diff(higher_force):
    force_diff = get_diff(higher_force)
    return np.hstack([-1,
                      force_diff])  # Shifts the difference over one, and assumes that the program starts in the descending phase.


def get_reversal(staircase_dir):
    reversal = np.diff(staircase_dir)
    end_val = -1 * reversal[np.nonzero(reversal)[0][-1]]
    reversal = np.hstack([reversal, end_val])
    return reversal / 2


def get_force_delta(higher_force):
    return higher_force - ref_force


def get_log10(array):
    return np.log10(array)


def get_reversal_vals(reversal, log10_delta):
    return log10_delta[np.nonzero(reversal)[0]]


def get_relevant_reversal_vals(reversal_vals):
    # Assumes the first two entries are not relevant.
    return reversal_vals[num_remove:]


# TODO: Write a function that takes in the file names and separates them into relevant data.
def get_data_demo(file_name):
    file = file_name.split('.')[0]
    file_list = file.split('_')
    data_demo = file_list
    return data_demo
