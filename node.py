import argparse
import time
import random

import file_handle
from utils import panic
import homomorphic as he

import threading

from mpi4py import MPI

def exchange(public_parameter):
    # Calculate neighbour ranks
    # Wrap around edge cases
    next_rank = rank + 1
    previous_rank = rank - 1
    if next_rank == size:
        next_rank = 0
    if previous_rank == -1:
        previous_rank = size - 1

    # Create a thread to send to next node
    # and another to send to previous
    send_to_next = threading.Thread(target=comm.send, args=(public_parameter, next_rank))
    send_to_previous = threading.Thread(target=comm.send, args=(public_parameter, previous_rank))
    send_to_previous.start()
    send_to_next.start()

    # Receive from neighbours
    previous_parameter = comm.recv(source=previous_rank)
    next_parameter = comm.recv(source=next_rank)

    # Wait for thread termination
    send_to_previous.join()
    send_to_next.join()

    return previous_parameter, next_parameter

def max_protocol(value):
    if rank == 0:
       digits = random.SystemRandom().randint(10, 20)
    else:
        digits = 0
    digits = comm.bcast(digits, root=0)

    product = he.Product(bits=16)
    product.setup(comm)
    public_parameter = product.calculate_public_parameter()
    previous_parameter, next_parameter = exchange(public_parameter)
    product.calculate_randomizer(next_parameter, previous_parameter)

    computation_round = 0
    while True:
        max_candidate = digits * pow(2, computation_round)
        vote = int(value / max_candidate) + 1
        if vote > 1:
            vote = 0
        else:
            vote = 1
        encrypted_value = product.encrypt(private_value=vote)
        partial_results = comm.allgather(encrypted_value)
        final_result = 1
        for each_result in partial_results:
            final_result *= each_result
        final_result %= product.prime_p
        
        if final_result == 1:
            return max_candidate
        else:
            computation_round += 1


# Main function that 
# implements the core algorithm
def main():
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Add arguments to parser
    parser.add_argument("-p", "--precision", type=int, required=False)
    parser.add_argument("-i", "--input_file", type=str, required=True)
    parser.add_argument("-o", "--output_file", type=str, required=False)

    # Get arguments as a dictionary
    args = vars(parser.parse_args())

    # If output file is not specified
    # default output to 'out.txt' 
    out_file = args["output_file"]
    if out_file is None:
        out_file = "out.txt"
    
    # If precision is not specified
    # default to 1 decimal place
    precision = args["precision"]
    if precision is None:
        precision = 1

    in_file = args["input_file"]
    private_vals = file_handle.read_line_by_line(in_file)    

    

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    round_digits = 2

    w = random.uniform(2.7, 10.5)
    y = random.uniform(1.4, 10.8)
    wy = w * y
    w = round(w, round_digits)
    wy = round(wy, round_digits)
