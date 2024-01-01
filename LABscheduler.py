#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from fuzzywuzzy import fuzz, process


# In[2]:


class Physician:
    def __init__(self, name, speciality, location, monAM, monPM, tueAM, tuePM, wedAM, wedPM, thuAM, thuPM):
        self.name = name
        self.speciality = speciality
        self.availability = {
            'monAM': monAM,
            'monPM': monPM,
            'tueAM': tueAM,
            'tuePM': tuePM,
            'wedAM': wedAM,
            'wedPM': wedPM,
            'thuAM': thuAM,
            'thuPM': thuPM
        }
        self.location = location

    def update_availability(self, time_slot):
        self.availability[time_slot] = False

    def __str__(self):
        return f"Name: {self.name}\nSpeciality: {self.speciality}\nAvailability: {self.availability}"

class Student:
    def __init__(self, name, flex_time, location, preference):
        self.name = name
        self.assignment = {
            "monAM": None,
            "monPM": None,
            "tueAM": None,
            "tuePM": None,
            "wedAM": None,
            "wedPM": None,
            "thuAM": None,
            "thuPM": None
        }
        self.assignment[flex_time] = "FLEX"
        self.specialities_assigned = {
            "FM": 2,
            "IM": 1,
            "Peds": 1,
            #"PalMed": 1,
            "Geriatrics": 1
        }
        self.location = location
        self.preference = preference

    def update_assignment(self, time_slot, physician):
        self.assignment[time_slot] = physician

    def __str__(self):
        return f"Name: {self.name}\nAssignment: {self.assignment}\nSpecialities Assigned: {self.specialities_assigned}"


# In[3]:


def create_students(students_df):
    """
    Creates a list of Student objects from a 2-column dataframe of student names and their preferred flex time.
    """
    students = []

    for _, row in students_df.iterrows():
        student = Student(row['name'], row['flex_time'], row['location'], row['preference'])
        students.append(student)
    
    return students

def create_physicians(physicians_df):
    """
    Creates a list of Physician objects from a dataframe of physicians with the associated speciality and their availability.
    """
    physicians = {}

    for _, row in physicians_df.iterrows():
        physician = Physician(
            row['name'],
            row['speciality'],
            row['location'],
            row['monAM'],
            row['monPM'],
            row['tueAM'],
            row['tuePM'],
            row['wedAM'],
            row['wedPM'],
            row['thuAM'],
            row['thuPM']
        )
        physicians[row['name']] = physician

    return physicians

def find_time(student, physician):
    for time_slot in student.assignment:
        if (student.assignment[time_slot] == None) and (physician.availability[time_slot]):
            return time_slot
    return None

def generate_student_schedule(students):
    """
    Generates a human-readable dataframe where each row represents a student. The assignment on each session is given in the column with the physicians name and speciality
    """
    # Create an empty DataFrame to store the schedule
    schedule_df = pd.DataFrame(columns=["Student", "monAM", "monPM", "tueAM", "tuePM", "wedAM", "wedPM", "thuAM", "thuPM"])

    # Iterate through each student
    for student in students:
        schedule = {
            "Student": student.name,
            "monAM": "FLEX" if student.assignment["monAM"] == "FLEX" else "free time",
            "monPM": "FLEX" if student.assignment["monPM"] == "FLEX" else "free time",
            "tueAM": "FLEX" if student.assignment["tueAM"] == "FLEX" else "free time",
            "tuePM": "FLEX" if student.assignment["tuePM"] == "FLEX" else "free time",
            "wedAM": "FLEX" if student.assignment["wedAM"] == "FLEX" else "free time",
            "wedPM": "FLEX" if student.assignment["wedPM"] == "FLEX" else "free time",
            "thuAM": "FLEX" if student.assignment["thuAM"] == "FLEX" else "free time",
            "thuPM": "FLEX" if student.assignment["thuPM"] == "FLEX" else "free time"
        }

        # Iterate through the assignments to fill in the physician names
        for time_slot, physician in student.assignment.items():
            if physician != "FLEX" and physician != None:
                schedule[time_slot] = physician.name + " (" + physician.speciality + ", " + physician.location + ")"

        # Append the schedule for the current student to the DataFrame
        schedule_df.loc[len(schedule_df)] = schedule
        #schedule_df = schedule_df.append(schedule, ignore_index=True)

    return schedule_df


# In[4]:


students_df = pd.read_csv("./input/students.csv")
physicians_df = pd.read_csv("./input/physicians.csv")

students = create_students(students_df)
physicians = create_physicians(physicians_df)
physicians_list = physicians_df['name']

for student in students:
    for specialty in student.specialities_assigned:
        while student.specialities_assigned[specialty] > 0:
            try:
                physician = physicians[process.extractOne(student.preference, physicians_list)[0]]
                time_slot = find_time(student, physician)
                if (time_slot != None) and (physician.speciality == specialty):
                    student.update_assignment(time_slot, physician)
                    physician.update_availability(time_slot)
                    student.specialities_assigned[specialty] -= 1
                    break
                else:
                    raise Exception()
            except:
                for name, physician in physicians.items():
                    if physician.speciality == specialty:
                        time_slot = find_time(student, physician)
                        if time_slot != None:
                            student.update_assignment(time_slot, physician)
                            physician.update_availability(time_slot)
                            student.specialities_assigned[specialty] -= 1
                            break

schedule_df = generate_student_schedule(students)
schedule_df.to_csv("assignment.csv")
print(schedule_df)

