import sys

def panic(err_msg):
    print(err_msg)
    sys.exit(1)

def get_precision(num):
    num_str = str(num)
    pos = num_str.find(".")
    if pos != -1:
        comma = num_str[pos:]
        return len(comma) - 1
    return 1
