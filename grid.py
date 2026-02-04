

grid = open('data/ascii-art.txt', 'r')
def identify():
    GRID_LIST = list()
    for row in grid:
        for x in range(39):
            if row[x] == 'A':
                GRID_LIST.append('wall')
            if row[x] == 'G':
                GRID_LIST.append('ghost')
            if row[x] == 'E':
                GRID_LIST.append('food')
            if row[x] == 'P':
                GRID_LIST.append('eater')
            if row[x] == ' ':
                GRID_LIST.append('blacktile')
        GRID_LIST.append('newline')
    return GRID_LIST
            
        
        
        
    

