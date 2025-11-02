# 파일명: error_correction.py
# (이 내용으로 파일 전체를 덮어쓰세요)

import networkx as nx
import numpy as np
import itertools # <--- ⭐️ [추가됨]

# --- 헬퍼 함수: 안정자 맵 + 디코딩 맵 추가 ---

def get_stabilizer_and_decoding_maps():
    """
    디코딩 그래프와 최종 신드롬 계산에 필요한
    안정자(stabilizer) 맵 및 디코딩 맵을 반환합니다.
    """
    
    # --- <수정됨> ---
    # 딕셔너리의 값(value)을 리스트(list)가 아닌 튜플(tuple)로 변경
    z_stabilizers = {
        'c_z[0]': ('d[0]', 'd[1]', 'd[3]'),
        'c_z[1]': ('d[1]', 'd[2]', 'd[4]'),
        'c_z[2]': ('d[3]', 'd[5]', 'd[6]', 'd[8]'),
        'c_z[3]': ('d[4]', 'd[6]', 'd[7]', 'd[9]'),
        'c_z[4]': ('d[8]', 'd[10]', 'd[11]'),
        'c_z[5]': ('d[9]', 'd[11]', 'd[12]')
    }
    
    # --- <수정됨> ---
    # 딕셔너리의 값(value)을 리스트(list)가 아닌 튜플(tuple)로 변경
    x_stabilizers = {
        'c_x[0]': ('d[0]', 'd[3]', 'd[5]'),
        'c_x[1]': ('d[1]', 'd[3]', 'd[4]', 'd[6]'),
        'c_x[2]': ('d[2]', 'd[4]', 'd[7]'),
        'c_x[3]': ('d[5]', 'd[8]', 'd[10]'),
        'c_x[4]': ('d[6]', 'd[8]', 'd[9]', 'd[11]'),
        'c_x[5]': ('d[7]', 'd[9]', 'd[12]')
    }
    
    # --- MWPM 엣지를 데이터 큐비트 인덱스로 매핑 ---
    
    # Z-Graph (X-error)의 Spatial 엣지 -> X-Correction 맵
    # (ancilla_u, ancilla_v): data_qubit_index
    z_spatial_map = {
        (0, 1): 1, (0, 2): 3, (1, 3): 4, (2, 3): 6, 
        (2, 4): 8, (3, 5): 9, (4, 5): 11
    }
    
    # Z-Graph (X-error)의 Boundary 엣지 -> X-Correction 맵
    # (ancilla_u): data_qubit_index
    z_boundary_map = {0: 0, 1: 2, 4: 10, 5: 12}
    
    # X-Graph (Z-error)의 Spatial 엣지 -> Z-Correction 맵
    x_spatial_map = {
        (0, 1): 3, (0, 3): 5, (1, 2): 4, (1, 4): 6, 
        (2, 5): 7, (3, 4): 8, (4, 5): 9
    }

    # X-Graph (Z-error)의 Boundary 엣지 -> Z-Correction 맵
    x_boundary_map = {0: 0, 1: 1, 2: 2, 3: 10, 4: 11, 5: 12}

    return (
        z_stabilizers, x_stabilizers, 
        z_spatial_map, z_boundary_map, 
        x_spatial_map, x_boundary_map
    )

