
from sympy.ntheory import isprime, primefactors
from random import getrandbits
from secrets import SystemRandom

from utils import panic


def _generate_prime(bits):
    while True:
        n = getrandbits(bits)
        n |= (1 << bits - 1) | 1
        if isprime(n):
            break
    return n


class Protocol:
    def __init__(self, bits=64):
        self._prime_p = None
        self._prime_q = None
        self._generator = None
        self._secret_random = None
        self._randomizer = None
        self._random_factory = SystemRandom()

        self.bits = bits
        
    @property
    def bits(self):
        return self.__bits

    @bits.setter
    def bits(self, value):
        if value < 64:
            self.__bits = 64
        self.__bits = value

    @property
    def prime_p(self):
        return self._prime_p
    
    @property
    def prime_q(self):
        return self._prime_q

    def _calculate_primes(self):
        self._prime_p = _generate_prime(self.bits)
        self._prime_q = max(primefactors(self.prime_p - 1))
    
    @property
    def generator(self):
        return self._generator

    def _product_generator(self):
        base_h = self._random_factory.randint(2, self._prime_p)
        self._generator = pow(base_h, int((self._prime_p - 1) / self._prime_q), self._prime_p)

    @property
    def secret_random(self):
        return self._secret_random

    def _calculate_secret_random(self):
        self._secret_random = self._random_factory.randint(2, self.prime_q)

    def calculate_public_parameter(self):
        pass

    def setup(self, comm, bit_length):
        pass

    def calculate_randomizer(self, next_parameter, previous_parameter):
        pass

    def encrypt(self, private_value):
        pass


class Product(Protocol):
    def __init__(self, bits):
        super().__init__(bits)

    def setup(self, comm):
        if comm.Get_rank() == 0:
            self._calculate_primes()
            self._product_generator()
            init_data = [self.prime_p, self.prime_q, self.generator]
        else:
            init_data = []

        self._prime_p, self._prime_q, self._generator = comm.bcast(init_data, root=0)
        self._calculate_secret_random()

    def calculate_public_parameter(self):
        return pow(self.generator, self.secret_random, self.prime_p)

    @property
    def randomizer(self):
        return self._randomizer

    def calculate_randomizer(self, next_parameter, previous_parameter):
        previous_inverse = pow(previous_parameter, -1, self.prime_p)
        self._randomizer = pow(next_parameter * previous_inverse, self.secret_random, self.prime_p)

    def encrypt(self, private_value):
        return (private_value * self.randomizer) % self.prime_p


class Sum(Protocol):
    def __init__(self, bits):
        super().__init__(bits)

        self.__p_squared = None

    @property
    def p_squared(self):
        return self.__p_squared

    def setup(self, comm):
        if comm.Get_rank() == 0:
            self._calculate_primes()
            self._product_generator()
            self.__p_squared = self.prime_p * self.prime_p
            self._generator = pow(self.generator, self.prime_p, self.p_squared)
            init_data = [self.prime_p, self.prime_q, self.generator]
        else:
            init_data = []

        self._prime_p, self._prime_q, self._generator = comm.bcast(init_data, root=0)
        if self.p_squared is None:
            self.__p_squared = self._prime_p * self._prime_p
        
        self._calculate_secret_random()

    def calculate_public_parameter(self):
        return pow(self.generator, self.secret_random, self.p_squared)

    def calculate_randomizer(self, next_parameter, previous_parameter):
        previous_inverse = pow(previous_parameter, -1, self.p_squared)
        self._randomizer = pow(next_parameter * previous_inverse, self.secret_random, self.p_squared)

    def encrypt(self, private_value):
        return ((1 + private_value * self._prime_p) * self._randomizer) % self.__p_squared