from functools import reduce
from random import randint, random
from num_base_converter import *
from hashlib import md5


class InvalidNumBitsError(Exception):
    pass
    
    
class BinaryClause:
    def __init__(self, sat_bits):
        for bit in sat_bits:
            if bit != "1" and bit != "0" and bit != "X":
                raise ValueError("Clause satisfiable bits must be 1, 0 or X")
        self.sat_bits = sat_bits
        self.num_bits = len(sat_bits)

    def copy(self):
        return BinaryClause(self.sat_bits)
        
    def __eq__(self, other):
        if not isinstance(other, BinaryClause):
            return False
        return self.sat_bits == other.sat_bits
        
    def __hash__(self):
        return hash(tuple(self.sat_bits))
        
    def __str__(self):
        return self.sat_bits
        
    def bit(self, pos):
        if pos < 0 or pos >= self.num_bits:
            raise ValueError("Valid bit positions lie between 0 and {0:d}".format(pos))
        return self.sat_bits[self.num_bits-1 - pos]
        
    def pos_active_bits(self):        
        return list(map(
            lambda posbit: self.num_bits-1 - posbit[0],
            filter(
                lambda posbit: posbit[1] != "X",
                enumerate(list(self.sat_bits))
            )
        ))
        
    def num_active_bits(self):
        return sum([bit != "X" for bit in self.sat_bits])
        
    def evaluate(self, eval_bits):
        if len(eval_bits) != self.num_bits:
            raise InvalidNumBitsError("Must introduce {0:d} bits for evaluation, introduced {1:d}".format(self.num_bits, len(eval_bits)))
        return all([sat_bit == eval_bit or sat_bit == "X" for eval_bit, sat_bit in zip(list(eval_bits), list(self.sat_bits))])
    
    
class BinaryCostFunction:
    def __init__(self, num_bits):
        if num_bits < 1:
            raise ValueError("num_bits must be 1 or greater")
        self.num_bits = num_bits
        self.clauses = {}
    
    def copy(self):
        self_copy = BinaryCostFunction(self.num_bits)
        for clause, value in self.clauses.items():
            self_copy.add_clause(clause.copy(), value)
        return self_copy
    
    def __str__(self):
        prnt_str = ""
        for clause, value in self.clauses.items():
            prnt_str += str(value) + " * " + str(clause) + "\n"
        if prnt_str == "":
            return "0"
        return prnt_str
    
    def add_clause(self, clause, value):
        if clause.num_bits != self.num_bits:
            raise InvalidNumBitsError("Clause must have {0:d} num_bits, but has {1:d}".format(self.num_bits, clause.num_bits))
        if clause in self.clauses and value == 0:
            self.clauses.pop(clause)
        elif value != 0:
            self.clauses[clause] = value
    
    def evaluate(self, eval_bits):
        if len(eval_bits) != self.num_bits:
            raise InvalidNumBitsError("Must introduce {0:d} bits for evaluation, introduced {1:d}".format(self.num_bits, len(eval_bits)))
        return sum([value * clause.evaluate(eval_bits) for clause, value in self.clauses.items()])

    def min_exhaustively(self):
        best_str = "1" * self.num_bits
        min_val = self.evaluate(best_str)
        for i in range(2**self.num_bits - 1):
            act_str = dec_to_bin(i, self.num_bits)
            act_val = self.evaluate(act_str)
            if act_val < min_val:
                best_str = act_str
                min_val = act_val
        return best_str, min_val

    def max_exhaustively(self):
        best_str = "1" * self.num_bits
        max_val = self.evaluate(best_str)
        for i in range(2**self.num_bits - 1):
            act_str = dec_to_bin(i, self.num_bits)
            act_val = self.evaluate(act_str)
            if act_val > max_val:
                best_str = act_str
                max_val = act_val
        return best_str, max_val

    def num_clauses_less(self, threshold):
        num_clauses = 0
        for i in range(2**self.num_bits - 1):
            act_str = dec_to_bin(i, self.num_bits)
            act_val = self.evaluate(act_str)
            if act_val < threshold:
                num_clauses += 1
        return num_clauses 

    def num_clauses_more(self, threshold):
        num_clauses = 0
        for i in range(2**self.num_bits - 1):
            act_str = dec_to_bin(i, self.num_bits)
            act_val = self.evaluate(act_str)
            if act_val > threshold:
                num_clauses += 1
        return num_clauses   

    def get_values(self):
        return list(map(lambda cv: cv[1], self.clauses.items()))

    def generate_hash_ID(self):
        h = md5()
        h.update(str(self).encode("utf-8"))
        return h.hexdigest()


def generate_random_bc(num_bits, spec):
    clause_str = ""
    for _ in range(num_bits):
        clause_str += chr(48 + randint(0, 1)) if random() <= spec else "X"
    return BinaryClause(clause_str)


def generate_random_bcf(num_bits, spec, v_min, v_max, c_min, c_max):
    random_bcf = BinaryCostFunction(num_bits)
    for _ in range(randint(c_min, c_max)):
        random_bcf.add_clause(generate_random_bc(num_bits, spec), randint(v_min, v_max))
    return random_bcf