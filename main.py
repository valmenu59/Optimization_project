from docplex.mp.model import Model
import datetime as dt

# h: number of days in the planning horizon
# J, the set of days involved in the planning (J = {1..h})
# W, the set of weekends involved in the planning (W = {1..7}), h -> always multiple of 7
# E, set of employees
# P, set of shift types

class Shift:
    """
    d_p: (int) duration time (in minutes)
    i_p: list(Shift) the set of shift types that cannot be assigned immediately
    u_jp: (int) the number of staff required for shift type p on day j in J
    """
    def __init__(self, duration: int, shift_type, number_staff_required: int):
        self.d_p = duration
        self.i_p = shift_type
        self.u_jp = number_staff_required

class Employee:
    """
    id: (str) employee id

    r_e: (int) the set of days when this employee does not work (days off)
    t_e_min: (int) minimum total working time (in min)
    t_e_max: (int) maximum total working time (in min)
    c_e_min: (int) minimum number f consecutive working shifts that must work
    c_e_max: (int) maximum number f consecutive working shifts that must work
    r_e_min: (int) minimum number of consecutive days off to be assigned
    w_e_max: (int) maximum number of weekends that he can work
    m_e_max: maximum number of days that can work on shift type p
    """
    def __init__(self, id: str, r_e: int, t_e_min: int, t_e_max: int, c_e_min: int, c_e_max: int, r_e_min: int, w_e_max: int, m_e_max: int):
        self.id = id
        self.r_e = r_e
        self.t_e_min = t_e_min
        self.t_e_max = t_e_max
        self.c_e_min = c_e_min
        self.c_e_max = c_e_max
        self.r_e_min = r_e_min
        self.w_e_max = w_e_max
        self.m_e_max = m_e_max



def read_txt_file(file_name: str):
    sections = ["SECTION_HORIZON", "SECTION_SHIFTS",
                "SECTION_STAFF", "SECTION_DAYS_OFF", "SECTION_SHIFT_ON_REQUESTS",
                "SECTION_SHIFT_OFF_REQUESTS", "SECTION_COVER"]

    duration = 0

    try:
        with open(file_name, "r") as f:
            section_number = -1
            for line in f:
                line = line.strip()
                print("line: ", line)
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
                    pass
                elif section_number == 2:
                    pass
                elif section_number == 3:
                    pass
                elif section_number == 4:
                    pass
                elif section_number == 5:
                    pass
                elif section_number == 6:
                    pass

    except FileNotFoundError as e:
        print("file not found")
    except Exception as e:
        print(e)



"""
# model
with Model(name='test_cplex') as md:
    # Variables
    x = md.continuous_var(name='x', lb=0)
    y = md.continuous_var(name='y', lb=0)

    # constraints
    md.add_constraint(x + y <= 10)

    # objective
    md.maximize(x + 2*y)

    # resolution
    sol = md.solve()

    if sol:
        print(f"Succès ! La valeur optimale est : {sol.objective_value}")
    else:
        print("Erreur lors de la résolution.")

"""



def main():
    read_txt_file("Instance3.txt")



if __name__ == "__main__":
    main()