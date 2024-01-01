# LAB Clerkship Scheduler

This software uses object oriented programming to assign students to various preceptors and create a schedule for the Longitudinal Ambulatory Block at the Cleveland Clinic Lerner College of Medicine at Case Western Reserve University.

## Requirements

In order to use this algorithm, you will need to have the following packages installed:

* Python3 
* Pandas (for data manipulation and analysis)
* fuzzywuzzy (for fuzzy matching of entered preceptor preferences)

You can install these packages by running the following command in the downloaded path:
```
pip install pandas fuzzywuzzy
```

## Usage

To use the algorithm, a `students.csv` and `preceptors.csv` file must be provided, which represent the students' preferences and the preceptors' availability, respectively. 

Running the following command will save the optimal assignment of students to `assignment.csv`.

```
python3 LABscheduler.py
```

## Example

The output of running the provided sample preferences and preceptors should be:
```
      Student  ...                                              thuPM
0    student1  ...                                               FLEX
1    student2  ...                                               FLEX
2    student3  ...                                          free time
3    student4  ...  Dobler, Kim/Marsh, Lisa/Goettemoeller, Michell...
4    student5  ...                                          free time
5    student6  ...                                               FLEX
6    student7  ...                                               FLEX
7    student8  ...  Alfes, John/Komitau, Jason/Hollingsworth, Ambe...
8    student9  ...                 Tchelidze, Tea (IM, Beachwood FHC)
9   student10  ...  Tousi, Babak (Geriatrics, Lakewood Medical Bui...
10  student11  ...             Preston, Andrea (Peds, Avon Point FHC)
11  student12  ...  Chisholm, Jessica/Cloud, Lisa/Anderson, Elizab...
12  student13  ...                                          free time
13  student14  ...                                          free time
14  student15  ...                                               FLEX
15  student16  ...  Allan, Daniel/Krajcik, Daniel/Waite, Coulton (...
16  student17  ...  Yepes-Rios, Monica (IM, Lutheran Hospital Medi...

[17 rows x 9 columns]
```
Note that the order of students is stochastic. 