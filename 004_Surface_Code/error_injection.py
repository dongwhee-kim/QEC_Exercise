from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# single data qubit error 'or' single measurement error
# error injection only round_idx=0

# e.g., d[5] bit flip at round=0
# round0: c_z[2] = 0 -> 1 (change!)
# round1: c_z[8] = 1 -> 1 (non-change!) [error_remain]
# round2: c_z[14] = 1 -> 1 (non-change!) [error_remain]
# result: c_z[2] single event -> correct only d[5] (apply bit-flip gate)

# e.g., sz[8] measurement error at round=0
# -> After AerSimulator!!!
# round0: sz[2] = 0 -> 1 (change!)
# round1: sz[8] = 1 -> 0 (change!)
# round2: sz[14] = 0 -> 0 (non-change!)
# result: sz[2], sz[8] double event -> no correction. shortest path is time-like measurement error

def error_injection_single_qubit_error_func(qc, flip_index, error_type='X'):
    if flip_index is None:
        return
    
    if error_type == 'X':
        qc.x(flip_index)
    elif error_type == 'Z':
        qc.z(flip_index)
    elif error_type == 'Y':
        qc.x(flip_index)
        qc.z(flip_index)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return

def post_process_measurement_error_func(measured_string, ancilla_flip_index, error_type, round_idx, num_z_ancillas, num_x_ancillas):
    """
    시뮬레이터 실행 후 얻은 'measured_string'에
    수동으로 측정 에러(고전 비트 플립)를 주입합니다.
    """
    if ancilla_flip_index is None:
        return measured_string

    num_rounds = 3 # 이 코드는 d=3, 3라운드에 고정됨
    num_total_sx_bits = num_rounds * num_x_ancillas
    num_total_sz_bits = num_rounds * num_z_ancillas

    # 레지스터 사이의 공백 제거
    cleaned_string = measured_string.replace(" ", "")
    
    # Qiskit counts 문자열은 'sx[17]...sx[0] sz[17]...sz[0] res[12]...res[0]' 순서입니다.
    # 리스트로 변환하여 수정 가능하게 함
    sx_bits = list(cleaned_string[0:num_total_sx_bits])
    sz_bits = list(cleaned_string[num_total_sx_bits : num_total_sx_bits + num_total_sz_bits])
    res_bits = list(cleaned_string[num_total_sx_bits + num_total_sz_bits:])
    
    # 'sz[5]...sz[0]' (round 0), 'sz[11]...sz[6]' (round 1) ...
    # Qiskit 문자열은 little-endian 인덱싱과 반대입니다.
    # sx[0] 비트는 sx_bits 문자열의 *오른쪽 끝*에서 1번째입니다 (인덱스 17).
    # sx[5] 비트는 sx_bits 문자열의 *오른쪽 끝*에서 6번째입니다 (인덱스 12).
    
    if error_type == 'Z' or error_type == 'Y': # Z-안정자 (sz) 측정 에러
        # 라운드와 인덱스를 기반으로 전체 18비트 'sz' 문자열 내의 인덱스를 계산
        # (num_total_sz_bits - 1) - (round_idx * num_z_ancillas + ancilla_flip_index)
        bit_pos_in_str = (num_total_sz_bits - 1) - (round_idx * num_z_ancillas + ancilla_flip_index)
        
        # 비트 플립
        current_bit = sz_bits[bit_pos_in_str]
        sz_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'
        
    elif error_type == 'X': # X-안정자 (sx) 측정 에러
        # 라운드와 인덱스를 기반으로 전체 18비트 'sx' 문자열 내의 인덱스를 계산
        bit_pos_in_str = (num_total_sx_bits - 1) - (round_idx * num_x_ancillas + ancilla_flip_index)
        
        # 비트 플립
        current_bit = sx_bits[bit_pos_in_str]
        sx_bits[bit_pos_in_str] = '1' if current_bit == '0' else '0'

    # 수정된 비트 문자열들을 다시 합쳐서 반환
    return "".join(sx_bits) + "".join(sz_bits) + "".join(res_bits)

def error_injection_logical_error_rate_func(qc, flip_index, error_type='X'):
    if flip_index is None:
        return
    
    if error_type == 'X':
        qc.x(flip_index)
    elif error_type == 'Z':
        qc.z(flip_index)
    elif error_type == 'Y':
        qc.x(flip_index)
        qc.z(flip_index)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return
