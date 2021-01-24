# TFG-QuantumAlgorithmsForFunctionOptimization

This project contains implementations, interactive test runs and visualizations of the Phase Estimation, Grover Search and Grover Adaptive Search quantum algorithms. The implementations are written in Python3, and the quantum algorithms use the Qiskit (https://github.com/Qiskit) framework.

To install the necessary libraries, generate a conda environment using the `requirements.txt` file on the base directory of this repository.

All code and test run results are in the `src` directory. The files on the `src` directory contain:

 - `num_base_converter.py`: Helper binary-to-decimal and decimal-to-binary conversion functions.
 - `binary_cost_function.py`: Classes `BinaryClause` and `BinaryCostFunction`. Also, some extra methods for random generation of instances of the classes.
 - `custom_gates.py`: Implementation for gates ![equation](https://latex.codecogs.com/gif.latex?U_G) and 
![equation](https://latex.codecogs.com/gif.latex?c%5C%21-%5C%21U%5Ex)
 - `custom_qft.py`: Implementation for the ![equation](https://latex.codecogs.com/gif.latex?%5Ctext%7BQFT%7D) and the ![equation](https://latex.codecogs.com/gif.latex?%5Ctext%7BQFT%7D%5E%7B-1%7D)
 - `custom_gas.py`: Implementation for all circuit components of the Grover Adaptive Search algorithm.

---

 - `PE_Tester.ipynb`: Jupyter Notebook with interactive test runs and visualizations of Phase Estimation executions and circuit components.
 - `GS_Tester.ipynb`: Jupyter Notebook with interactive test runs and visualizations of Grover Search executions and circuit components.
 - `GAS_Tester_1.ipynb`: Jupyter Notebook with interactive test runs and visualizations of Grover Adaptive Search executions and circuit components. This notebook should be viewed before `GAS_Tester_2.ipynb`.
 - `GAS_Tester_2.ipynb`: Jupyter Notebook with heavy and extensive test runs of Grover Adaptive Search. The tests in this notebook start taking pretty long for `n = 8` qubits. At `n = 12` qubits the Python kernel shuts down.

---

 - `GAS_results`: Directory containing test run data for the Grover Search Algorithm. The data is encoded as a binary stream and is not intelligible. To view the data, open `GAS_Tester_2.ipynb` and go to the "Automatic tests" section of the notebook. The directory includes:
   - `results_41f3748b586b6e336e6f1dd5e2d621f3.txt`: 193 test runs of a binary cost function with `n, m = 8, 8`.
   - `results_f41e67fdf60afdb63f7713d8c8a8853d.txt`: 172 test runs of a binary cost function with `n, m = 10, 8`.
