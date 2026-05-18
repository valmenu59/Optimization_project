from itertools import count

from docplex.cp.modeler import true
from docplex.mp.model import Model

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

    u_jp: (int) the number of staff required for shift type p on day j in J
    """
    def __init__(self, id: str, duration: int, cannot_follow, number_staff_required: int):
        self.id = id
        self.d_p = duration
        self.cannot_follow = cannot_follow
        # SECTION_COVER
        self.u_jp = number_staff_required

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
    r_e: (int) the set of days when this employee does not work (days off)
    """
    def __init__(self, id: str,  m_e_max: list,  t_e_max: int, t_e_min: int, c_e_min: int, c_e_max: int, r_e_min: int, w_e_max: int,  r_e: int):
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
    def __init__(self, employee: Employee, shift: Shift, day: int, weight: int, is_off_request: bool):
        self.employee = employee
        self.shift = shift
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
                    for elem in section_staff[index][1]:
                        for el in elem.strip("=").split("="):
                            index1.append(str_to_int(el))

                    section_staff[index][1] = index1
                    #print(section_staff[index][1])
                elif section_number == 3:
                    section_days_off.append(transform_line_to_list(line))
                elif section_number == 4:
                    section_shift_on_requests.append(transform_line_to_list(line))
                elif section_number == 5:
                    section_shift_off_requests.append(transform_line_to_list(line))
                elif section_number == 6:
                    section_cover.append(transform_line_to_list(line))

            return duration, section_shift, section_staff, section_days_off, section_shift_on_requests, section_shift_off_requests, section_cover

    except FileNotFoundError as e:
        assert FileNotFoundError("This file is not found")
    except Exception as e:
        assert Exception(e)

