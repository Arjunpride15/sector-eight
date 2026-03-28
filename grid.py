

def identify():
    with open('data/ascii-art.txt', 'r') as f:
        for row in f:
            # row.rstrip() removes the invisible \n and trailing spaces
            clean_row = row.rstrip('\n\r') 
            for char in clean_row:
                if char == 'A': yield 'wall'
                elif char == 'G': yield 'ghost'
                elif char == 'E': yield 'food'
                elif char == 'P': yield 'eater'
                elif char == 'M': yield 'magnet'
                elif char == ' ': yield 'blacktile'
            # Tell the canvas to reset X and increment Y
            yield 'newline'
        
        
        
    

