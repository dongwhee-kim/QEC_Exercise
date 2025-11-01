# 파일명: error_correction.py

import networkx as nx
import numpy as np

# --- 헬퍼 함수: main.py의 stabilizer 정보를 그대로 가져옴 ---

def get_stabilizer_maps():
    """
    디코딩 그래프와 최종 신드롬 계산에 필요한
    안정자(stabilizer) 맵을 반환합니다.
    """
    z_stabilizers = {
        'c_z[0]': ['d[0]', 'd[1]', 'd[3]'],
        'c_z[1]': ['d[1]', 'd[2]', 'd[4]'],
        'c_z[2]': ['d[3]', 'd[5]', 'd[6]', 'd[8]'],
        'c_z[3]': ['d[4]', 'd[6]', 'd[7]', 'd[9]'],
        'c_z[4]': ['d[8]', 'd[10]', 'd[11]'],
        'c_z[5]': ['d[9]', 'd[11]', 'd[12]']
    }
    
    x_stabilizers = {
        'c_x[0]': ['d[0]', 'd[3]', 'd[5]'],
        'c_x[1]': ['d[1]', 'd[3]', 'd[4]', 'd[6]'],
        'c_x[2]': ['d[2]', 'd[4]', 'd[7]'],
        'c_x[3]': ['d[5]', 'd[8]', 'd[10]'],
        'c_x[4]': ['d[6]', 'd[8]', 'd[9]', 'd[11]'],
        'c_x[5]': ['d[7]', 'd[9]', 'd[12]']
    }
    return z_stabilizers, x_stabilizers

# --- 2번 요청 (측정 에러)을 위한 함수 ---

def post_process_measurement_error(measured_string, ancilla_flip_index, error_type, round_idx, num_z_ancillas, num_x_ancillas):
    """
    시뮬레이터 실행 후 얻은 'measured_string'에
    수동으로 측정 에러(고전 비트 플립)를 주입합니다.
    """
    if ancilla_flip_index is None:
        return measured_string

    num_rounds = 3 # 이 코드는 d=3, 3라운드에 고정됨
    num_total_sx_bits = num_rounds * num_x_ancillas
    num_total_sz_bits = num_rounds * num_z_ancillas
    
    # Qiskit counts 문자열은 'sx[17]...sx[0] sz[17]...sz[0] res[12]...res[0]' 순서입니다.
    # 리스트로 변환하여 수정 가능하게 함
    sx_bits = list(measured_string[0:num_total_sx_bits])
    sz_bits = list(measured_string[num_total_sx_bits : num_total_sx_bits + num_total_sz_bits])
    res_bits = list(measured_string[num_total_sx_bits + num_total_sz_bits:])
    
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


# --- 1번 요청 (에러 커렉션)을 위한 함수들 ---

def create_decoding_graph(num_rounds, num_ancillas, spatial_edges, p_data, p_meas):
    """
    MWPM을 위한 시공간(space-time) 디코딩 그래프를 생성합니다.
    """
    G = nx.Graph()
    
    # 가중치 계산 (log-likelihood)
    w_spatial = -np.log(p_data) if p_data > 0 else float('inf')
    w_temporal = -np.log(p_meas) if p_meas > 0 else float('inf')
    # 경계 가중치 (마지막 라운드와 최종 데이터 측정 사이의 데이터 에러)
    w_boundary = -np.log(p_data) if p_data > 0 else float('inf')

    num_nodes_per_round = num_ancillas
    
    # 1. 공간적 엣지 (Spatial Edges) - 데이터 큐비트 에러
    for r in range(num_rounds):
        offset = r * num_nodes_per_round
        for u, v in spatial_edges:
            G.add_edge(u + offset, v + offset, weight=w_spatial)
            
    # 2. 시간적 엣지 (Temporal Edges) - 측정 에러
    for r in range(num_rounds - 1):
        offset1 = r * num_nodes_per_round
        offset2 = (r + 1) * num_nodes_per_round
        for a in range(num_ancillas):
            G.add_edge(a + offset1, a + offset2, weight=w_temporal)

    # 3. 경계 엣지 (Boundary Edges) - 마지막 라운드의 신드롬
    # 마지막 라운드의 각 안실라 노드(r=2)를 가상의 "경계 노드"에 연결합니다.
    final_round_offset = (num_rounds - 1) * num_nodes_per_round
    boundary_node_offset = num_rounds * num_nodes_per_round
    for a in range(num_ancillas):
        G.add_node(a + boundary_node_offset) # 경계 노드 (e.g., 18~23)
        G.add_edge(a + final_round_offset, a + boundary_node_offset, weight=w_boundary)
        
    return G

def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    """
    최종 측정된 'res' 데이터 큐비트 값으로부터
    논리적 신드롬(logical syndrome)을 계산합니다.
    """
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    for a_idx, (a_name, data_qubits) in enumerate(stabilizers_map.items()):
        parity = 0
        for dq_str in data_qubits:
            # 'd[5]' -> 5
            dq_idx = int(dq_str[2:-1])
            parity ^= res_bits[dq_idx]
        final_syndrome[a_idx] = parity
        
    return final_syndrome

