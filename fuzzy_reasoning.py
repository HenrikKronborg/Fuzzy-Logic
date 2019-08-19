# Functions/Methods for different fuzzy-sets
def triangle(position, x0, x1, x2, clip=None):
    value = 0.0
    if (position >= x0 and position <= x1):
        value = (position - x0) / (x1 - x0)
    elif position >= x1 and position <= x2:
        value = (x2 - position) / (x1 - x0)

    if (value > clip):
        value = clip

    return value

def grade(position, x0, x1, clip):
    value = 0.0;
    if position >= x1:
        value = 1.0
    elif(position <= x0):
        value = 0.0
    else:
        value = (position - x0) / (x1 - x0)

    if (value > clip):
        value = clip

    return value

def reverse_grade(position, x0, x1, clip):
    value = 0.0
    if position <= x0:
        value = 1.0
    elif position >= x1:
        value = 0.0
    else:
        value = (x1 - position) / (x1 - x0)

    if (value > clip):
        value = clip

    return value


# -----------
# Step 1 - Fuzzification
# -----------
def fuzzification(distance, delta):
    # Read the numbers from the given graphs. No clip, so set to 1.0 for all
    # Numbers are read from the graphs where the lines change
    # For example for distance, VerySmall: Line changes at 1 and ends at 2.5
    # This is done because we need a start and end value. For triangles we need a middle value as well
    distanceData = {
        "VerySmall": reverse_grade(distance, x0=1.0, x1=2.5, clip=1.0),
        "Small": triangle(distance, x0=1.5, x1=3.0, x2=4.5, clip=1.0),
        "Perfect": triangle(distance, x0=3.5, x1=5.0, x2=6.5, clip=1.0),
        "Big": triangle(distance, x0=5.5, x1=7.0, x2=8.5, clip=1.0),
        "VeryBig": grade(distance, x0=7.5, x1=9.0, clip=1.0)
    }
    deltaData = {
        "ShrinkingFast": reverse_grade(delta, x0=-4.0, x1=-2.5, clip=1.0),
        "Shrinking": triangle(delta, x0=-3.5, x1=-2.0, x2=-0.5, clip=1.0),
        "Stable": triangle(delta, x0=-1.5, x1=0.0, x2=1.5, clip=1.0),
        "Growing": triangle(delta, x0=0.5, x1=2.0, x2=3.5, clip=1.0),
        "GrowingFast": grade(delta, x0=2.5, x1=4.0, clip=1.0)
    }

    return distanceData, deltaData

# -----------
# Step 2 - Rule Evaluation
# -----------
# Evaluate the graphs declared in fuzziciation. Clipping is used
def AND(x, y):
    return min(x, y)
def OR(x, y):
    return max(x, y)
def NOT(x):
    return 1.0 - x

def ruleEvaluation(distanceData, deltaData):
    rules = {
        "BrakeHard": distanceData["VerySmall"],
        "SlowDown": AND(distanceData["Small"], deltaData["Stable"]),
        "None": AND(distanceData["Small"], deltaData["Growing"]),
        "SpeedUp": AND(distanceData["Perfect"], deltaData["Growing"]),
        "FloorIt": AND(distanceData["VeryBig"], OR(NOT(deltaData["Growing"]), NOT(deltaData["GrowingFast"])))
    }

    return rules

# -----------
# Step 3 - Aggregation
# -----------
# Find the largest action for each x-axis value between -10 and 10
def aggregation(rules):
    values = []

    # Save the largest action for each x value in an array for later use
    for positionX in range(-10, 11):
        value = largestActionYValueAtPosition(positionX, rules)[0]
        values.append(value)

    return values

# Finds the largest action at the given x-axis positoin
def largestActionYValueAtPosition(positionX, rules):
    # Same as in Step 1 - Fuzzification, but this time clip is set to its corresponding rule
    actionData = {
        "BrakeHard": reverse_grade(positionX, x0=-8.0, x1=-5.0, clip=rules["BrakeHard"]),
        "SlowDown": triangle(positionX, x0=-7.0, x1=-4.0, x2=-1.0, clip=rules["SlowDown"]),
        "None": triangle(positionX, x0=-3.0, x1=0.0, x2=3.0, clip=rules["None"]),
        "SpeedUp": triangle(positionX, x0=1.0, x1=4.0, x2=7.0, clip=rules["SpeedUp"]),
        "FloorIt": grade(positionX, x0=5.0, x1=8.0, clip=rules["FloorIt"])
    }

    largestValue = 0.0
    largestAction = "BrakeHard"

    # Finds the largest value and action for that value
    for action, value in actionData.items():
        if value > largestValue:
            largestValue = actionData[action]
            largestAction = action

    return largestValue, largestAction

# -----------
# Step 4 - Defuzzification
# -----------
def defuzzification(values):
    sumXValues = 0.0
    sumValues = 0.0

    # Sum all values
    # Aggregated value*(increasing number from -10 to 10)
    for x, value in enumerate(values, start=-10):
        sumXValues += x * value
        sumValues += value

    return sumXValues / sumValues


if __name__ == '__main__':
    # Input values
    distance = 1
    delta = 1

    # Step 1
    distanceData, deltaData = fuzzification(distance, delta)
    # Step 2
    rules = ruleEvaluation(distanceData, deltaData)
    # Step 3
    values = aggregation(rules)
    # Step 4
    centreOfGravity = defuzzification(values)

    print("Input:\n\tdistance=" + str(distance) + " and delta=" + str(delta))
    print("Centre of Gravity:\n\t" + str(centreOfGravity))
    print("Action performed on this CoG:\n\t", largestActionYValueAtPosition(centreOfGravity, rules)[1])