# --- 디코딩 그래프 생성 (기존과 동일) ---
def create_decoding_graph(num_rounds, num_ancillas, spatial_edges, p_data, p_meas):
    """
    MWPM을 위한 시공간(space-time) 디코딩 그래프를 생성합니다.
    (V2: 모든 'qubits' 속성을 튜플로 강제)
    """
    
    G = nx.Graph()
    
    w_spatial = -np.log(p_data) if p_data > 0 else float('inf')
    w_temporal = -np.log(p_meas) if p_meas > 0 else float('inf')
    w_boundary = -np.log(p_data) if p_data > 0 else float('inf')

    num_nodes_per_round = num_ancillas
    
    # 1. 공간적 엣지 (Spatial Edges)
    for r in range(num_rounds):
        offset = r * num_nodes_per_round
        for u_raw, v_raw in spatial_edges:
            # 맵의 키와 순서를 맞추기 위해 정렬
            u, v = min(u_raw, v_raw), max(u_raw, v_raw)
            # <--- 'type'과 'qubits' 튜플 속성이 있는 V2 원본
            G.add_edge(u + offset, v + offset, weight=w_spatial, type='spatial', qubits=((u_raw, v_raw),))
            
    # 2. 시간적 엣지 (Temporal Edges)
    for r in range(num_rounds - 1):
        offset1 = r * num_nodes_per_round
        offset2 = (r + 1) * num_nodes_per_round
        for a in range(num_ancillas):
            # <--- 'type'과 'qubits' 튜플 속성이 있는 V2 원본
            G.add_edge(a + offset1, a + offset2, weight=w_temporal, type='temporal', qubits=())

    # 3. 경계 엣지 (Boundary Edges)
    final_round_offset = (num_rounds - 1) * num_nodes_per_round
    boundary_node_offset = num_rounds * num_nodes_per_round # 가상 경계 노드 시작 인덱스
    for a in range(num_ancillas):
        G.add_node(a + boundary_node_offset) 
        # <--- 'type'과 'qubits' 튜플 속성이 있는 V2 원본
        G.add_edge(a + final_round_offset, a + boundary_node_offset, weight=w_boundary, type='boundary', qubits=((a,),))
        
    return G

# --- 신드롬 계산 (기존과 동일) ---

def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    """
    최종 측정된 'res' 데이터 큐비트 값으로부터
    논리적 신드롬(logical syndrome)을 계산합니다.
    """
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    for a_idx, (a_name, data_qubits) in enumerate(stabilizers_map.items()):
        parity = 0
        for dq_str in data_qubits: # 튜플을 순회하는 것은 리스트와 동일하게 동작합니다.
            dq_idx = int(dq_str[2:-1])
            parity ^= res_bits[dq_idx]
        final_syndrome[a_idx] = parity
        
    return final_syndrome

# --- <수정됨> 메인 리포팅 함수 ---

