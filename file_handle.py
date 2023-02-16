from utils import panic

# Read input file line by line 
# and store them in a list of tuples
# This function panics on error and exits
def read_line_by_line(filename):
    private_vals = []

    try:
        with open(filename, 'r') as stdin:
            while True:
                line = stdin.readline()
                if not line:
                    break
                values_pair = split_line(line)
                if values_pair is not None:
                    private_vals.append(values_pair)
    except IOError as io_error:
        panic(io_error)

    return private_vals

# Tokenize each line and return 
# w, y private values as a tuple
def split_line(line):
    # Split line on every ','
    parts = line.split(',')
    if len(parts) != 2:
        return None

    # Split on '=' and trim whitespace from
    # the second element that is the actual value
    w = float(parts[0].split("=") [1].strip())
    y = float(parts[1].split("=") [1].strip())

    return (w, y)
