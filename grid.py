

grid = open('data/ascii-art.txt', 'r')
def identify():
    
    for row in grid:
        for x in range(40):
            if row[x] == 'A':
                yield 'wall'
            if row[x] == 'G':
                yield 'ghost'
            if row[x] == 'E':
                yield 'food'
            if row[x] == 'P':
                yield 'eater'
            if row[x] == ' ':
                yield 'blacktile'
        yield 'newline'
    

        
        
        
    

