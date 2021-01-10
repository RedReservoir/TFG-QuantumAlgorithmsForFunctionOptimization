from qiskit import *

import math


#Inverse QFT circuit with digits xn,...,x1
def QFT_inv_circuit(n):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n, "q")
    qc.add_register(qr)
    
    for i in range(n):
    	qc.h(qr[i])
    	for j in range(i+1, n):
        	qc.crz(-math.pi * 2**(i-j), qr[i], qr[j])
    
    return qc

#QFT circuit with digits xn,...,x1
def QFT_circuit(n):
    qc = QuantumCircuit()
    
    qr = QuantumRegister(n, "q")
    qc.add_register(qr)
    
    for i in range(n-1, -1, -1):
        for j in range(n-1, i, -1):
            qc.crz(math.pi * 2**(i-j), qr[i], qr[j])
        qc.h(qr[i])
    
    return qc