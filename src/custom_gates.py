from qiskit import *

import math


#Generates rotation of theta radians on hadamard state
def UG_circuit(n, theta):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n, "q")
    qc.add_register(qr)
    
    for i in range(n):
    	qc.rz(2**(n-i-1) * theta, qr[i])
    
    return qc