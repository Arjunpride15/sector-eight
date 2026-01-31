

grid = open('data/ascii-art.txt', 'r')
#print(grid.readlines())
GRID_LIST = grid.readlines()
PROPER_GRID_STR = None
def identify():
    global GRID_DTR, PROPER_GRID_STR
    for row in GRID_LIST:
        for i in range(39):
            if row[i] == 'A':
                return 'wall'
            elif row[i] == 'P':
                return 'eater'
            elif row[i] == 'G':
                return 'ghost'
            elif row[i] == 'E':
                return 'food'
            elif row[i] ==' ':
                return 'empty'
            else:
                return None
        return 'newrow'
        
        
    

