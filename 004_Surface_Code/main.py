from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit

"""
Error Model (Weight)
1. 각 data qubit마다 X/Z/Y error 발생할 확률 다르다. (이 문제에서는 똑같이 X, Z 각각 50%로)
 - Y error는 X, Z 2개의 곱으로 생각하자.

2. Measurement error 발생확률 각 X/Z ancillary qubit마다 다르다. (이 문제에서는 똑같이 X,Z 각각 10%로)
 -> (d round 반복)

Error injection 순서
 1. 발생시킬 error 결정 (data qubit error 또는 measurement error)
 -> d=3이니 1개만 정함.

2. 해당 위치에서 X/Z/Y 중 어떤 error 발생시킬지 정함. 독립으로 곱해서 Y도 발생시킬 수 있도록함.

3. 값이 1인 ancillary qubit으로 graph생성

4. graph로 MWPM 실행.

"""