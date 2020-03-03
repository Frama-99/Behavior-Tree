import time
import random
import argparse
import logging

blackboard = {
    "BATTERY_LEVEL": int,
    "SPOT": bool,
    "GENERAL": bool,
    "DUSTY_SPOT": bool,
    "HOME_PATH": "",
    "DOCKED": False
}

battery_consumption = {
    "find_home": 1,
    "go_home": 3,
    "dock": 1,
    "clean_spot": 2,
    "done_spot": 0,
    "general_cleaning": 1,
    "done_general": 0,
    "do_nothing": 0.1
}

s = "SUCCESS"
f = "FAILURE"
r = "RUNNING"

class Node:
    def __init__(self, name):
        self.name = name
        self.children = [] # list of children of a given node
        self.status = ""   # succeeded, failed, or running

class Composite(Node):
    pass

class Sequence(Composite):
    def run(self):
        self.status = s # if we make it through each children without failing, then we succeeded
        for c in self.children:
            c.run()
            if c.status == r:
                self.status = r
                break
            if c.status == f:
                self.status = f
                break
        logging.debug("%s's status is %s", self.name, self.status)

class Selector(Composite):
    def run(self):
        self.status = f # if we make it through each children without succeeding, then we have failed
        for c in self.children:
            c.run()
            if c.status == r:
                self.status = r
                break # A selector node would stop progressing through the nodes and return running if one of its children is running
            if c.status == s:
                self.status = s
                break
        logging.debug("%s's status is %s", self.name, self.status)
        
class Priority(Composite):
    def run(self):
        for c in self.children:
            c.run()
            if c.status == r:
                self.status = r
                break
        logging.debug("%s's status is %s", self.name, self.status)

class Task(Node):
    def __init__(self, name, status):
        super().__init__(name)
        self.status = status
    def run(self):
        if self.name == "done_general":
            blackboard["GENERAL"] = False
            print("General cleaning has finished.")
        elif self.name == "done_spot":
            blackboard["SPOT"] = False
            print("Done with spot cleaning.")
        elif self.name == "clean_spot":
            print("Cleaning spot...")
        elif self.name == "general_cleaning":
            print("General cleaning...")
        elif self.name == "find_home":
            print("Finding Home...")
            Home = [random.randrange(1, 50), random.randrange(1, 50)]
            blackboard["HOME_PATH"] = Home 
            print("Found home at ", blackboard["HOME_PATH"])
        elif self.name == "go_home":
            print("Going home at ", blackboard["HOME_PATH"])
        elif self.name == "dock":
            print("Docking...")
            blackboard["DOCKED"] = True
            print("Docking complete.")
        elif self.name == "do_nothing":
            print("Doing nothing...")
        
        logging.debug("%s's status is %s", self.name, self.status)

        blackboard["BATTERY_LEVEL"] = blackboard["BATTERY_LEVEL"] - battery_consumption[self.name]
        print(round(battery_consumption[self.name],1), "% battery was consumed. Battery level is now", round(blackboard["BATTERY_LEVEL"], 1), "%")

class Condition(Node):
    def __init__(self, name):
        super().__init__(name)
        # self.run()
    def run(self):
        if self.name == "spot":
            if blackboard.get("SPOT") == False:
                self.status = f
            else:
                self.status = s
                print("Running spot cleaning sequence...")
        elif self.name == "dusty_spot":
            if blackboard.get("DUSTY_SPOT") == False:
                self.status = f
                print("No dusty spot found while performing general cleaning.")
            else: 
                self.status = s
                print("Dusty spot found while performing general cleaning.")
        elif self.name == "battery<30%":
            if blackboard.get("BATTERY_LEVEL") < 30:
                self.status = s
                print("Battery is less than 30%. Starting charging sequence.")
            else: self.status = f
        elif self.name == "general":
            if blackboard.get("GENERAL") == False:
                self.status = f
            else:
                self.status = s
                print("Running general cleaning sequence...")
        logging.debug("%s's status is %s", self.name, self.status)

class Decorator(Node):
    pass

class Negation(Decorator):
    def __init__(self, name):
        super().__init__(name)
    def run(self):
        self.children[0].run()
        if self.children[0].status == s:
            self.status = f
        elif self.children[0].status == f:
            self.status = s
        else:
            raise ValueError
        logging.debug("%s's status is %s", self.name, self.status)

class Until_Success(Decorator):
    def __init__(self, name):
        super().__init__(name)
    def run(self):
        if self.children[0].status != s:
            self.children[0].run()
            self.status = self.children[0].status
        else:
            self.status = s
        logging.debug("%s's status is %s", self.name, self.status)

class Timer(Decorator):
    def __init__(self, name, time):
        super().__init__(name)
        blackboard[self.name] = time
    def run(self):
        if blackboard[self.name] != 0:
            self.children[0].run()
            self.status = r
            blackboard[self.name] = blackboard[self.name] - 1
        else:
            self.children[0].status = s
            self.status = s
        if (blackboard[self.name] >= 0 and self.status == r):
            print(blackboard[self.name], "seconds remaining.")
        if (self.name == "timer1" and blackboard[self.name] == 0):
                blackboard["DUSTY_SPOT"] = False
                print("Dusty spot has been cleaned.")

        logging.debug("%s, is %s with %d seconds left.", self.name, self.status, blackboard[self.name])

