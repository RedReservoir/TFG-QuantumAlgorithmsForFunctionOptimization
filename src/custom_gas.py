from qiskit import *

from custom_gates import *
from custom_qft import *

from binary_cost_function import *

import math


#Creates an UG gate controlled on the bits of a binary clause
def bc_circuit(m, binary_clause, value):
    n = binary_clause.num_bits
    num_active_bits = binary_clause.num_active_bits()
    pos_active_bits = binary_clause.pos_active_bits()
    
    qc = QuantumCircuit()
    
    qr_ctrl = QuantumRegister(n, "ctrl")
    qr_trgt = QuantumRegister(m, "trgt")
    qc.add_register(qr_ctrl)
    qc.add_register(qr_trgt)
    
    for pos_active_bit in pos_active_bits:
        if binary_clause.bit(pos_active_bit) == "0":
            qc.x(qr_ctrl[pos_active_bit])
    
    ctrl_ug_gate = UG_circuit(m, 2**(1-m)*math.pi*value).to_gate(label = "$R_{%d}(2^{%d} \\pi \\cdot %d)$"%(m, 1-m, value))
    if num_active_bits != 0:
        ctrl_ug_gate = ctrl_ug_gate.control(num_active_bits)
    qc.append(
        ctrl_ug_gate,
        [qr_ctrl[p] for p in pos_active_bits] + qr_trgt[0:m]
    )

    for pos_active_bit in pos_active_bits:
        if binary_clause.bit(pos_active_bit) == "0":
            qc.x(qr_ctrl[pos_active_bit])
     
    return qc


#Creates UG gates for all binary clauses of a cost function
def bcf_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits

    qc = QuantumCircuit()
    
    qr_ctrl = QuantumRegister(n, "ctrl")
    qr_trgt = QuantumRegister(m, "trgt")
    qc.add_register(qr_ctrl)
    qc.add_register(qr_trgt)
    
    for clause, value in binary_cost_function.clauses.items():
        clause_gate = bc_circuit(m, clause, value).to_gate(label = "$BC: %d \\cdot %s$"%(value, str(clause)))
        qc.append(clause_gate, qr_ctrl[0:n] + qr_trgt[0:m])
        
    return qc


#Inverse of bcf_circuit
def bcf_inv_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits

    qc = QuantumCircuit()
    
    qr_ctrl = QuantumRegister(n, "ctrl")
    qr_trgt = QuantumRegister(m, "trgt")
    qc.add_register(qr_ctrl)
    qc.add_register(qr_trgt)
    
    for clause, value in binary_cost_function.clauses.items():
        clause_gate = bc_circuit(m, clause, -value).to_gate(label = "$BC: %d \\cdot %s$"%(-value, str(clause)))
        qc.append(clause_gate, qr_ctrl[0:n] + qr_trgt[0:m])
        
    return qc


#Preparation operator A, which uses the custom implementation of the inverse QFT
def A_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
    
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)

    qc.h(qr_strs)
    qc.h(qr_vals)

    bcf_gate = bcf_circuit(m, binary_cost_function).to_gate(label = "$BCF$")
    qc.append(bcf_gate, qr_strs[0:n] + qr_vals[0:m])

    inv_qft_gate = QFT_inv_circuit(m).to_gate(label = "$\\mathrm{QFT}_{%d}^{-1}$"%(m))
    qc.append(inv_qft_gate, qr_vals)
        
    return qc


#Inverse of A_circuit, which uses the custom implementation of the QFT
def A_inv_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
        
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    
    qft_gate = QFT_circuit(m).to_gate(label = "$\\mathrm{QFT}_{%d}$"%(m))
    qc.append(qft_gate, qr_vals)
    
    inverse_bcf_gate = bcf_inv_circuit(m, binary_cost_function).to_gate(label = "$BCF^{-1}$")
    qc.append(inverse_bcf_gate, qr_strs[0:n] + qr_vals[0:m])
    
    qc.h(qr_strs)
    qc.h(qr_vals)
    
    return qc
        

#The oracle O
def O_circuit(m):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(m)
    qc.add_register(qr)
    
    qc.z(qr[m-1])
    
    return qc


# The diffusor D
def D_circuit(n):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n)
    qc.add_register(qr)
    
    diag_vals = [1] * (2**n)
    diag_vals[0] = -1
    qc.diagonal(diag_vals, qr)
    
    return qc


#The Grover iterator G
def G_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
        
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    
    O_gate = O_circuit(m).to_gate(label = "$O$")
    qc.append(O_gate, qr_vals)
    
    inverse_A_gate = A_inv_circuit(m, binary_cost_function).to_gate(label = "$A^{-1}$")
    qc.append(inverse_A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    D_gate = D_circuit(n).to_gate(label = "$D$")
    qc.append(D_gate, qr_strs)
    
    A_gate = A_circuit(m, binary_cost_function).to_gate(label = "$A$")
    qc.append(A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    return qc


#The complete Grover Adaptive Search circuit
#Can input threshold and number of iterations r
def GAS_circuit(m, binary_cost_function, threshold, r):
    bcf_copy = binary_cost_function.copy()
    
    n = bcf_copy.num_bits
    bcf_copy.add_clause(BinaryClause("X" * n), -threshold)
    
    qc = QuantumCircuit()
    
    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    
    A_gate = A_circuit(m, bcf_copy).to_gate(label = "$A$")
    qc.append(A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    G_gate = G_circuit(m, bcf_copy).to_gate(label = "$G$")
    for i in range(r):
        qc.append(G_gate, qr_strs[0:n] + qr_vals[0:m])
    
    return qc