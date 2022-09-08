import sys, random, copy
from collections import namedtuple
from math import sqrt, acos, degrees, floor
import argparse as argp

#%% Parameters

# A type for our 3D points.
# In this scenario, units are in km.
Vector3 = namedtuple('Vector3', ['x', 'y', 'z'])

# Center of the earth.
origin = Vector3(0,0,0)

# Speed of light, km/s
speed_of_light_km_s = 299792.0

# Beams per satellite.
beams_per_satellite = 32

# List of valid beam IDs.
valid_beam_ids = [str(i) for i in range(1, beams_per_satellite + 1)]

# Colors per satellite.
colors_per_satellite = 4

# List of valid color IDs.
valid_color_ids = [chr(ord('A') + i) for i in range(0, colors_per_satellite)]

# Self-interference angle, degrees
self_interference_max = 10.0

# Non-Starlink interference angle, degrees
non_starlink_interference_max = 20.0

# Max user to Starlink beam angle, degrees from vertical.
max_user_visible_angle = 45.0

#%% Read sat, user and interferer info and store data

def read_object(object_type:str, line:str, dest:dict) -> bool:
    """
    Given line, of format 'type id float float float', grabs a Vector3 from the last
    three tokens and puts it into dest[id].

    Returns: Success or failure.
    """
    parts = line.split()
    if parts[0] != object_type or len(parts) != 5:
        print("Invalid line! " + line)
        return False
    else:
        ident = parts[1]
        try:
            x = float(parts[2])
            y = float(parts[3])
            z = float(parts[4])
        except:
            print("Can't parse location! " + line)
            return False

        dest[ident] = Vector3(x, y, z)
        return True
    
def read_scenario(filename:str, scenario:dict) -> bool:
    """
    Given a filename of a scenario file, and a dictionary to populate, populates
    the dictionary with the contents of the file, doing some validation along
    the way.

    Returns: Success or failure.
    """

    #print("Reading scenario file " + filename) 

    scenariofile_lines = open(filename).readlines()
    scenario['sats'] = {}
    scenario['users'] = {}
    scenario['interferers'] = {}
    for line in scenariofile_lines:
        if "#" in line:
            # Comment.
            continue

        elif line.strip() == "":
            # Whitespace or empty line.
            continue

        elif "interferer" in line:
            # Read a non-starlink-sat object.
            if not read_object('interferer', line, scenario['interferers']):
                return False

        elif "sat" in line:
            # Read a sat object.
            if not read_object('sat', line, scenario['sats']):
                return False

        elif "user" in line:
            # Read a user object.
            if not read_object('user', line, scenario['users']):
                return False

        else:
            print("Invalid line! " + line)
            return False

    return True

#%% Calculate Angle and Distance

def calculate_angle_degrees(vertex: Vector3, point_a: Vector3, point_b: Vector3) -> float:
    """
    Returns: the angle formed between point_a, the vertex, and point_b in degrees.
    """

    # Calculate vectors va and vb
    va = Vector3(point_a.x - vertex.x, point_a.y - vertex.y, point_a.z - vertex.z)
    vb = Vector3(point_b.x - vertex.x, point_b.y - vertex.y, point_b.z - vertex.z)

    # Calculate each vector's magnitude.
    va_mag = sqrt( (va.x ** 2) + (va.y ** 2) + (va.z ** 2) )
    vb_mag = sqrt( (vb.x ** 2) + (vb.y ** 2) + (vb.z ** 2) )

    # Normalize each vector.
    va_norm = Vector3(va.x / va_mag, va.y / va_mag, va.z / va_mag)
    vb_norm = Vector3(vb.x / vb_mag, vb.y / vb_mag, vb.z / vb_mag)

    # Calculate the dot product.
    dot_product = (va_norm.x * vb_norm.x) + (va_norm.y * vb_norm.y) + (va_norm.z * vb_norm.z)

    # Error can add up here. Bound the dot_product to something we can take the acos of. Scream if it's a big delta.
    dot_product_bound = min(1.0, max(-1.0, dot_product))
    if abs(dot_product_bound - dot_product) > 0.000001:
        print(f"dot_product: {dot_product} bounded to {dot_product_bound}")

    # Return the angle.
    return degrees(acos(dot_product_bound))


def calculate_distance(point_a: Vector3, point_b: Vector3) -> float:
    """
    Returns: the distance between two 3D points.
    """

    # The square root of the difference squared between each compontent.
    x_diff_squared = (point_b.x - point_a.x) ** 2
    y_diff_squared = (point_b.y - point_a.y) ** 2
    z_diff_squared = (point_b.z - point_a.z) ** 2
    return sqrt(x_diff_squared + y_diff_squared + z_diff_squared)