def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index):
    """
    MWPM 디코더를 실행하고 에러 상태를 리포트합니다.
    """
    
    (z_stabilizers, x_stabilizers, 
     z_spatial_map, z_boundary_map, 
     x_spatial_map, x_boundary_map) = get_stabilizer_and_decoding_maps()
    
    # --- 1. 측정 문자열 파싱 ---
    num_sx = num_rounds * num_x_ancillas
    num_sz = num_rounds * num_z_ancillas
    
    # 공백 제거 (중요)
    cleaned_string = measured_string.replace(" ", "")

    sx_bits = [int(bit) for bit in cleaned_string[0:num_sx]][::-1]
    sz_bits = [int(bit) for bit in cleaned_string[num_sx : num_sx + num_sz]][::-1]
    res_bits = [int(bit) for bit in cleaned_string[num_sx + num_sz:]][::-1]

    # --- 2. 신드롬을 2D 배열로 변환 ---
    sz_syndromes = np.array(sz_bits).reshape((num_rounds, num_z_ancillas))
    sx_syndromes = np.array(sx_bits).reshape((num_rounds, num_x_ancillas))
    
    # --- 3. 디펙트(Defect) 계산 ---
    z_defects = np.zeros((num_rounds, num_z_ancillas), dtype=int)
    z_defects[0, :] = sz_syndromes[0, :]
    for r in range(1, num_rounds):
        z_defects[r, :] = np.bitwise_xor(sz_syndromes[r, :], sz_syndromes[r-1, :])
        
    x_defects = np.zeros((num_rounds, num_x_ancillas), dtype=int)
    x_defects[0, :] = sx_syndromes[0, :]
    for r in range(1, num_rounds):
        x_defects[r, :] = np.bitwise_xor(sx_syndromes[r, :], sx_syndromes[r-1, :])

    # --- 4. 경계(Boundary) 디펙트 계산 ---
    final_z_syndrome = calculate_syndrome_from_res(res_bits, z_stabilizers, num_z_ancillas)
    final_x_syndrome = calculate_syndrome_from_res(res_bits, x_stabilizers, num_x_ancillas)
    
    final_z_defects = np.bitwise_xor(sz_syndromes[num_rounds-1, :], final_z_syndrome)
    final_x_defects = np.bitwise_xor(sx_syndromes[num_rounds-1, :], final_x_syndrome)

    # --- 5. <⭐️ [수정됨]> MWPM 그래프 생성 및 실행 ---
    
    # Z-Graph (X 에러 교정)
    z_graph = create_decoding_graph(num_rounds, num_z_ancillas, spatial_edges_z, prob_data_x, prob_meas_z)
    z_defect_nodes = []
    for r in range(num_rounds):
        for a in range(num_z_ancillas):
            if z_defects[r, a] == 1:
                z_defect_nodes.append(r * num_z_ancillas + a) # 노드 0-17
    for a in range(num_z_ancillas):
        if final_z_defects[a] == 1:
            z_defect_nodes.append(num_rounds * num_z_ancillas + a) # 경계 노드 18-23
    
    # --- [⭐️ 수정된 MWPM 로직 시작] ---
    # 1. 디펙트 노드들로만 구성된 완전 그래프(K_z) 생성
    K_z = nx.Graph()
    for u, v in itertools.combinations(z_defect_nodes, 2):
        # 2. 원본 z_graph에서 (u, v) 간의 최단 경로 가중치를 계산
        path_weight = nx.shortest_path_length(z_graph, source=u, target=v, weight='weight')
        # 3. K_z에 해당 가중치로 엣지 추가
        K_z.add_edge(u, v, weight=path_weight)

    # 4. 이 'K_z' 그래프에 대해 MWPM 실행
    z_matching_edges = nx.min_weight_matching(K_z)
    
    # z_matching_edges는 (u, v) 쌍의 set입니다.
    # 이를 원본 z_graph의 경로로 변환해야 합니다. (교정을 위해)
    z_matching = set()
    for u, v in z_matching_edges:
        # z_matching은 (u, v) 쌍의 set이므로,
        # 나중에 교정 로직에서 z_graph.get_edge_data(u, v)를 사용하려면
        # (u, v)가 z_graph에 직접 연결된 엣지여야 합니다.
        # 따라서 최단 경로를 찾아 z_graph의 엣지들로 분해해야 합니다.
        path = nx.shortest_path(z_graph, source=u, target=v, weight='weight')
        for i in range(len(path) - 1):
            z_matching.add(tuple(sorted((path[i], path[i+1]))))
    # --- [⭐️ 수정된 MWPM 로직 끝] ---


    # X-Graph (Z 에러 교정)
    x_graph = create_decoding_graph(num_rounds, num_x_ancillas, spatial_edges_x, prob_data_z, prob_meas_x)
    x_defect_nodes = []
    for r in range(num_rounds):
        for a in range(num_x_ancillas):
            if x_defects[r, a] == 1:
                x_defect_nodes.append(r * num_x_ancillas + a)
    for a in range(num_x_ancillas):
        if final_x_defects[a] == 1:
            x_defect_nodes.append(num_rounds * num_x_ancillas + a)

    # --- [⭐️ 수정된 MWPM 로직 시작] ---
    K_x = nx.Graph()
    for u, v in itertools.combinations(x_defect_nodes, 2):
        path_weight = nx.shortest_path_length(x_graph, source=u, target=v, weight='weight')
        K_x.add_edge(u, v, weight=path_weight)

    x_matching_edges = nx.min_weight_matching(K_x)
    
    x_matching = set()
    for u, v in x_matching_edges:
        path = nx.shortest_path(x_graph, source=u, target=v, weight='weight')
        for i in range(len(path) - 1):
            x_matching.add(tuple(sorted((path[i], path[i+1]))))
    # --- [⭐️ 수정된 MWPM 로직 끝] ---

    # --- 5.5. <추가됨> 교정(Correction) 적용 ---
    # MWPM의 결과를 바탕으로 'res_bits'와 'final_x_syndrome'을 보정합니다.
    
    corrected_res_bits = np.array(res_bits)
    corrected_final_x_syndrome = np.array(final_x_syndrome)
    
    # Z-Graph (X-Error) 교정 -> res_bits를 플립 (X-gate)
    # [수정됨] z_matching은 이제 (u, v) 튜플의 set입니다.
    for u, v in z_matching:
        edge_data = z_graph.get_edge_data(u, v)
        # 엣지가 존재하지 않는 경우(드물지만) 방지
        if edge_data is None: 
            continue
            
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            # (u_raw, v_raw) 튜플
            ancilla_pair = edge_data['qubits'][0] 
            # 맵의 키와 순서를 맞추기 위해 정렬
            key = tuple(sorted(ancilla_pair)) 
            qubit_to_flip = z_spatial_map.get(key)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]
                
        elif edge_type == 'boundary':
            # (ancilla_u,) 튜플
            ancilla_idx = edge_data['qubits'][0][0] 
            qubit_to_flip = z_boundary_map.get(ancilla_idx)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]

    # X-Graph (Z-Error) 교정 -> final_x_syndrome을 플립 (Z-gate)
    # (res_bits는 Z-측정이므로 Z-에러에 영향받지 않음)
    # [수정됨] x_matching은 이제 (u, v) 튜플의 set입니다.
    for u, v in x_matching:
        edge_data = x_graph.get_edge_data(u, v)
        if edge_data is None:
            continue
            
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            ancilla_pair = edge_data['qubits'][0]
            key = tuple(sorted(ancilla_pair))
            qubit_to_flip = x_spatial_map.get(key)
            
            # 이 Z-에러가 어떤 X-안정자에 영향을 주는지 확인
            if qubit_to_flip is not None: # <--- [추가됨] 맵에 없는 엣지(시간적 엣지) 방지
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

        elif edge_type == 'boundary':
            ancilla_idx = edge_data['qubits'][0][0]
            qubit_to_flip = x_boundary_map.get(ancilla_idx)

            if qubit_to_flip is not None: # <--- [추가됨] 맵에 없는 엣지(시간적 엣지) 방지
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

    # --- 6. <수정됨> 에러 리포트 ---
    # 교정된(corrected) 비트와 신드롬을 기준으로 논리적 오류를 판단합니다.
    
    no_error_injected = (injected_error_group == 'Data' and injected_data_flip_index is None) or \
                          (injected_error_group == 'Measurement' and injected_ancilla_flip_index is None)

    # 교정된 res_bits로 Z-신드롬을 다시 계산
    corrected_final_z_syndrome = calculate_syndrome_from_res(corrected_res_bits, z_stabilizers, num_z_ancillas)
    
    # X-논리 오류: 교정된 Z-신드롬이 0이 아니거나, 교정된 res_bits가 0이 아닌 경우
    logical_x_error_detected = any(corrected_final_z_syndrome) or any(corrected_res_bits)
    
    # Z-논리 오류: 교정된 X-신드롬이 0이 아닌 경우
    logical_z_error_detected = any(corrected_final_x_syndrome)
    
    logical_error_detected = logical_x_error_detected or logical_z_error_detected
    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error (에러 주입 O, 논리 에러 X)
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error (논리 에러 O)
    else:
        # (no_error_injected and logical_error_detected)
        return 'UE'