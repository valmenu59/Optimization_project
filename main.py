from docplex.mp.model import Model
import xml.etree.ElementTree as xml_tree
import warnings
import argparse

NON_WORKING_SHIFT = "//"
NUMBER_SHIFTS_PER_DAY = 3

# h: number of days in the planning horizon
# J, the set of days involved in the planning (J = {1..h})
# W, the set of weekends involved in the planning (W = {1..7}), h -> always multiple of 7
# E, set of employees
# P, set of shift types

class Shift:
    """
    id: (str) shift id
    d_p: (int) duration time (in minutes)
    cannot_follow: list(Shift) [i_p] the set of shift types that cannot be assigned immediately
    """
    def __init__(self, id: str, duration: int, cannot_follow):
        # force to have 2 characters for id
        self.id = id
        self.d_p = duration
        self.cannot_follow = cannot_follow

class Employee:
    """
    id: (str) employee id
    m_e_max: [(Shift, int)] maximum number of days that can work on shift type p
    t_e_max: (int) maximum total working time (in min)
    t_e_min: (int) minimum total working time (in min)
    c_e_max: (int) maximum number f consecutive working shifts that must work (nombre de jour consécutif qu'il peut travailler au max)
    c_e_min: (int) minimum number f consecutive working shifts that must work
    r_e_min: (int) minimum number of consecutive days off to be assigned (nombre de jour off minimum consécutif)
    w_e_max: (int) maximum number of weekends that he can work
    # SECTIONS_DAYS_OFF
    r_e: [int] the set of days when this employee does not work (days off)
    """
    def __init__(self, id: str,  m_e_max: list,  t_e_max: int, t_e_min: int, c_e_max: int, c_e_min: int, r_e_min: int, w_e_max: int,  r_e: list[int]):
        # SECTION_STAFF
        self.id = id
        self.m_e_max = m_e_max
        self.t_e_max = t_e_max
        self.t_e_min = t_e_min
        self.c_e_max = c_e_max
        self.c_e_min = c_e_min
        self.r_e_min = r_e_min
        self.w_e_max = w_e_max
        # SECTION_DAYS_OFF
        self.r_e = r_e

class ShiftEmployee:
    """
    employee: Employee concerned
    shift: Shift concerned

    """
    def __init__(self, employee_id: str, shift_id: str, day: int, weight: int, is_off_request: bool):
        self.employee = employee_id
        self.shift = shift_id
        self.day = day
        self.weight = weight
        self.is_off_request = is_off_request



class Cover:
    def __init__(self, day: int, shift_id: str, requirement: int, weight_under: int, weight_over):
        self.day = day
        self.shift_id = shift_id
        self.requirement = requirement
        self.weight_under = weight_under
        self.weight_over = weight_over









def str_to_int(elem):
    try:
        return int(elem)
    except ValueError:
        return elem


def convert_str_1_character_to_2(val: str):
    if type(val) == str and len(val) == 1:
        return "*" + val
    return val

def transform_line_to_list(line: str):
    elements = []
    for x in line.strip(",").split(","):
        if not("|" in x):
            elements.append(str_to_int(x))

        else:
            elements.append([])
            for y in x.strip("|").split("|"):
                elements[-1].append(str_to_int(y))
    return elements