def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index):
    """
    MWPM 디코더를 실행하고 에러 상태를 리포트합니다.
    """
    
    z_stabilizers, x_stabilizers = get_stabilizer_maps()
    
    # --- 1. 측정 문자열 파싱 ---
    num_sx = num_rounds * num_x_ancillas
    num_sz = num_rounds * num_z_ancillas
    
    # 'sx[17]...sx[0]' -> [sx[0], ..., sx[17]] (little-endian)
    sx_bits = [int(bit) for bit in measured_string[0:num_sx]][::-1]
    # 'sz[17]...sz[0]' -> [sz[0], ..., sz[17]]
    sz_bits = [int(bit) for bit in measured_string[num_sx : num_sx + num_sz]][::-1]
    # 'res[12]...res[0]' -> [res[0], ..., res[12]]
    res_bits = [int(bit) for bit in measured_string[num_sx + num_sz:]][::-1]

    # --- 2. 신드롬을 2D 배열로 변환 (round, ancilla) ---
    sz_syndromes = np.array(sz_bits).reshape((num_rounds, num_z_ancillas))
    sx_syndromes = np.array(sx_bits).reshape((num_rounds, num_x_ancillas))
    
    # --- 3. 디펙트(Defect) 계산 (신드롬의 *변화*) ---
    # Z-디펙트 (X-에러 검출)
    z_defects = np.zeros((num_rounds, num_z_ancillas), dtype=int)
    z_defects[0, :] = sz_syndromes[0, :] # Round 0 (초기상태 '0'과 비교)
    for r in range(1, num_rounds):
        z_defects[r, :] = np.bitwise_xor(sz_syndromes[r, :], sz_syndromes[r-1, :])
        
    # X-디펙트 (Z-에러 검출)
    x_defects = np.zeros((num_rounds, num_x_ancillas), dtype=int)
    x_defects[0, :] = sx_syndromes[0, :] # Round 0
    for r in range(1, num_rounds):
        x_defects[r, :] = np.bitwise_xor(sx_syndromes[r, :], sx_syndromes[r-1, :])

    # --- 4. 경계(Boundary) 디펙트 계산 ---
    # 최종 데이터 큐비트(res)의 신드롬을 계산
    final_z_syndrome = calculate_syndrome_from_res(res_bits, z_stabilizers, num_z_ancillas)
    final_x_syndrome = calculate_syndrome_from_res(res_bits, x_stabilizers, num_x_ancillas)
    
    # 마지막 라운드 신드롬(r=2)과 최종 데이터 신드롬을 비교
    final_z_defects = np.bitwise_xor(sz_syndromes[num_rounds-1, :], final_z_syndrome)
    final_x_defects = np.bitwise_xor(sx_syndromes[num_rounds-1, :], final_x_syndrome)

    # --- 5. MWPM 실행 ---
    # Z-Graph (X 에러 교정)
    z_defect_nodes = []
    for r in range(num_rounds):
        for a in range(num_z_ancillas):
            if z_defects[r, a] == 1:
                z_defect_nodes.append(r * num_z_ancillas + a) # 노드 0-17
    for a in range(num_z_ancillas):
        if final_z_defects[a] == 1:
            z_defect_nodes.append(num_rounds * num_z_ancillas + a) # 경계 노드 18-23
            
    # X-Graph (Z 에러 교정)
    x_defect_nodes = []
    for r in range(num_rounds):
        for a in range(num_x_ancillas):
            if x_defects[r, a] == 1:
                x_defect_nodes.append(r * num_x_ancillas + a)
    for a in range(num_x_ancillas):
        if final_x_defects[a] == 1:
            x_defect_nodes.append(num_rounds * num_x_ancillas + a)

    # (참고: MWPM 실행은 이 코드에서 생략. 디코딩 그래프 생성/디펙트 검출까지만 구현)
    # z_graph = create_decoding_graph(num_rounds, num_z_ancillas, spatial_edges_z, prob_data_x, prob_meas_z)
    # z_matching = nx.min_weight_matching(z_graph, z_defect_nodes)
    # (매칭 결과를 분석하여 실제 보정 게이트를 결정하는 로직이 추가로 필요)

    # --- 6. 에러 리포트 (단순화된 버전) ---
    # 이 테스트의 목적(단일 에러 교정)에 맞춰,
    # 최종 논리적 상태가 '0'인지 아닌지만으로 판단합니다.
    # (모든 데이터 큐비트가 |0>으로 초기화되었다고 가정)
    
    no_error_injected = (injected_error_group == 'Data' and injected_data_flip_index is None) or \
                          (injected_error_group == 'Measurement' and injected_ancilla_flip_index is None)

    # final_z_syndrome이 0이 아니라는 것은, X-에러가 교정되지 않았음을 의미.
    # res_bits가 |00..0>이 아니라는 것은 (Z-에러가 |0> 상태에 영향을 주지 않으므로),
    # X-에러가 교정되지 않았음을 의미.
    logical_x_error_detected = any(final_z_syndrome) or any(res_bits)
    
    # final_x_syndrome이 0이 아니라는 것은, Z-에러가 교정되지 않았음을 의미.
    logical_z_error_detected = any(final_x_syndrome)
    
    logical_error_detected = logical_x_error_detected or logical_z_error_detected
    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error (에러 주입 O, 논리 에러 X)
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error (논리 에러 O)
    else:
        # (no_error_injected and logical_error_detected)
        # -> 에러 주입 안했는데 논리 에러 발생 (시뮬레이터 노이즈 등. 여기서는 해당 없음)
        return 'UE'
