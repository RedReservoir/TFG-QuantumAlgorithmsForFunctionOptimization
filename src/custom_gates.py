from qiskit import *
from qiskit.quantum_info import Operator

import math


#Generates rotation of theta radians on hadamard state
def UG_circuit(n, theta):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n, "q")
    qc.add_register(qr)
    
    for i in range(n):
    	qc.rz(2**(n-i-1) * theta, qr[i])
    
    return qc


#Generates gate U^x of unitary U
def Ux_circuit(n, U, x):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n, "q")
    qc.add_register(qr)
    
    U_op = Operator(U)

    for _ in range(x):
    	qc.unitary(U_op, qr[:])
    
    return qc