def read_txt_file(file_name: str):
    sections = ["SECTION_HORIZON", "SECTION_SHIFTS",
                "SECTION_STAFF", "SECTION_DAYS_OFF", "SECTION_SHIFT_ON_REQUESTS",
                "SECTION_SHIFT_OFF_REQUESTS", "SECTION_COVER"]

    duration = 0
    section_shift = []
    section_staff = []
    section_days_off = []
    section_shift_on_requests = []
    section_shift_off_requests = []
    section_cover = []

    try:
        with open(file_name, "r") as f:
            section_number = -1
            for line in f:
                line = line.strip()
                # print("line: ", line)
                if line in sections:
                    section_number += 1
                elif line.startswith("#") or line == "":
                    pass


                elif section_number == 0:
                    try:
                        duration = int(line)
                    except ValueError:
                        assert "this is not a number"
                elif section_number == 1:
                    section_shift.append(transform_line_to_list(line))
                    # The goal here is to have a list the second index of section_shift even there is nothing or
                    # one element
                    # For example: _ -> []
                    #              'E' -> ['E']
                    #              'E|G|K' -> ['E', 'G', 'K']
                    index = len(section_shift) - 1
                    try:
                        if len(section_shift[index][2]) <= 1:
                            shift_cannot_follow = [section_shift[index][2]]
                            # print(shift_cannot_follow)
                        else:
                            shift_cannot_follow = section_shift[index][2]
                    except IndexError:
                        shift_cannot_follow = []
                    if len(section_shift[index]) <= 2:
                        section_shift[index].append(shift_cannot_follow)
                    else:
                        section_shift[index][2] = shift_cannot_follow # erase this specific index



                elif section_number == 2:
                    section_staff.append(transform_line_to_list(line))
                    index = len(section_staff) - 1
                    #print(section_staff[index][1])

                    # Here: before we have for example ['E=14', 'D=14', 'L=0']
                    # The goal here is to get only number and letter like this example: ['E', 14, 'D', 14, 'L', 0]
                    # Even: letter, odd: number
                    index1 = []
                    elements_list = section_staff[index][1]
                    for elem in elements_list:
                        # Normal case
                        if len(elem) > 1:
                            parts = elem.split("=")

                            if len(parts) == 2:
                                letter = parts[0].strip()
                                number = parts[1].strip()

                                index1.append(letter)
                                index1.append(str_to_int(number))
                        # particular case for the file n°1
                        else:
                            if elem != "=":
                                index1.append(str_to_int(elem))

                    # also for the particular case of file n°1
                    if len(index1) == 3:
                        index1[1] = str_to_int(str(index1[1]) + str(index1[2]))
                        index1.pop()

                    section_staff[index][1] = index1
                elif section_number == 3:
                    section_days_off.append(transform_line_to_list(line))
                elif section_number == 4:
                    section_shift_on_requests.append(transform_line_to_list(line))
                elif section_number == 5:
                    section_shift_off_requests.append(transform_line_to_list(line))
                elif section_number == 6:
                    section_cover.append(transform_line_to_list(line))

            # section_days_off can be merged with section_staff
            for elem in section_days_off:
                #print(elem)
                for staff in section_staff:
                    #print(elem, staff[0])
                    if elem[0] == staff[0]:
                        staff.append(elem[1:])
                        break
            for staff in section_staff:
                if len(staff) == 8:
                    staff.append([])
            #section_days_off = None
            return duration, section_shift, section_staff, [], section_shift_on_requests, section_shift_off_requests, section_cover

    except FileNotFoundError as e:
        #assert FileNotFoundError("This file is not found")
        print("\n\033[91m {}\033[00m\n".format(f"It is not possible to open the file {file_name}"))
        return None
    except Exception as e:
        print("\n\033[91m {}\033[00m\n".format(f"An unknown error was occurred for the file {file_name}: {e}"))
        return None


def print_test(constraint_number: int, is_satisfied: bool, tolerance_satisfied: bool, text_failed: str = ""):
    print(f"Constraint n°{constraint_number}:", end="\t")
    if is_satisfied:
        print("\033[92m {}\033[00m".format("PASSED"))
    else:
        if tolerance_satisfied:
            if text_failed != "":
                print("\033[93m {} {}\033[00m".format("ONLY ONE TIME FAILED", text_failed))
            else:
                print("\033[93m {}\033[00m".format("ONLY ONE TIME FAILED"))
        else:
            if text_failed != "":
                print("\033[91m {} {}\033[00m".format("FAILED", text_failed))
            else:
                print("\033[91m {}\033[00m".format("FAILED"))



