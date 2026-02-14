from collections import deque

grid = open('data/ascii-art.txt', 'r')
def identify():
    GRID_QUEUES = deque()
    for row in grid:
        for x in range(40):
            if row[x] == 'A':
                GRID_QUEUES.append('wall')
            if row[x] == 'G':
                GRID_QUEUES.append('ghost')
            if row[x] == 'E':
                GRID_QUEUES.append('food')
            if row[x] == 'P':
                GRID_QUEUES.append('eater')
            if row[x] == ' ':
                GRID_QUEUES.append('blacktile')
        GRID_QUEUES.append('newline')
    return GRID_QUEUES

        
        
        
    

