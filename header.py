# This file holds all the data constants and functions.
import numpy as np

# CONSTANTS
# --data_header constants--
# Time: Double. The time stamp associated with when in the recording the answer was measured.
# Left Force: Double. The force assigned to the left cube.
# Right Force: Double. The force assigned to the right cube.
# Left_Answer: Boolean. True if person selected left square as the correct answer, False otherwise.
# Right_Answer: Boolean.True if person selected right square as the correct answer, False otherwise.
# Left_Correct: Boolean. True if the left square contains the higher force, False otherwise.
# Right_Correct: Boolean. True if the right square contains the higher force, False otherwise.
data_header = ["Time", "Left_Force", "Right_Force", "Left_Answer", "Right_Answer", "Left_Correct", "Right_Correct"]
# --demo_header constants--
# ID_STRING: First two letters contain the name of the study. Next letter contains the group to which the person
# belongs. Final two digits correspond to the patient number; this will always be two digits long, and the number is
# unique across all groups.
# COHORT: To be extracted from ID_STRING of data file for matching purposes. 0 for Control, 1 for PD.
# ID: To be extracted from ID_STRING of data file for matching purposes. Int value, unique to each group.
# DOB_YEAR: The year of date of birth. For age calculation. Int value.
# DOB_MONTH: The month of date of birth. For age calculation. Int value.
# DOB_DAY: The day of date of birth. For age calculation. Int value.
# VISIT_YEAR: The year of the visit. For age calculation. Int value.
# VISIT_MONTH: The month of the visit. For age calculation. Int value.
# VISIT_DAY: The day of the visit. For age calculation. Int value.
# DOM_HAND: The dominant hand of the participant. 0 for Left, 1 for Right.
# SEX: The assigned sex of the participant. 0 for Female, 1 for Male.
# NEURO_ISSUES: Any noticeable neurological issues will be noted. 0 for none, 1 for noticeable. Will be used as
# exclusionary criteria for selected candidates.
# DIAGNOSIS_YEAR: Year of original diagnosis of PD. Estimated only. Patients less than 4 years will be excluded.
# YEARS_ON_DRT: Number of years on dopamine replacement therapy.
# MOCA_SCORE: Total score for a PD patient on the Montreal Cognitive Assessment. Will be used as demographic and
# screening tool.
# UPDRS_OFF: Total score for a PD patient on the Movement Disorders Society Unified Parkinson's Disease Rating Scale
# (MDS-UPDRS) for Part III Motor Assessment only, when not in the medication state. This means that the patient did not
# take their medication the night before, or the morning of, the assessment.
# UPDRS_ON: Total score for a PD patient on the Movement Disorders Society Unified Parkinson's Disease Rating Scale
# # (MDS-UPDRS) for Part III Motor Assessment only, when in the medicated state. This means that the patient took 1.5
# to 2 times their dose.
# SIDE_OF_ONSET: The estimated side, according to patient history of symptom onset, on which symptoms first began.
demo_header = ["ID_STRING", "COHORT", "ID", "DOB_YEAR", "DOB_MONTH", "DOB_DAY", "VISIT_YEAR", "VISIT_MONTH",
               "VISIT_DAY", "DOM_HAND", "SEX", "NEURO_ISSUES", "DIAGNOSIS_YEAR", "YEARS_ON_DRT", "MOCA_SCORE_ON",
               "UPDRS_OFF", "UPDRS_ON", "SIDE_OF_ONSET"]

# --data_name_header--
# ID_STRING: First two letters contain the name of the study. Next letter contains the group to which the person
# belongs. Final two digits correspond to the patient number; this will always be two digits long, and the number is
# unique across all groups.
# COHORT: 0 for Control, 1 for PD.
# ID: Int value, unique to each group.
# MED_STATE: 0: OFF, 1: ON, 2: NA.
# HAND: 0: Left, 1: Right.
data_name_header = ["ID_STRING", "COHORT", "ID", "MED_STATE", "HAND", "WEBER_FRACTION"]

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
    return np.hstack([-1, force_diff])  # Shifts the difference over one, and assumes that the program starts in the
    # descending phase.


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


def get_data_demo(file_name):
    file = file_name.split('.')[0]
    file_list = file.split('_')
    # Extract the first part of the string for row matching.
    id_string = '_'.join(file_list[0:3])
    # Delete parts of file_list unrelated to data I want to keep.
    file_list = file_list[1:5]
    # Change the first value to C:0 and P:1.
    file_list[0] = get_cohort_num(file_list[0])
    file_list[1] = get_id_num(file_list[1])
    file_list[2] = get_med_state(file_list[2])
    file_list[3] = get_side(file_list[3])
    data_demo = file_list
    data_demo.insert(0, id_string)
    return data_demo


def get_age_at_assessment(birth_date, visit_date):
    # Assume that the the dates are passed as arrays containing the dates. Extract these values.
    birth_year = birth_date[0]
    birth_month = birth_date[1]
    birth_day = birth_date[2]
    visit_year = visit_date[0]
    visit_month = visit_date[1]
    visit_day = visit_date[2]
    age = visit_year - birth_year
    if birth_month > visit_month:
        age -= 1
    elif birth_month == visit_month:
        if birth_day > visit_day:
            age -= 1
    return age


def get_cohort_num(val):
    if val == "C":
        num = 0
    else:
        num = 1
    return num


def get_id_num(val):
    # Convert value from string to number. I think I may have to check for zeroes.
    if val[0] == '0':
        val = val[1:]
    num = int(val)
    return num


def get_med_state(val):
    # 0: OFF, 1: ON, 2: NA
    if val == "OFF":
        num = 0
    elif val == "ON":
        num = 1
    else:
        num = 2
    return num


def get_side(val):
    # 0: Left, 1: Right.
    if val == "L":
        num = 0
    else:
        num = 1
    return num