#%% Check Constraints

def check_self_interference(scenario: dict, solution: dict) -> bool:
    """
    Given the scenario and the proposed solution, calculate whether any sat has
    a pair of beams with fewer than self_interference_max degrees of separation.

    Returns: Success or failure.
    """

    # print("Checking no sat interferes with itself...")

    for sat in solution:
        # Grab the list of beams per sat, and the sat's location.
        beams = solution[sat]
        keys = list(beams.keys())
        sat_loc = scenario['sats'][sat]
        # Iterate over all pairs of beams.
        for i in range(len(beams)):
            for j in range(i+1, len(beams)):
                # Grab the colors of each beam, only check for
                # self interference if they are the same color.
                color_a = beams[keys[i]][1]
                color_b = beams[keys[j]][1]
                if color_a != color_b:
                    continue

                # Grab the locations of each user.
                user_a = beams[keys[i]][0]
                user_b = beams[keys[j]][0]
                user_a_loc = scenario['users'][user_a]
                user_b_loc = scenario['users'][user_b]

                # Calculate angle the sat sees from one user to the other.
                angle = calculate_angle_degrees(sat_loc, user_a_loc, user_b_loc)
                if angle < self_interference_max:
                    # Bail if this pair of beams interfere.
                    # print(f"\tSat {sat} beams {keys[i]} and {keys[j]} interfere.")
                    # print(f"\t\tBeam angle: {angle} degrees.")
                    return False

    # Looks good!
    # print("\tNo satellite self-interferes.")
    return True


def check_interferer_interference(scenario: dict, solution: dict) -> bool:
    """
    Given the scenario and the proposed solution, calculate whether any sat has
    a beam that will interfere with a non-Starlink satellite by placing a beam
    that the user would see as within non_starlink_interference_max of a
    non-Starlink satellite.

    Returns: Success or failure.
    """

    # print("Checking no sat interferes with a non-Starlink satellite...")

    for sat in solution:
        # Iterate over users, by way of satellites.
        sat_loc = scenario['sats'][sat]
        for beam in solution[sat]:
            user = solution[sat][beam][0]
            user_loc = scenario['users'][user]
            # Iterate over the non-Starlink satellites.
            for interferer in scenario['interferers']:
                interferer_loc = scenario['interferers'][interferer]

                # Calculate the angle the user sees from the Starlink to the not-Starlink.
                angle = calculate_angle_degrees(user_loc, sat_loc, interferer_loc)

                if angle < non_starlink_interference_max:
                    # Bail if this link is within the interference threshold.
                    # print(f"\tSat {sat} beam {beam} interferes with non-Starlink sat {interferer}.")
                    # print(f"\t\tAngle of separation: {angle} degrees.")
                    return False

    # Looks good!
    # print("\tNo satellite interferes with a non-Starlink satellite!")
    return True


def check_user_coverage(scenario: dict, solution: dict) -> bool:
    """
    Given the scenario and the proposed solution, percentage of users covered
    and verify each covered user is only covered once.

    Returns: Success or failure.
    """

    # print("Checking user coverage...")

    # Build list of covered users.
    covered_users = []

    for sat in solution:
        for beam in solution[sat]:
            user  = solution[sat][beam][0]

            # Bail if the user is already covered elsewhere.
            if user in covered_users:
                # print(f"\tUser {user} is covered multiple times by solution!")
                return False

            # Otherwise mark the user as covered.
            covered_users.append(user)

    # Report how many users were covered.
    total_users_count = len(scenario['users'])
    covered_users_count = len(covered_users)
    # print(f"{(covered_users_count / total_users_count) * 100}% of {total_users_count} total users covered.")
    return True


def check_user_visibility(scenario: dict, solution: dict) -> bool:
    """
    Given the scenario and the proposed solution, calculate whether all users
    can see their assigned satellite.

    Returns: Success or failure.
    """

    # print("Checking each user can see their assigned satellite...")

    for sat in solution:
        for beam in solution[sat]:
            user = solution[sat][beam][0]

            # Grab the user and sat's position.
            user_pos = scenario['users'][user]
            sat_pos = scenario['sats'][sat]

            # Get the angle, relative to the user, between the sat and the
            # center of the earth.
            angle = calculate_angle_degrees(user_pos, origin, sat_pos)

            # User terminals are unable to form beams too far off of from vertical.
            if angle <= (180.0-max_user_visible_angle):

                # Elevation is relative to horizon, so subtract 90 degrees
                # to convert from origin-user-sat angle to horizon-user-sat angle.
                elevation = str(angle - 90)
                # print(f"\tSat {sat} outside of user {user}'s field of view.")
                # print(f"\t\t{elevation} degrees elevation.")
                # print(f"\t\t(Min: {90-max_user_visible_angle} degrees elevation.)")

                return False

    # Looks good!
    # print("\tAll users' assigned satellites are visible.")
    return True


