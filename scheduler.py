#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from fuzzywuzzy import fuzz, process
import time

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
    def __init__(self, name, flex_time, preference):
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
            "Geriatrics": 1,
            "IM": 1,
            "Peds": 1
            #"PalMed": 1,
        }
        self.preference = preference

    def update_assignment(self, time_slot, physician):
        self.assignment[time_slot] = physician

    def __str__(self):
        return f"Name: {self.name}\nAssignment: {self.assignment}\nSpecialities Unassigned: {self.specialities_assigned}"

def create_students(students_df):
    """
    Creates a list of Student objects from a 2-column dataframe of student names and their preferred flex time.
    """
    students = []

    for _, row in students_df.iterrows():
        student = Student(row['name'], row['flex_time'], row['preference'])
        students.append(student)
    
    return students

def create_physicians(physicians_df):
    """
    Creates a list of Physician objects from a dataframe of physicians with the associated speciality and their availability.
    """
    physicians_df['travel_miles'] = physicians_df['travel_miles'].fillna(0)
    physicians_df = physicians_df.sort_values('travel_miles').drop('travel_miles', axis = 1)
    physicians_df = physicians_df.fillna(False)
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

def find_time(student, physician, isFM):
    for time_slot in student.assignment:
        if (student.assignment[time_slot] == None) and (physician.availability[time_slot] == True):
            #return time_slot
            if(isFM):
                if(time_slot[3:] == 'AM'):
                    return time_slot
            else:
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
            "monAM": "FLEX" if student.assignment["monAM"] == "FLEX" else "open",
            "monPM": "FLEX" if student.assignment["monPM"] == "FLEX" else "open",
            "tueAM": "FLEX" if student.assignment["tueAM"] == "FLEX" else "open",
            "tuePM": "FLEX" if student.assignment["tuePM"] == "FLEX" else "open",
            "wedAM": "FLEX" if student.assignment["wedAM"] == "FLEX" else "open",
            "wedPM": "FLEX" if student.assignment["wedPM"] == "FLEX" else "open",
            "thuAM": "FLEX" if student.assignment["thuAM"] == "FLEX" else "open",
            "thuPM": "FLEX" if student.assignment["thuPM"] == "FLEX" else "open"
        }

        # Iterate through the assignments to fill in the physician names
        for time_slot, physician in student.assignment.items():
            if physician != "FLEX" and physician != None:
                schedule[time_slot] = physician.name + " (" + physician.speciality + ", " + physician.location.strip() + ")"
                #schedule[time_slot] = physician.name + " (" + physician.speciality + ")"

        # Append the schedule for the current student to the DataFrame
        schedule_df.loc[len(schedule_df)] = schedule
        #schedule_df = schedule_df.append(schedule, ignore_index=True)

    return schedule_df

def clean_student_df(students_df):
    students_df['preference'] = students_df.apply(lambda x: list([x['Family Medicine Preceptor Preference'], 
                                                                  x['Internal Medicine Preceptor Preference'], 
                                                                  x['Geriatrics Preceptor Preference'],
                                                                 x['Pediatrics Preceptor Preference']]), axis=1)
    flex_dict = {"Monday AM": "monAM", "Monday PM": "monPM", 
                 "Tuesday AM": "tueAM", "Tuesday PM": "tuePM", 
                 "Wednesday AM": "wedAM", "Wednesday PM": "wedPM", 
                 "Thursday AM": "thuAM", "Thursday PM": "thuPM",
                "No Preference": None}
    students_df = students_df[['Email', 'Flex Preference', 'preference']].rename(columns={"Email": "name", "Flex Preference": "flex_time"}).replace({"flex_time": flex_dict})
    students_df = students_df.sample(frac=1).reset_index()
    return students_df


# In[ ]:


students_df = clean_student_df(pd.read_excel("./input/Longitudinal Ambulatory Block Preferences(1-18).xlsx"))
physicians_df = pd.read_csv("./input/physicians.csv")

students = create_students(students_df)
physicians = create_physicians(physicians_df)
physicians_list = physicians_df['name']


# In[ ]:


for student in students:
    for specialty in student.specialities_assigned:
        timeout = time.time() + 5 # give 5 seconds to find the assignment
        while student.specialities_assigned[specialty] > 0:
            if time.time() > timeout:
                print(specialty + " unassigned")
                break
            try:
                specialty_index = None
                if(specialty == "FM"):
                    specialty_index = 0
                elif(specialty == "IM"):
                    specialty_index = 1
                elif(specialty == "Geriatrics"):
                    specialty_index = 2
                elif(specialty == "Peds"):
                    specialty_index = 3
                physician = physicians[process.extractOne(student.preference[specialty_index], physicians_list)[0]]
                isFM = (specialty == "FM")
                time_slot = find_time(student, physician, isFM)
                if (time_slot != None) and (physician.speciality == specialty):
                    print(specialty + " assigned")
                    student.update_assignment(time_slot, physician)
                    physician.update_availability(time_slot)
                    student.specialities_assigned[specialty] -= 1
                    if(specialty == "FM"):
                        next_time_slot = time_slot[:3] + 'P' + time_slot[4:]
                        student.update_assignment(next_time_slot, physician)
                        physician.update_availability(next_time_slot)
                        student.specialities_assigned[specialty] -= 1
                    break
                else:
                    raise Exception()
            except:
                for name, physician in physicians.items():
                    if physician.speciality == specialty:
                        time_slot = find_time(student, physician, isFM)
                        if time_slot != None:
                            print(specialty + " assigned")
                            student.update_assignment(time_slot, physician)
                            physician.update_availability(time_slot)
                            student.specialities_assigned[specialty] -= 1
                            if(specialty == "FM"):
                                next_time_slot = time_slot[:3] + 'P' + time_slot[4:]
                                student.update_assignment(next_time_slot, physician)
                                physician.update_availability(next_time_slot)
                                student.specialities_assigned[specialty] -= 1
                            break
    print(student)
    print("\n")
schedule_df = generate_student_schedule(students)
schedule_df.to_csv("assignment.csv")
schedule_df

