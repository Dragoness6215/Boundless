import random

grid = [[[], [], [], [], [], [], []],
        [[], [    ], [    ], [    ], [    ], [    ], []], 
            [[], [    ], [    ], [    ], [    ], [    ], []], 
                [[], [    ], [    ], [3, 3], [    ], [    ], []], 
                    [[], [    ], [    ], [    ], [    ], [    ], []], 
                        [[], [    ], [    ], [    ], [    ], [    ], []], 
        [[], [], [], [], [], [], []]]

biomes=[['Tundra','Plains', 'Plains', 'Desert','Desert'], 
        ['Tundra', 'Plains', 'Plains', 'Desert', 'Desert'],
        ['Tundra', 'Taiga', 'Savana', 'Savana', 'Savana'],
        ['Tundra', 'Taiga', 'Forest', 'Forest', 'Forest'],
        ['Tuundra', 'Taiga', 'Swamp', 'Swamp', 'Rainforest']]

currentIndex = [3,3]
directions = [ "northeast", "east", "southeast", "southwest",  "west", "northwest"]
neighbors = [[-1, 1], [0, 1], [1, 0], [1, -1], [0, -1], [-1, 0]]

##Moves position on grid and returns new biome if applicable
def move(direction):
    global currentIndex
    newIndex = currentIndex.copy()
    playerDirec = directions.index(direction)

    ##Creates index for new hex and updates values based on direction using hexagon grid based neighbor values
    newIndex[0] += neighbors[playerDirec][0]
    newIndex[1] += neighbors[playerDirec][1]
    
    ##If index not in grid, abort code
    if newIndex[0] < 1 or newIndex[0] > 5 or newIndex[1] < 1 or newIndex[1] > 5:
        return "Index not currently available: Please try a different direction."
    
    ##If already explored tile, return that biome
    if grid[newIndex[0]][newIndex[1]]:
        currentIndex = newIndex
        return ["You have moved to a previously discovered %s biome." % getBiome(), 0]
    
    ##Checks how many neighbors hex has
    newNeighbors = []
    for index in neighbors:
        if grid[newIndex[0] + index[0]][newIndex[1] + index[1]]:
            newNeighbors.append(grid[newIndex[0] + index[0]][newIndex[1] + index[1]])
    
    ##Returns the least common pair of rainfall/temperature among neighbors
    lowestFrequency = 6
    leastCommon = []
    for hex in newNeighbors:
        currFrequency = newNeighbors.count(hex)
        if hex in leastCommon:
            continue
        elif currFrequency == lowestFrequency:
            leastCommon.append(hex)
        elif currFrequency < lowestFrequency:
            leastCommon = [hex]
            lowestFrequency = currFrequency

    newHex = random.choice(leastCommon).copy()
    
    ##Algorithm to determine how rainfall and temperature change based off six-sided die
    for i in range(2):
        val = newHex[i]
        change = random.randint(1,6)

        ##Only change values if dice rolls a 1 or 6
        if change == 1:
            if val == 1:
                val+=1
            else:
                val-=1
        
        elif change == 6:
            if val == 5:
                val-=1
            else:
                val+=1
        
        newHex[i] = val
    
    ##Updates grid with new pair of hex values
    currentIndex = newIndex
    grid[newIndex[0]][newIndex[1]] = newHex
    return ["Exploring to the %s, you find...\n\na %s biome!" % (direction, getBiome()), 5]

##Returns current biome
def getBiome():
    listval = grid[currentIndex[0]][currentIndex[1]]
    return biomes[listval[0]-1][listval[1]-1]