# Check constraints

def check_all_constraints(scenario: dict, solution: dict) -> bool:
    if not check_user_coverage(scenario, solution):
        return False
    if not check_user_visibility(scenario, solution):
        return False
    if not check_self_interference(scenario, solution):
        return False
    if not check_interferer_interference(scenario, solution):
        # print("Solution contained a beam that could interfere with a non-Starlink satellite.")
        return False
    # print("\nSolution passed all checks!\n")
    return True

#%% Functions

# Calculate coverage rate
def cal_coverage_rate(scenario: dict, solution: dict) -> float:
    """
    Given the scenario and the proposed solution, percentage of users covered
    and verify each covered user is only covered once.

    Returns: Coverage rate
    """
    # Build list of covered users.
    covered_users = []

    for sat in solution:
        for beam in solution[sat]:
            user  = solution[sat][beam][0]
            if user in covered_users:
                print("Already covered ! ", user)
            covered_users.append(user)

    # Report how many users were covered.
    total_users_count = len(scenario['users'])
    covered_users_count = len(covered_users)
    coverage_rate = covered_users_count / total_users_count
    return coverage_rate

def beam_planning(scenario: dict, usr_list: list, sat_list: list):
    solution = {}
    color = valid_color_ids
    usr_planning_list = copy.deepcopy(usr_list)
    
    for sat_id in sat_list:
        beam_id = 1
        beam_dict = {}
        i = 0
        while i < len(usr_planning_list):
            color_id = color[beam_id % 4]
            beam_dict[beam_id] = (usr_planning_list[i], color_id)
            solution[sat_id] = beam_dict

            if (check_all_constraints(scenario, solution)):
                beam_id = beam_id + 1
                usr_planning_list.remove(usr_planning_list[i])
                if (beam_id > beams_per_satellite):
                    break
            else:
                solution[sat_id].pop(beam_id)
    coverage_rate = cal_coverage_rate(scenario, solution)
    return solution, coverage_rate

def planning_optimizer(scenario: dict):
    usr_list = [keys for keys in scenario['users']]
    sat_list = [keys for keys in scenario['sats']]
    opti_iter_times = 1
    best_solution = {}
    best_coverage_rate = 0

    for i in range(opti_iter_times):
        #print("Optimization iterations: ", i)
        sat_list = random.sample(sat_list, len(sat_list))
        usr_list = random.sample(usr_list, len(usr_list))
        solution, coverage_rate = beam_planning(scenario, usr_list, sat_list)
        #print(f"{(coverage_rate) * 100}% of total users covered.")
        if coverage_rate > best_coverage_rate:
            best_solution = {}
            best_solution = solution
            best_coverage_rate = coverage_rate
        #print(f"{(best_coverage_rate) * 100}% of total users covered finally.")
    return best_coverage_rate, best_solution

def output_results(best_solution: dict, filename):
    for sat_id in best_solution:
        for beam_id in best_solution[sat_id]:
            print("sat", sat_id, "beam", beam_id, "user", best_solution[sat_id][beam_id][0], "color", best_solution[sat_id][beam_id][1])
            with open("solution.txt", "a") as f:
                f.write("sat"),
                f.write(" ")
                f.write(sat_id)
                f.write(" ")
                f.write("beam")
                f.write(" ")
                f.write(str(beam_id))
                f.write(" ")
                f.write("user")
                f.write(" ")
                f.write(best_solution[sat_id][beam_id][0])
                f.write(" ")
                f.write("color")
                f.write(" ")
                f.write(best_solution[sat_id][beam_id][1])
                f.write("\n")
    

#%% Main

def main() -> int:
    """
    Entry point. Reads inputs, runs checks, outputs stats.

    Returns: exit code.
    """

    # Make sure args are valid.
    argu=argp.ArgumentParser(prog=f"python3.7 {sys.argv[0]}",description='Starlink beam-planning solution')
    argu.add_argument('scenario',metavar='/path/to/scenario.txt',help='Test input scenario.')
    argup=argu.parse_args()
    
    #path = r'C:\Users\liaowenjun\Desktop\starlink\beam-planning\test_cases\\'
    filename = argup.scenario
    # scenario format: scenario['sats'/'users'/'interferers'][index] = Vector3(x, y, z)
    scenario = {}
    # solution format: solution[sat_id][beam_id] = (user_id, color_id)
       
    read_scenario(filename, scenario)
     
    best_coverage_rate, best_solution = planning_optimizer(scenario)
              
    output_results(best_solution, filename)


if __name__ == "__main__":
    sys.exit(main())