def test_model(result, shifts, employees):
    current_employee = ""
    for employee_schedule in result:
        # 1
        constraint_1 = True
        non_working_shift = -1
        # 2
        constraint_2 = True
        current_shift = "/"
        # 3
        list_count_shift = [[0, s.id] for s in shifts]
        constraint_3 = True
        # 4
        total_duration = 0
        constraint_4 = True
        # 5 & 6
        consecutive_day = 0
        max_consecutive_days = 0
        constraint_5 = True
        min_consecutive_days = 1_000_000_000
        constraint_6 = True


        #print(employee_schedule)
        for i, schedule in enumerate(employee_schedule):
            if i == 0:
                current_employee = employee_schedule[0]
                print(f"Employee {current_employee}")
            else:
                # Test constraint n°1
                if i < len(employee_schedule) - 1:
                    # can't work night and the morning next day
                    if employee_schedule[i][2] != "/" and employee_schedule[i + 1][0] != "/":
                        constraint_1 = False
                # count the number of non-working shift per day, results need to be equal at 2 or 3, not 1 or 0
                non_working_shift = schedule.count("/")
                if non_working_shift < 2:
                    constraint_1 = False

                # Test constraint n°2
                last_shift = current_shift
                if non_working_shift != 3:
                    for shift in schedule:
                        if shift != "/":
                            current_shift = shift
                else:
                    current_shift = "/"
                for s in shifts:
                    # verify if last shift is in the list cannot_follow
                    if last_shift == s.id:
                        if current_shift in s.cannot_follow:
                            constraint_2 = False

                # Test constraint n°3
                if non_working_shift != 3:
                    for shift in schedule:
                        for shift_count in list_count_shift:
                            #print(shift_count)
                            if shift == shift_count[1]:
                                shift_count[0] += 1
                for e in employees:
                    if e.id == current_employee:
                        for j in range(0, len(e.m_e_max), 2):
                            # ex of e.m_e_max -> ['E', 14, 'D', 14, 'L', 0] (in txt file: E=14|D=14|L=0)
                            if e.m_e_max[j] == list_count_shift[j // 2][1]:
                                if list_count_shift[j // 2][0] > e.m_e_max[j + 1]:
                                    constraint_2 = False

                # Test constraint n°4
                if non_working_shift:
                    for shift in schedule:
                        if shift != "/":
                            for s in shifts:
                                if s.id == shift:
                                    total_duration += s.d_p
                for e in employees:
                    if e.id == current_employee:
                        constraint_4 = e.t_e_min <= total_duration <= e.t_e_max

                # Test constraint n°5 & 6
                if non_working_shift != 3:
                    consecutive_day += 1
                    # Max
                    if consecutive_day > max_consecutive_days:
                        max_consecutive_days = consecutive_day
                else:
                    if consecutive_day <= min_consecutive_days and consecutive_day != 0: # ignore for days and force for the last day
                        min_consecutive_days = consecutive_day
                    consecutive_day = 0
                if consecutive_day <= min_consecutive_days and i == len(employee_schedule) - 1 and consecutive_day != 0:  # for the last
                    min_consecutive_days = consecutive_day



        print("Constraint n°1:", end="\t")
        if constraint_1:
            print("\033[92m {}\033[00m".format("PASSED"))
        else:
            #print(f"FAILED   {constraint_1}   {non_working_shift}")
            print("\033[91m {} {} {}\033[00m".format("FAILED", constraint_1, non_working_shift))
        print("Constraint n°2:", end="\t")
        if constraint_2:
            print("\033[92m {}\033[00m".format("PASSED"))
        else:
            print("\033[91m {}\033[00m".format("FAILED"))
        print("Constraint n°3:", end="\t")
        if constraint_3:
            print("\033[92m {}\033[00m".format("PASSED"))
        else:
            print("\033[91m {}\033[00m".format("FAILED"))
        print("Constraint n°4:", end="\t")
        if constraint_4:
            print("\033[92m {}\033[00m".format("PASSED"))
        else:
            print("\033[91m {} duration:{}\033[00m".format("FAILED", total_duration))
        print("Constraint n°5 & 6:", end="\t")
        print(max_consecutive_days, min_consecutive_days)
        print()




def main():
    elements = read_txt_file("Instance3.txt")
    print(elements)

    numbers_days = int(elements[0])
    numbers_shift_per_day = 3

    shifts = []
    for i in range(len(elements[1])):
        # TODO: replace elements[1][i][3] by another things than -1
        # THINK IT IS SECTION COVER
        shifts.append(Shift(elements[1][i][0], elements[1][i][1], elements[1][i][2], -1))

    print(shifts[0].id)
    for i in shifts:
        print(i.cannot_follow)

    employees = []
    for i in range(len(elements[2])):
        # TODO: replace -1
        employees.append(Employee(elements[2][i][0], elements[2][i][1], elements[2][i][2], elements[2][i][3], elements[2][i][4],
                                  elements[2][i][5], elements[2][i][6], elements[2][i][7], -1))

    print(employees[0].m_e_max)

    covers =  []
    for i in range(len(elements[6])):
        covers.append(Cover(elements[6][i][0], elements[6][i][1], elements[6][i][2], elements[6][i][3], elements[6][i][4]))

    ##################
    ### MODEL PART ###
    ##################

    with Model(name = "cplex") as md:
        # variables
        x = md.binary_var_dict([(e.id, d, s.id, ns)
                                for e in employees
                                for d in range(numbers_days)
                                for s in shifts
                                for ns in range(numbers_shift_per_day)
                                ], name = "x"
                               )

        y_minus = md.integer_var_dict([(d, s.id, ns) for d in range(numbers_days) for s in shifts for ns in range(numbers_shift_per_day)], lb=0, name="shortage")
        y_plus = md.integer_var_dict([(d, s.id, ns) for d in range(numbers_days) for s in shifts for ns in range(numbers_shift_per_day)], lb=0, name="surplus")

        # CONSTRAINTS
        # 1st constraint: Each employee can be assigned to only one shift type per day at most
        for e in employees:
            for d in range(numbers_days):
                md.add_constraint(
                    md.sum(x[e.id, d, s.id, ns] for s in shifts for ns in range(numbers_shift_per_day)) <= 1
                )
        # Impossible to work in night and the morning the next day
        for e in employees:
            for d in range(numbers_days - 1):
                night_shifts = md.sum(x[e.id, d, s.id, 2] for s in shifts)
                morning_shifts_plus_one = md.sum(x[e.id, d + 1, s.id, 0] for s in shifts)
                md.add_constraint(night_shifts + morning_shifts_plus_one <= 1)


        # 2nd constraint: Incompatibility in the sequence of certain shift types across consecutive days
        for e in employees:
            for d in range(numbers_days - 1):  # the last day is useless to get
                for s in shifts:
                    for not_follow in s.cannot_follow:
                        day_j = md.sum(x[e.id, d, s.id, ns] for ns in range(numbers_shift_per_day))
                        day_j_plus_one = md.sum(x[e.id, d + 1, not_follow, ns] for ns in range(numbers_shift_per_day))
                        md.add_constraint(day_j + day_j_plus_one <= 1)


        # 3rd constraint: Each employee e is assigned at most m^max(ep) times to shift p
        for e in employees:
            for j in range(0, len(e.m_e_max), 2):
                shift_id = e.m_e_max[j]  # Ex: 'E'
                max_assignments = e.m_e_max[j + 1] # Ex: '14'

                md.add_constraint(
                    md.sum(x[e.id, d, shift_id, ns] for d in range(numbers_days) for ns in range(numbers_shift_per_day)) <= max_assignments
                )

        # 4th constraint: Each employee works a bounded total duration.
        for e in employees:
            total_minutes = md.sum(x[e.id, d, s.id, ns] * s.d_p
                                   for d in range(numbers_days)
                                   for s in shifts
                                   for ns in range(numbers_shift_per_day)
                                   )

            md.add_constraint(total_minutes >= e.t_e_min,
                              ctname=f"min_time_{e.id}")

            md.add_constraint(total_minutes <= e.t_e_max,
                              ctname=f"max_time_{e.id}")

        # 5th constraint: Each employee works at most c^max(e) consecutive days
        """
        for e in employees:
            for d in range(numbers_days):
                print(d  + e.c_e_max)
                if d + e.c_e_max < numbers_days:
                   # md.add_constraint(x[e.id, d, s.id] + x[e.id, d + e.c_e_max, s.id] <= 1)
                   md.add_constraint(x[e.id, d + e.c_e_max , s.id] <= 1)
                   
       """

        # 6th constraint: Each employee works at least c^min(e) consecutive days.
        # 7th constraint: Each employee has a minimum number of consecutive days off.
        # 8th constraint: Each employee e must not work more than w^max(e) weekends (a weekend is considered worked
        #   if the employee works at least one of the two days, Saturday or Sunday)
        # 9th constraint: Each employee does not work on certain days.


        # 10th constraint: Shift coverage constraints, i.e., each shift requires a certain number of staff, but there
        #   may be staff shortages or surpluses which are penalized in the objective function
        cover_dict = None
        for d in range(numbers_days):
            for s in shifts:
                for ns in range(numbers_shift_per_day):
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
            for ns in range(numbers_shift_per_day)
        )

        md.minimize(obj)

        # RESOLUTION
        solution = md.solve()

        #print("# SOLUTION: #")
        #print(solution)
        final_solution = []

        # Print and write the calendar for each employee
        if solution:
            with open(f"results.txt", "w") as f:
                for nb, e in enumerate(employees):
                    print(f"Schedule for the employee {e.id}:")
                    f.write(f"{e.id}\n")
                    final_solution.append([e.id])
                    for d in range(numbers_days):
                        assigned_shift = ["/", "/", "/"]
                        for p in shifts:
                            for ns in range(numbers_shift_per_day):
                                # if solution.get_value(x[e.id, d, p.id]):
                                if solution.get_value(x[e.id, d, p.id, ns]) > 0.5:
                                    assigned_shift[ns] = p.id

                        #f.write(f"{assigned_shift}")
                        shift = "/"
                        for i, val in enumerate(assigned_shift):
                            if val != "/":
                                shift = val
                                f.write(f"{shift}{i}")
                        if shift == "/":
                            f.write(f"{shift}9")
                        final_solution[nb].append(assigned_shift)
                        print(f"Day {d} : {assigned_shift}", end=" ")
                    f.write("\n")
                    print()

            #print(final_solution)
            test_model(final_solution, shifts, employees)
        else:
            assert Exception("There is no solution")



if __name__ == "__main__":
    main()