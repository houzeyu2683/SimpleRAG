import utility

for scenario in [1,2,3]: 
    grid = [
        {"chunk": 300, "overlap": 30},
        {"chunk": 500, "overlap": 50},
        {"chunk": 800, "overlap": 80},
        {"chunk": 1000, "overlap": 100},
    ]
    for parameter in grid:
        representation = utility.Representation(scenario)
        representation.createEngine(parameter)
        representation.createData()
        continue
    continue

# scenario = 2
# parameter = {"chunk": 500, "overlap": 50}
# representation = utility.Representation(scenario)
# representation.createEngine(parameter)
# representation.createData()

# scenario = 3
# parameter = {"chunk": 500, "overlap": 50}
# representation = utility.Representation(scenario)
# representation.createEngine(parameter)
# representation.createData()