def get_input():
    while True:
        try:
            blackboard["BATTERY_LEVEL"] = int(input("Enter the Roomba's battery level (Number between 5 and 100): "))
            if blackboard["BATTERY_LEVEL"] > 100 or blackboard["BATTERY_LEVEL"] < 5:
                raise ValueError
        except ValueError:
            print("A valid battery level is between 5 and 100.")
            continue
        else:
            break

    while True:    
        try:
            cleaning_type = int(input("Spot cleaning (1), general cleaning (2), both (3), or do nothing (4)? "))
            if cleaning_type != 1 and cleaning_type != 2 and cleaning_type != 3 and cleaning_type != 4:
                raise ValueError
            else:
                if cleaning_type == 1:
                    blackboard["SPOT"] = True
                    blackboard["GENERAL"] = False
                elif cleaning_type == 2:
                    blackboard["SPOT"] = False
                    blackboard["GENERAL"] = True
                elif cleaning_type == 3:
                    blackboard["SPOT"] = True
                    blackboard["GENERAL"] = True
                elif cleaning_type == 4:
                    blackboard["SPOT"] = False
                    blackboard["GENERAL"] = False
        except ValueError:
            print("Please enter a valid input.")
            continue
        else:
            break
    # There may or may not be a dusty spot during general cleaning
    blackboard["DUSTY_SPOT"] = random.choice([True, False])


def build_bt():
    print("Initializing...")
    ############## ROOT PRIORITY SEQUENCE ##############
    root = Priority("root")

    ############## CHARGING SEQUENCE ##############
    seq_charge = Sequence("seq_charge")
    battery = Condition("battery<30%")
    find_home = Task("find_home", s)
    go_home = Task("go_home", s)
    dock = Task("dock", r)

    seq_charge.children = [battery, find_home, go_home, dock]

    ############## CLEANING SEQUENCES ##############
    sel_clean = Selector("sel_clean")

    # SPOT CLEANING
    seq_spot = Sequence("seq_spot")
    spot = Condition("spot")
    timer2 = Timer("timer2", 20)
    clean_spot = Task("clean_spot", r)
    done_spot = Task("done_spot", s)

    seq_spot.children = [spot, timer2, done_spot]
    timer2.children = [clean_spot]

    # GENERAL CLEANING
    timer1 = Timer("timer1", 35)
    timer1.children = [clean_spot]
    dusty_spot = Condition("dusty_spot")
    seq1 = Sequence("seq1")
    seq1.children = [dusty_spot, timer1]

    general_cleaning = Task("general_cleaning", r)
    sel1 = Selector("sel1")
    sel1.children = [seq1, general_cleaning]

    neg1 = Negation("neg1")
    neg1.children = [battery]
    seq2 = Sequence("seq2")
    seq2.children = [neg1, sel1]

    until_success = Until_Success("until_success")
    until_success.children = [seq2]
    done_general = Task("done_general", s)
    seq3 = Sequence("seq3")
    seq3.children = [until_success, done_general]

    general = Condition("general")
    seq_general = Sequence("seq_general")
    seq_general.children = [general, seq3]

    # ADD SPOT SEQUENCE AND GENERAL SEQUENCE AS CHILDREN OF CLEAN SELECTOR
    sel_clean.children = [seq_spot, seq_general]

    ############## DO NOTHING ##############
    do_nothing = Task("do_nothing", s)

    # ADD THREE CLASSES OF ACTIONS TO ROOT NODE
    root.children = [seq_charge, sel_clean, do_nothing]
    print("\n")
    return root

def run(root):
    Online_time = 0

    while True:
        # Changing the environment
        Online_time = Online_time + 1
        print("Online Time: ", Online_time, "s")

        # Change Robot (Battery, etc.)
        if blackboard["BATTERY_LEVEL"] == 100 and blackboard["DOCKED"] == True:
            blackboard["DOCKED"] = False
            print("Undocking and resuming cleaning...")

        if (blackboard["DOCKED"] == True and blackboard["BATTERY_LEVEL"] != 100):
            if (100 - blackboard["BATTERY_LEVEL"]) < 5:
                blackboard["BATTERY_LEVEL"] = blackboard["BATTERY_LEVEL"] + (100 - blackboard["BATTERY_LEVEL"])
            else: blackboard["BATTERY_LEVEL"] = blackboard["BATTERY_LEVEL"] + 5
            print("Charging... Battery level is now", round(blackboard["BATTERY_LEVEL"], 1), "%")
        
        # Evaluate Tree
        else:
            root.run()
            print("\n")

        time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Prints out status of each node",
                    action="store_true")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    get_input()
    root = build_bt()
    run(root)

if __name__ == '__main__':
    main()