def test_model(result, shifts, employees):
    current_employee = ""
    print("\n----------------------------------------------\n")
    print("TEST RESULT:\n")
    count_tests = [0 for _ in range(9)]
    count_tests_with_tolerance = [0 for _ in range(9)]

    for employee_schedule in result:
        constraints = [True for _ in range(9)]
        # allow one time for each employee for each constraint one time which is not satisfied
        tolerances = [True for _ in range(9)]

        # 2
        current_shift = NON_WORKING_SHIFT
        # 3
        list_count_shift = [[0, s.id] for s in shifts]
        # 4
        total_duration = 0
        # 5 & 6
        consecutive_day = 0
        max_consecutive_days = 0
        min_consecutive_days = 1_000_000_000
        number_time_min_consecutive_days_on = 0
        # 7
        consecutive_days_off = 0
        weekend_already_worked = False

        min_consecutive_days_off = 1_000_000_000
        number_time_min_consecutive_days_off = 0
        # 8
        count_weekend_worked = 0
        #print(employee_schedule)

        for i, schedule in enumerate(employee_schedule):
            if i == 0:
                current_employee = employee_schedule[0]
                print(f"Employee {current_employee}")
            else:
                # count number shift worked per day
                non_working_shift = schedule.count(NON_WORKING_SHIFT)

                # Test constraint n°1
                # check only for shifts where there is more than 1 shift worked per day
                if non_working_shift < 2:
                    shift_type = NON_WORKING_SHIFT
                    for shift in schedule:
                        if shift_type == NON_WORKING_SHIFT and shift != NON_WORKING_SHIFT:
                            shift_type = shift
                        elif shift_type != NON_WORKING_SHIFT and shift != NON_WORKING_SHIFT and shift != shift_type:
                            if not(constraints[0]):
                                tolerances[0] = False
                            # at this case, there is more than 2 shift type per day
                            constraints[0] = False

                # Test constraint n°20
                last_shift = current_shift
                if non_working_shift != NUMBER_SHIFTS_PER_DAY:
                    for shift in schedule:
                        if shift != NON_WORKING_SHIFT:
                            current_shift = shift
                else:
                    current_shift = NON_WORKING_SHIFT
                for s in shifts:
                    # verify if last shift is in the list cannot_follow
                    if last_shift == s.id:
                        if current_shift in s.cannot_follow:
                            if not(constraints[1]):
                                tolerances[1] = False
                            constraints[1] = False

                # Test constraint n°3
                if non_working_shift != NUMBER_SHIFTS_PER_DAY:
                    for shift in schedule:
                        for shift_count in list_count_shift:
                            #print(shift_count)
                            if shift == shift_count[1]:
                                shift_count[0] += 1


                # Test constraint n°4
                if non_working_shift != NUMBER_SHIFTS_PER_DAY:
                    for shift in schedule:
                        if shift != NON_WORKING_SHIFT:
                            for s in shifts:
                                if s.id == shift:
                                    total_duration += s.d_p


                # Test constraint n°5 & 6
                if non_working_shift != NUMBER_SHIFTS_PER_DAY:
                    consecutive_day += 1
                    # Max
                    if consecutive_day > max_consecutive_days:
                        max_consecutive_days = consecutive_day
                else:
                    # min
                    if consecutive_day <= min_consecutive_days and consecutive_day != 0: # ignore for days and force for the last day
                        min_consecutive_days = consecutive_day
                        number_time_min_consecutive_days_on = 0
                    elif consecutive_day == min_consecutive_days and consecutive_day != 0:
                        number_time_min_consecutive_days_on += 1
                    consecutive_day = 0
                # min
                if consecutive_day <= min_consecutive_days and i == len(employee_schedule) - 1 and consecutive_day != 0:  # for the last
                    min_consecutive_days = consecutive_day


                # Constraint n°7
                if non_working_shift == NUMBER_SHIFTS_PER_DAY:
                    consecutive_days_off += 1
                else:
                    consecutive_days_off = 0
                if consecutive_days_off <= min_consecutive_days_off and consecutive_days_off != 0:
                    min_consecutive_days_off = consecutive_days_off
                    number_time_min_consecutive_days_off = 0
                elif consecutive_days_off == min_consecutive_days_off and consecutive_days_off != 0:
                    number_time_min_consecutive_days_off += 1


                # Constraint n°8
                if non_working_shift != NUMBER_SHIFTS_PER_DAY and ((i - 1) % 7 == 5 or (i - 1) % 7 == 6):
                    if not weekend_already_worked:
                        count_weekend_worked += 1
                        weekend_already_worked = True
                elif (i - 1) % 7 == 1:
                    # Reinitialization
                    weekend_already_worked = False

                # Global test
                for e in employees:
                    if e.id == current_employee:
                        # Constraint n°3
                        for j in range(0, len(e.m_e_max), 2):
                            # ex of e.m_e_max -> ['E', 14, 'D', 14, 'L', 0] (in txt file: E=14|D=14|L=0)
                            if e.m_e_max[j] == list_count_shift[j // 2][1]:
                                if list_count_shift[j // 2][0] > e.m_e_max[j + 1]:
                                    if not (constraints[2]):
                                        tolerances[2] = False
                                    constraints[2] = False

                        # Constraint n°4
                        #print(e.t_e_min, total_duration, e.t_e_max)
                        constraints[3] = e.t_e_min <= total_duration <= e.t_e_max # only the last is the most important
                        tolerances[3] = constraints[3]

                        # Constraint n°5
                        if max_consecutive_days > e.c_e_max:
                            if not(constraints[4]):
                                tolerances[4] = False
                            constraints[4] = False

                        # Constraint n°6
                        # print(min_consecutive_days, e.c_e_min)
                        if min_consecutive_days < e.c_e_min:
                            # ignore first and last days
                            if i != 1 or i != len(employee_schedule) - 1:
                                if number_time_min_consecutive_days_on > 0:
                                    tolerances[5] = False
                                constraints[5] = False

                        # Constraint n°7
                        if min_consecutive_days < e.r_e_min:
                            if number_time_min_consecutive_days_off > 0:
                                tolerances[6] = False
                            constraints[6] = False

                        # Constraint n°8
                        if count_weekend_worked > e.w_e_max:
                            if not(constraints[7]):
                                tolerances[7] = False
                            constraints[7] = False

                        # Constraint n°9
                        for days_off in e.r_e:
                            #print(schedule, i - 1, e.r_e, days_off)
                            if (i - 1) == days_off and non_working_shift != NUMBER_SHIFTS_PER_DAY:
                                if not (constraints[8]):
                                    tolerances[8] = False
                                constraints[8] = False


        print_test(1, constraints[0], tolerances[0])
        print_test(2, constraints[1], tolerances[1])
        print_test(3, constraints[2], tolerances[2])
        print_test(4, constraints[3], False, "duration: " + str(total_duration)) # No tolerance for this case
        print_test(5, constraints[4], tolerances[4], "max duration: " + str(max_consecutive_days))
        print_test(6, constraints[5], tolerances[5], "min duration: " + str(min_consecutive_days))
        print_test(7, constraints[6], tolerances[6], "min consecutive days off: " + str(min_consecutive_days_off))
        print_test(8, constraints[7], tolerances[7], "count weekend worked:" + str(count_weekend_worked))
        print_test(9, constraints[8], tolerances[8])
        print()
        for i in range(9):
            count_tests_with_tolerance[i] += 1 if tolerances[i] else 0
            count_tests[i] += 1 if constraints[i] else 0

    print("TESTS RESULT")
    for i in range(9):
        print(f"Constraint {i + 1}: ", end="")
        print("{:>16} {:>30}".format(f"{round(count_tests[i] / len(employees) * 100, 2)}% PASSED", f"(with one tolerance: {round(count_tests_with_tolerance[i] / len(employees) * 100, 2)}%)"))


def register_solution_to_txt_file(solution, x, number_days, employees, shifts, filename):
    final_solution = []

    # Print and write the calendar for each employee
    with open(filename, "w") as f:
        for nb, e in enumerate(employees):
            print(f"Schedule for the employee {e.id}:")
            f.write(f"{e.id}\n")
            final_solution.append([e.id])
            for d in range(number_days):
                assigned_shift = [NON_WORKING_SHIFT, NON_WORKING_SHIFT, NON_WORKING_SHIFT]
                for p in shifts:
                    for ns in range(NUMBER_SHIFTS_PER_DAY):
                        # if solution.get_value(x[e.id, d, p.id]):
                        if solution.get_value(x[e.id, d, p.id, ns]) > 0.5:
                            assigned_shift[ns] = p.id

                # f.write(f"{assigned_shift}")
                for value in assigned_shift:
                    f.write(f"{convert_str_1_character_to_2(value)}")
                final_solution[nb].append(assigned_shift)
                print(f"Day {d} : {assigned_shift}", end=" ")
            f.write("\n")
            print()

    # print(final_solution)
    return final_solution

def register_solution_to_ros_file(solution, x, number_days, employees, shifts, filename_number):
    xml_tree.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    # root (roster)
    roster = xml_tree.Element("Roster", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "Roster.xsd"
    })

    # link
    period_file = xml_tree.SubElement(roster, "SchedulingPeriodFile")
    period_file.text = f"instances/Instance{filename_number}.ros"

    for nb, e in enumerate(employees):
        employee_xml = xml_tree.SubElement(roster, "Employee", {
            "ID": e.id
        })

        for d in range(number_days):
            assigned_shift = ""
            for p in shifts:
                for ns in range(NUMBER_SHIFTS_PER_DAY):
                    if solution.get_value(x[e.id, d, p.id, ns]) > 0.5:
                        assigned_shift = p.id
                        break
                if assigned_shift != "":
                    break
            if assigned_shift != "":
                assign = xml_tree.SubElement(employee_xml, "Assign")
                xml_tree.SubElement(assign, "Day").text = str(d)
                xml_tree.SubElement(assign, "Shift").text = assigned_shift

    xml_data = xml_tree.tostring(roster, encoding="utf-8")

    with open(f"results/result{filename_number}.roster.xml", "wb") as f:
        f.write(xml_data)





def calculate_schedule(elements):
    numbers_days = int(elements[0])

    shifts = []
    for i in range(len(elements[1])):
        shifts.append(Shift(
            elements[1][i][0],
            elements[1][i][1],
            elements[1][i][2]
        ))

    employees = []
    for i in range(len(elements[2])):
        for j in range(len(elements[2][i][1])):
            elements[2][i][1][j] = elements[2][i][1][j]
        employees.append(Employee(
            elements[2][i][0],
            elements[2][i][1],
            elements[2][i][2],
            elements[2][i][3],
            elements[2][i][4],
            elements[2][i][5],
            elements[2][i][6],
            elements[2][i][7],
            elements[2][i][8]
        ))

    #print(employees[0].m_e_max)
    #print(employees[0].t_e_max)
    #print(employees[0].t_e_min)
    #print(employees[0].c_e_max)
    #print(employees[0].c_e_min)
    #print(elements[3])

    employees_shifts = []
    for i in range(len(elements[4])):
        #print(elements[4][i])
        # SECTION_SHIFT_ON_REQUESTS
        employees_shifts.append(ShiftEmployee(
            elements[4][i][0],
            elements[4][i][2],
            elements[4][i][1],
            elements[4][i][3],
            False
        ))

    for i in range(len(elements[5])):
        # SECTION_SHIFT_OFF_REQUESTS
        employees_shifts.append(ShiftEmployee(
            elements[5][i][0],
            elements[5][i][2],
            elements[5][i][1],
            elements[5][i][3],
            True
        ))


    covers =  []
    for i in range(len(elements[6])):
        covers.append(Cover(elements[6][i][0], elements[6][i][1], elements[6][i][2], elements[6][i][3], elements[6][i][4]))

    ##################
    ### MODEL PART ###
    ##################

    with Model(name = "cplex") as md:
        # VARIABLES
        # w = 1 if the employee does the same type of shift for the day d, else 0
        # x depends on employee, day, shift
        w = md.binary_var_dict([(e.id, d, s.id) for e in employees for d in range(numbers_days) for s in shifts],
                               name="w")

        # x depends on employee, day, shift, shift_day
        x = md.binary_var_dict([(e.id, d, s.id, ns)
                                for e in employees
                                for d in range(numbers_days)
                                for s in shifts
                                for ns in range(NUMBER_SHIFTS_PER_DAY)
                                ], name = "x"
                               )
        # y -> e.id
        # y count is equal at 1 if the employee worked at day j, else 0
        # y depends on employee, day
        y = md.binary_var_dict([(e.id, d) for e in employees for d in range(numbers_days)], name="y")



        y_minus = md.integer_var_dict([(d, s.id, ns) for d in range(numbers_days) for s in shifts for ns in range(NUMBER_SHIFTS_PER_DAY)], lb=0, name="shortage")
        y_plus = md.integer_var_dict([(d, s.id, ns) for d in range(numbers_days) for s in shifts for ns in range(NUMBER_SHIFTS_PER_DAY)], lb=0, name="surplus")

        num_weekends = numbers_days // 7
        weekend_worked = md.binary_var_dict([(e.id, w_idx) for e in employees for w_idx in range(num_weekends)])

        # CONSTRAINTS
        # 1st constraint: Each employee can be assigned to only one shift type per day at most
        for e in employees:
            for d in range(numbers_days):
                for s in shifts:
                    for ns in range(NUMBER_SHIFTS_PER_DAY):
                        md.add_constraint(x[e.id, d, s.id, ns] <= w[e.id, d, s.id])

                md.add_constraint(md.sum(w[e.id, d, s.id] for s in shifts) <= 1)


        # 2nd constraint: Incompatibility in the sequence of certain shift types across consecutive days
        for e in employees:
            for d in range(numbers_days - 1):  # the last day is useless to get
                for s in shifts:
                    for not_follow in s.cannot_follow:
                        #day_j = md.sum(x[e.id, d, s.id, ns] for ns in range(NUMBER_SHIFTS_PER_DAY))
                        #day_j_plus_one = md.sum(x[e.id, d + 1, not_follow, ns] for ns in range(NUMBER_SHIFTS_PER_DAY))
                        day_j = md.sum(
                            x.get((e.id, d, s.id, ns), 0)
                            for ns in range(NUMBER_SHIFTS_PER_DAY)
                        )

                        day_j_plus_one = md.sum(
                            x.get((e.id, d + 1, not_follow, ns), 0)
                            for ns in range(NUMBER_SHIFTS_PER_DAY)  # Utilise la même variable ici !
                        )


                        md.add_constraint(day_j + day_j_plus_one <= 1)


        # 3rd constraint: Each employee e is assigned at most m^max(ep) times to shift p
        for e in employees:
            for j in range(0, len(e.m_e_max), 2):
                shift_id = e.m_e_max[j]  # Ex: 'E'
                max_assignments = e.m_e_max[j + 1] # Ex: '14'

                md.add_constraint(
                    md.sum(x[e.id, d, shift_id, ns] for d in range(numbers_days) for ns in range(NUMBER_SHIFTS_PER_DAY)) <= max_assignments
                )

        # 4th constraint: Each employee works a bounded total duration.
        for e in employees:
            total_minutes = md.sum(x[e.id, d, s.id, ns] * s.d_p
                                   for d in range(numbers_days)
                                   for s in shifts
                                   for ns in range(NUMBER_SHIFTS_PER_DAY)
                                   )

            md.add_constraint(total_minutes >= e.t_e_min,
                              ctname=f"min_time_{e.id}")

            md.add_constraint(total_minutes <= e.t_e_max,
                              ctname=f"max_time_{e.id}")

        # 5th constraint: Each employee works at most c^max(e) consecutive days
        for e in employees:
            for d in range(numbers_days):
                # day = y if the employee works
                md.add_constraint(
                    y[e.id, d] == md.sum(w[e.id, d, s.id] for s in shifts)
                )
        for e in employees:
            max_days = e.c_e_max + 1
            for d in range(numbers_days - max_days + 1):
                md.add_constraint(
                    md.sum(y[e.id, day] for day in range(d, d + max_days)) <= e.c_e_max,
                )

        # 6th constraint: Each employee works at least c^min(e) consecutive days.
        for e in employees:
            md.add_constraint(
                md.sum(y[e.id, day] for day in range(0, e.c_e_min)) >= e.c_e_min * y[e.id, 0])

            for d in range(1, numbers_days):
                remaining_days = numbers_days - d

                current_window = min(e.c_e_min, remaining_days)

                start_work = y[e.id, d] - y[e.id, d - 1]

                md.add_constraint(
                    md.sum(y[e.id, day] for day in range(d, d + current_window)) >= current_window * start_work
                )

        # 7th constraint: Each employee has a minimum number of consecutive days off.
        for e in employees:
            md.add_constraint(
                md.sum(1 - y[e.id, day] for day in range(0, e.r_e_min)) >= e.r_e_min * (1 - y[e.id, 0])
            )

            for d in range(1, numbers_days):
                remaining_days = numbers_days - d
                current_window = min(e.r_e_min, remaining_days)

                start_off = y[e.id, d - 1] - y[e.id, d]

                md.add_constraint(
                    md.sum(1 - y[e.id, day] for day in range(d, d + current_window)) >= current_window * start_off)


        # 8th constraint: Each employee e must not work more than w^max(e) weekends (a weekend is considered worked
        #   if the employee works at least one of the two days, Saturday or Sunday)
        for e in employees:
            for w_idx in range(num_weekends):
                saturday_idx = 5 + (w_idx * 7)
                sunday_idx = 6 + (w_idx * 7)

                md.add_constraint(weekend_worked[e.id, w_idx] >= y[e.id, saturday_idx])
                md.add_constraint(weekend_worked[e.id, w_idx] >= y[e.id, sunday_idx])

            md.add_constraint(
                md.sum(weekend_worked[e.id, w_idx] for w_idx in range(num_weekends)) <= e.w_e_max)

        # 9th constraint: Employees must not be assigned any shift on their mandatory days off.
        for e in employees:
            if len(e.r_e) > 0:
                for d in e.r_e:
                    if d < numbers_days:
                        md.add_constraint(y[e.id, d] == 0)

        # 10th constraint: Shift coverage constraints, i.e., each shift requires a certain number of staff, but there
        #   may be staff shortages or surpluses which are penalized in the objective function
        cover_dict = None
        for d in range(numbers_days):
            for s in shifts:
                for ns in range(NUMBER_SHIFTS_PER_DAY):
                    cover_dict = {(c.day, c.shift_id): (c.requirement, c.weight_under, c.weight_over) for c in covers}

                    req, w_under, w_over = cover_dict.get((d, s.id), (0, 0, 0))

                    # constraint 10th
                    md.add_constraint(
                        md.sum(x[e.id, d, s.id, ns] for e in employees) == req - y_minus[d, s.id, ns] + y_plus[d, s.id, ns],
                        ctname=f"coverage_d{d}_s{s.id}"
                    )


        # OBJECTIVE
        # The goal here is to minimize the weight (weight = penality), defined in section_cover
        # Here force the model to do working employees
        obj = md.sum(
            y_minus[d, s.id, ns] * cover_dict.get((d, s.id), (0, 0, 0))[1] +  # weight_under
            y_plus[d, s.id, ns] * cover_dict.get((d, s.id), (0, 0, 0))[2]  # weight_over
            for d in range(numbers_days)
            for s in shifts
            for ns in range(NUMBER_SHIFTS_PER_DAY)
        )

        md.minimize(obj)

        # RESOLUTION
        solution = md.solve()

        return solution, x, numbers_days, employees, shifts


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--start", type=int, default=1, help="Number of start instance")
    parser.add_argument("-e", "--end", type=int, default=10, help="Number of end instance")

    args = parser.parse_args()

    if args.start < 1:
        args.start = 1

    if args.end > 24:
        args.end = 24

    if args.end >= 19:
        warnings.warn("Instances superior at 18 can take too much resources for your computer")

    if args.start > args.end:
        args.start, args.end = args.end, args.start # exchange values
    elif args.start == args.end:
        args.end += 1
        if args.end == 25:
            args.end = 24

    for i in range(args.start, args.end + 1):
        print("\n################")
        print(f"### FILE N°{i} ###")
        print("################\n")
        list_from_instance = read_txt_file(f"instances/Instance{i}.txt")
        if list_from_instance:
            elements_schedule = calculate_schedule(list_from_instance)
            # elements_schedule[0] is the solution of the model
            if elements_schedule[0]:
                solution = register_solution_to_txt_file(
                                        elements_schedule[0],
                                        elements_schedule[1],
                                        elements_schedule[2],
                                        elements_schedule[3],
                                        elements_schedule[4],
                                        f"results/result{i}.txt"
                                        )
                register_solution_to_ros_file(
                    elements_schedule[0],
                    elements_schedule[1],
                    elements_schedule[2],
                    elements_schedule[3],
                    elements_schedule[4],
                    i
                )
                test_model(solution, elements_schedule[4], elements_schedule[3])
            else:
                print("\n\033[91m {}\033[00m\n".format(f"There is no solution for the instance n°{i}"))



if __name__ == "__main__":
    main()