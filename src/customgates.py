from qiskit import *
from binarycostfunction import *
import math

def create_ug_circuit(m, theta):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(m, "q")
    qc.add_register(qr)
    
    for i in range(m):
        qc.rz(2**(m-i-1) * theta, qr[i])
    
    return qc

def create_binary_clause_circuit(m, binary_clause, value):
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
    
    ctrl_ug_gate = create_ug_circuit(m, 2**(1-m)*math.pi*value).to_gate(label = "UG {0:f}".format(2**(1-m)*math.pi*value))
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

def create_binary_cost_function_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits

    qc = QuantumCircuit()
    
    qr_ctrl = QuantumRegister(n, "ctrl")
    qr_trgt = QuantumRegister(m, "trgt")
    qc.add_register(qr_ctrl)
    qc.add_register(qr_trgt)
    
    for clause, value in binary_cost_function.clauses.items():
        clause_gate = create_binary_clause_circuit(m, clause, value).to_gate(label = "BC {0:d} * {1:s}".format(value, str(clause)))
        qc.append(clause_gate, qr_ctrl[0:n] + qr_trgt[0:m])
        
    return qc

def create_inverse_binary_cost_function_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits

    qc = QuantumCircuit()
    
    qr_ctrl = QuantumRegister(n, "ctrl")
    qr_trgt = QuantumRegister(m, "trgt")
    qc.add_register(qr_ctrl)
    qc.add_register(qr_trgt)
    
    for clause, value in binary_cost_function.clauses.items():
        clause_gate = create_binary_clause_circuit(m, clause, -value).to_gate(label = "BC {0:d} * {1:s}".format(-value, str(clause)))
        qc.append(clause_gate, qr_ctrl[0:n] + qr_trgt[0:m])
        
    return qc

def create_A_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
    
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)

    qc.h(qr_strs)
    qc.h(qr_vals)

    bcf_gate = create_binary_cost_function_circuit(m, binary_cost_function).to_gate(label = "BCF")
    qc.append(bcf_gate, qr_strs[0:n] + qr_vals[0:m])

    inv_qft_gate = qiskit.circuit.library.QFT(num_qubits = m, inverse = True, do_swaps = True).to_gate(label = "QFT^-1")
    qc.append(inv_qft_gate, qr_vals)

    for i in range(m//2):
        qc.swap(qr_vals[i], qr_vals[m-1 - i])
        
    return qc

def create_inverse_A_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
        
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    
    for i in range(m//2):
        qc.swap(qr_vals[i], qr_vals[m-1 - i])

    qft_gate = qiskit.circuit.library.QFT(num_qubits = m, inverse = False, do_swaps = True).to_gate(label = "QFT")
    qc.append(qft_gate, qr_vals)
    
    inverse_bcf_gate = create_inverse_binary_cost_function_circuit(m, binary_cost_function).to_gate(label = "BCF^-1")
    qc.append(inverse_bcf_gate, qr_strs[0:n] + qr_vals[0:m])
    
    qc.h(qr_strs)
    qc.h(qr_vals)
    
    return qc
        
def create_O_circuit(m):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(m)
    qc.add_register(qr)
    
    qc.z(qr[m-1])
    
    return qc

def create_D_circuit(n):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n)
    qc.add_register(qr)
    
    diag_vals = [1] * (2**n)
    diag_vals[0] = -1
    qc.diagonal(diag_vals, qr)
    
    return qc

def create_G_circuit(m, binary_cost_function):
    n = binary_cost_function.num_bits
        
    qc = QuantumCircuit()

    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    
    O_gate = create_O_circuit(m).to_gate(label = "O")
    qc.append(O_gate, qr_vals)
    
    inv_A_gate = create_inverse_A_circuit(m, binary_cost_function).to_gate(label = "A^-1")
    qc.append(inv_A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    D_gate = create_D_circuit(n).to_gate(label = "D")
    qc.append(D_gate, qr_strs)
    
    A_gate = create_A_circuit(m, binary_cost_function).to_gate(label = "A")
    qc.append(A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    return qc

def create_GAS_circuit(m, binary_cost_function, threshold, r):
    bcf_copy = binary_cost_function.copy()
    
    n = bcf_copy.num_bits
    bcf_copy.add_clause(BinaryClause("X" * n), threshold)
    
    qc = QuantumCircuit()
    
    qr_strs = QuantumRegister(n, "strs")
    qr_vals = QuantumRegister(m, "vals")
    cr_strs = ClassicalRegister(n, "cl_strs")
    cr_vals = ClassicalRegister(m, "cl_vals")
    qc.add_register(qr_strs)
    qc.add_register(qr_vals)
    qc.add_register(cr_strs)
    qc.add_register(cr_vals)
    
    A_gate = create_A_circuit(m, bcf_copy).to_gate(label = "A")
    qc.append(A_gate, qr_strs[0:n] + qr_vals[0:m])
    
    G_gate = create_G_circuit(m, bcf_copy).to_gate(label = "G")
    for i in range(r):
        qc.append(G_gate, qr_strs[0:n] + qr_vals[0:m])
    
    qc.measure(qr_strs, cr_strs)
    qc.measure(qr_vals, cr_vals)
    
    return qc