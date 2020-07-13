#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

""" Description
I wrote this script while studying for the AWS Solutions Architect - Associate
exam. I was struggling with the math and rules surrounding RDS storage types 
and instance selection as they relate to IO per second (IOPS), especially
when it comes to gp2 storage. 
The goal of this script is to query the user for RDS specifics and then feed 
the the minimum instance requirements back to the user. Hopefully they can use
this as a tool to ensure they choose the proper RDS instance.
A secondary goal is to show the forumulas and DB specific information where
appropriate so this can be used as a study aide to reinforce testable RDS 
information. This script could also be used to check the results from manual 
calculations while working on testable scenarios.
"""

from os import system, name
import math

__author__ = 'Chris Phillips'
__copyright__ = "Copyright 2020, Chris Phillips AWS Tools"
__email__ = 'chris.phillips2@cerner.com'

# Global variable declarations
rds_db_dict = {}
rds_db_dict = dict(Aurora = {'Name': 'Amazon Aurora',
                            'Menu Number': '1',
                            'Page Size': '16'},
                   Maria = {'Name': 'MariaDB',
                            'Menu Number': '2',
                            'Page Size': '16'},
                   MsSQL = {'Name': 'Microsoft SQL Server',
                            'Menu Number': '3',
                            'Page Size': '8'},
                   MySQL = {'Name': 'MySQL',
                            'Menu Number': '4',
                            'Page Size': '16'},
                   Oracle = {'Name': 'Oracle',
                            'Menu Number': '5',
                            'Page Size': '8'},
                   PostgreSQL = {'Name': 'PostgreSQL',
                                'Menu Number': '6',
                                'Page Size': '8'})
user_input = []
db_instance_invalid = 'You must enter 1 or 2.\n'
e_cont = 'Press <ENTER> to continue.'
iops_invalid = 'IOPS must be an integer between 1000 and 40000.\n'
menu_invalid = 'You must enter a number between 1 and 6.\n'
page_num_invalid = 'The page number must be an integer between 1 and 32.\n'
range_invalid = 'IOPS must be an integer, in an increment of 1000, and between 1000 and 40000\n'

# Function declarations
def clear():
    if name == 'nt':
        _ = system('cls')

def main_screen():
    clear()
    print('AWS RDS IOPS Calculator\n\n')

# The function introduces the user to the script and explains what information
# they need to provide.
def script_intro():
    main_screen()
    print('''
When building a database using Amazon RDS you need to define the server
instance type, the type of storage, and the amount of storage. These work
together to provide the best peformance at the least cost. If you don't 
understand how these work with each other, you run the risk of creating 
performance bottlenecks, or buying to0 much of the wrong resources.
You will do the best job of balancing cost and performance if you can provide
accurate information about several key factors.  
At a minimum you will need to know the following:
\t1. Which RDS database you plan to use 
\t\t(Aurora, MariaDB, Microsoft SQL, MySQL, Oracle, or PostgreSQL)
\t2. The database page size in KB (if using gp2 storage).
\t3. The desired IOPS (Input/output Operations Per Second).t
\t4. The type of storage you plan to use (gp2 or Io1).
\n
Accurate data in the above areas will help you make the best choices regarding
how much disk space you need and which DB instance to choose.
''')
    x=input('\nPress any key when ready to begin or "Q" to exit: ')
    if x == str("q") or x == str("Q"):
        exit()
    else:
        return(None)

# This collects the necessary input from the user, validates the data and 
# returns the user's input as a list.
def get_input():
    num_range = list(range(1000, 41000, 1000))
    local_input = [0] * 5
    while True:
        main_screen()
        print('Which RDS service are you planning to use?\n')
        for db_type, db_details in sorted(rds_db_dict.items()):
            dbnum = db_details['Menu Number']
            dbname = db_details['Name']
            print(dbnum + ": " + dbname)
        menu_choice = input('Please enter a number between 1 and 6: ')
        if menu_choice.isdigit():
            if int(menu_choice) >= 1 and int(menu_choice) <=6:
                for db_type, db_details in sorted(rds_db_dict.items()):
                    dbnum = db_details['Menu Number']
                    if int(dbnum) == int(menu_choice):
                        local_input[0] = db_details['Name']
                        page_in_kb = db_details['Page Size']
                break
            else:
                input('Not valid - ' + menu_invalid + e_cont)
        else:
            input('Not INT - ' + menu_invalid + e_cont)
    while True:
        local_input[1] = input('What type of storage will your DB use? (1 = gp2, 2 = Io1): ')
        if local_input[1].isdigit():
            if int(local_input[1]) == 1 or int(local_input[1]) == 2:
                break
            else:
                input('Not 1 or 2 - ' + db_instance_invalid + e_cont)
        else:
            input('Not INT - ' + db_instance_invalid + e_cont)
    while True:
        local_input[2] = input('What is the database page size in KB (default ' + page_in_kb + '): ')
        if len(local_input[2]) == 0:
            local_input[2] = page_in_kb
            break
        else:
            if local_input[2].isdigit():
                if int(local_input[2]) > 0 and int(local_input[2]) < 33:
                    break
                else:
                    input(page_num_invalid + e_cont)   
            else:
                input(page_num_invalid + e_cont)
    while True:
        local_input[3] = input('What is the desired IOPS?: ')
        if local_input[3].isdigit():
            if int(local_input[1]) == 1:
                if int(local_input[3]) > 0 and int(local_input[3]) <= 40000:
                    break
                else:
                    input('Out of range - ' + iops_invalid + e_cont)
            else:
                if int(local_input[3]) in num_range:
                    break
                else:
                    input('Not 1000 - ' + range_invalid + e_cont)
        else:
            input('Not INT - ' + iops_invalid + e_cont)
    return (local_input)

# This functions performs calculations based on the user's input and 
# provides the output to the user.
def calc_db_instance(rds_type: str, db_instance: int, page: int, iops: int):
    max_rps = iops * page
    gp2_volume_size = math.ceil(iops / 3)
    gp2_disk_throughput = math.ceil(iops * ((page * 8)/1000))
    io1_size = math.ceil(iops / 50)
    main_screen()
    print('You plan to use the RDS type ' 
            + str(rds_type)
            + ' with a page size of ' 
            + str(page)
            + 'KB.\n')
    print(str(iops), 
            'IOPS multiplied by a page size of', 
            str(page), 
            'KB will produce\n  up to', 
            str(max_rps),
            'KB read per second.')
    print('To achieve ' 
            + str(iops),
            'IOPS you will need disk throughput of at least', 
            str(gp2_disk_throughput), 
            'Mbps.')
    print('\t(IOPS * ((page size * 8)/1000))\n')
    print('If you choose general-purpose SSD (gp2) storage, your DB instance will need') 
    print('  a disk volume that is at least', str(gp2_volume_size), 'GB.')
    print('\t(disk size = IOPS/3 (3 IOPS per GB up to 10000 IOPS per volume))\n')
    print('If you choose provisioned IOPS (Io1) storage, your DB instance will need')
    print('  a disk volume that is at least', str(io1_size), 'GB.')
    print('\t(disk size = IOPS/50)')
    print('\t(50 IOPS per GB up to 32K for MS SQL and 40K for all others.)')
    return None

# Script execution
script_intro()
user_input = get_input()
calc_db_instance(
                rds_type = str(user_input[0]), 
                db_instance = int(user_input[1]), 
                page = int(user_input[2]), 
                iops = int(user_input[3])
                )