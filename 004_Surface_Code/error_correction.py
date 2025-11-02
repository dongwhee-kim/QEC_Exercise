# 파일명: error_correction.py
# (이 내용으로 파일 전체를 덮어쓰세요)

import networkx as nx
import numpy as np
import itertools 

# --- 헬퍼 함수 (기존과 동일) ---
def get_stabilizer_and_decoding_maps():
    z_stabilizers = {
        'c_z[0]': ('d[0]', 'd[1]', 'd[3]'),
        'c_z[1]': ('d[1]', 'd[2]', 'd[4]'),
        'c_z[2]': ('d[3]', 'd[5]', 'd[6]', 'd[8]'),
        'c_z[3]': ('d[4]', 'd[6]', 'd[7]', 'd[9]'),
        'c_z[4]': ('d[8]', 'd[10]', 'd[11]'),
        'c_z[5]': ('d[9]', 'd[11]', 'd[12]')
    }
    x_stabilizers = {
        'c_x[0]': ('d[0]', 'd[3]', 'd[5]'),
        'c_x[1]': ('d[1]', 'd[3]', 'd[4]', 'd[6]'),
        'c_x[2]': ('d[2]', 'd[4]', 'd[7]'),
        'c_x[3]': ('d[5]', 'd[8]', 'd[10]'),
        'c_x[4]': ('d[6]', 'd[8]', 'd[9]', 'd[11]'),
        'c_x[5]': ('d[7]', 'd[9]', 'd[12]')
    }
    z_spatial_map = {
        (0, 1): 1, (0, 2): 3, (1, 3): 4, (2, 3): 6, 
        (2, 4): 8, (3, 5): 9, (4, 5): 11
    }
    # Z-Graph의 경계 안정자 인덱스 (c_z[2], c_z[3], c_z[4] 포함)
    z_boundary_map = {0: 0, 1: 2, 2: 5, 3: 7, 4: 10, 5: 12}
    x_spatial_map = {
        (0, 1): 3, (0, 3): 5, (1, 2): 4, (1, 4): 6, 
        (2, 5): 7, (3, 4): 8, (4, 5): 9
    }
    x_boundary_map = {0: 0, 1: 1, 2: 2, 3: 10, 4: 11, 5: 12}

    return (
        z_stabilizers, x_stabilizers, 
        z_spatial_map, z_boundary_map, 
        x_spatial_map, x_boundary_map
    )

# --- 디코딩 그래프 생성 (V3 단일 경계 노드 - 수정 없음) ---
def create_decoding_graph(num_rounds, num_ancillas, spatial_edges, boundary_map, p_data, p_meas):
    G = nx.Graph()
    w_spatial = -np.log(p_data) if p_data > 0 else float('inf')
    w_temporal = -np.log(p_meas) if p_meas > 0 else float('inf')
    w_boundary_edge = -np.log(p_data) if p_data > 0 else float('inf')
    num_nodes_per_round = num_ancillas
    
    # 1. 공간적 엣지
    for r in range(num_rounds):
        offset = r * num_nodes_per_round
        for u_raw, v_raw in spatial_edges:
            u, v = min(u_raw, v_raw), max(u_raw, v_raw)
            G.add_edge(u + offset, v + offset, weight=w_spatial, type='spatial', qubits=((u_raw, v_raw),))
            
    # 2. 시간적 엣지
    for r in range(num_rounds - 1):
        offset1 = r * num_nodes_per_round
        offset2 = (r + 1) * num_nodes_per_round
        for a in range(num_ancillas):
            G.add_edge(a + offset1, a + offset2, weight=w_temporal, type='temporal', qubits=())

    # 3. 경계 엣지
    final_round_offset = (num_rounds - 1) * num_nodes_per_round
    boundary_node = num_rounds * num_nodes_per_round 
    G.add_node(boundary_node) 
    
    for a_idx in range(num_ancillas):
        if a_idx in boundary_map: 
            node_in_final_round = a_idx + final_round_offset
            G.add_edge(
                node_in_final_round, 
                boundary_node, 
                weight=w_boundary_edge, 
                type='boundary', 
                qubits=((a_idx,),) 
            )
        
    return G

# --- 신드롬 계산 (기존과 동일) ---
def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    for a_idx, (a_name, data_qubits) in enumerate(stabilizers_map.items()):
        parity = 0
        for dq_str in data_qubits: 
            dq_idx = int(dq_str[2:-1])
            parity ^= res_bits[dq_idx]
        final_syndrome[a_idx] = parity
        
    return final_syndrome

# --- 메인 리포팅 함수 (디버그 플래그 유지) ---
def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index,
    enable_debug_printing=False): 
    
    (z_stabilizers, x_stabilizers, 
     z_spatial_map, z_boundary_map, 
     x_spatial_map, x_boundary_map) = get_stabilizer_and_decoding_maps()
    
    # --- 1. 파싱 ---
    num_sx = num_rounds * num_x_ancillas
    num_sz = num_rounds * num_z_ancillas
    cleaned_string = measured_string.replace(" ", "")
    sx_bits = [int(bit) for bit in cleaned_string[0:num_sx]][::-1]
    sz_bits = [int(bit) for bit in cleaned_string[num_sx : num_sx + num_sz]][::-1]
    res_bits = [int(bit) for bit in cleaned_string[num_sx + num_sz:]][::-1]

    # --- 2. 2D 변환 ---
    sz_syndromes = np.array(sz_bits).reshape((num_rounds, num_z_ancillas))
    sx_syndromes = np.array(sx_bits).reshape((num_rounds, num_x_ancillas))
    
    # --- 3. 디펙트 계산 ---
    z_defects = np.zeros((num_rounds, num_z_ancillas), dtype=int)
    z_defects[0, :] = sz_syndromes[0, :]
    for r in range(1, num_rounds):
        z_defects[r, :] = np.bitwise_xor(sz_syndromes[r, :], sz_syndromes[r-1, :])
    x_defects = np.zeros((num_rounds, num_x_ancillas), dtype=int)
    x_defects[0, :] = sx_syndromes[0, :]
    for r in range(1, num_rounds):
        x_defects[r, :] = np.bitwise_xor(sx_syndromes[r, :], sx_syndromes[r-1, :])

    # --- 4. 경계 디펙트 계산 ---
    final_z_syndrome = calculate_syndrome_from_res(res_bits, z_stabilizers, num_z_ancillas)
    final_x_syndrome = np.zeros(num_x_ancillas, dtype=int) 
    
    final_z_defects = np.bitwise_xor(sz_syndromes[num_rounds-1, :], final_z_syndrome)
    final_x_defects = np.bitwise_xor(sx_syndromes[num_rounds-1, :], final_x_syndrome)

    # --- 5. <⭐️ [수정됨]> MWPM 그래프 생성 (총 패리티 검사) ---
    
    # Z-Graph (X 에러 교정)
    z_graph = create_decoding_graph(num_rounds, num_z_ancillas, spatial_edges_z, z_boundary_map, prob_data_x, prob_meas_z)
    z_defect_nodes = []
    z_boundary_node = num_rounds * num_z_ancillas 
    
    # 1. Add bulk defects (R0, R1, R2)
    for r in range(num_rounds):
        for a in range(num_z_ancillas):
            if z_defects[r, a] == 1:
                z_defect_nodes.append(r * num_z_ancillas + a)
    
    # 2. Add final boundary defects
    # (final_z_defects는 R2와 res_bits 사이의 디펙트)
    final_z_defect_count = 0
    for a in range(num_z_ancillas):
        if final_z_defects[a] == 1:
            # 이 디펙트는 R2 슬라이스(12-17)의 노드에 위치
            z_defect_nodes.append((num_rounds - 1) * num_z_ancillas + a)
            final_z_defect_count += 1
            
    # <⭐️ [수정된 로직]>
    # 'final_z_defects'의 합이 아니라, 'z_defect_nodes'의 총 개수로 패리티를 검사
    if len(z_defect_nodes) % 2 == 1:
        z_defect_nodes.append(z_boundary_node)
    
    K_z = nx.Graph()
    for u, v in itertools.combinations(z_defect_nodes, 2):
        path_weight = nx.shortest_path_length(z_graph, source=u, target=v, weight='weight')
        K_z.add_edge(u, v, weight=path_weight)
    z_matching_edges = nx.min_weight_matching(K_z)
    
    z_matching = set()
    for u, v in z_matching_edges:
        path = nx.shortest_path(z_graph, source=u, target=v, weight='weight')
        for i in range(len(path) - 1):
            z_matching.add(tuple(sorted((path[i], path[i+1]))))

    # X-Graph (Z 에러 교정)
    x_graph = create_decoding_graph(num_rounds, num_x_ancillas, spatial_edges_x, x_boundary_map, prob_data_z, prob_meas_x)
    x_defect_nodes = []
    x_boundary_node = num_rounds * num_x_ancillas 

    # 1. Add bulk defects (R0, R1, R2)
    for r in range(num_rounds):
        for a in range(num_x_ancillas):
            if x_defects[r, a] == 1:
                x_defect_nodes.append(r * num_x_ancillas + a)

    # 2. Add final boundary defects
    final_x_defect_count = 0
    for a in range(num_x_ancillas):
        if final_x_defects[a] == 1:
            x_defect_nodes.append((num_rounds - 1) * num_x_ancillas + a)
            final_x_defect_count += 1
            
    # <⭐️ [수정된 로직]>
    if len(x_defect_nodes) % 2 == 1:
        x_defect_nodes.append(x_boundary_node)

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

    # --- 5.5. 교정(Correction) 적용 ---
    
    corrected_res_bits = np.array(res_bits)
    corrected_final_x_syndrome = np.array(final_x_defects) 
    
    # Z-Graph (X-Error) 교정 -> res_bits를 플립
    for u, v in z_matching:
        edge_data = z_graph.get_edge_data(u, v)
        if edge_data is None: continue
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            ancilla_pair = edge_data['qubits'][0] 
            key = tuple(sorted(ancilla_pair)) 
            qubit_to_flip = z_spatial_map.get(key)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]
                
        elif edge_type == 'boundary':
            ancilla_idx = edge_data['qubits'][0][0] 
            qubit_to_flip = z_boundary_map.get(ancilla_idx)
            if qubit_to_flip is not None:
                corrected_res_bits[qubit_to_flip] = 1 - corrected_res_bits[qubit_to_flip]

    # X-Graph (Z-Error) 교정 -> corrected_final_x_syndrome을 플립
    for u, v in x_matching:
        edge_data = x_graph.get_edge_data(u, v)
        if edge_data is None: continue
        edge_type = edge_data['type']
        
        if edge_type == 'spatial':
            ancilla_pair = edge_data['qubits'][0]
            key = tuple(sorted(ancilla_pair))
            qubit_to_flip = x_spatial_map.get(key)
            
            if qubit_to_flip is not None: 
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

        elif edge_type == 'boundary':
            ancilla_idx = edge_data['qubits'][0][0]
            qubit_to_flip = x_boundary_map.get(ancilla_idx)

            if qubit_to_flip is not None: 
                for a_idx, data_qubits in enumerate(x_stabilizers.values()):
                    if f'd[{qubit_to_flip}]' in data_qubits:
                        corrected_final_x_syndrome[a_idx] = 1 - corrected_final_x_syndrome[a_idx]

    # --- 6. 에러 리포트 (디버그 프린트 유지) ---
    
    no_error_injected = (injected_error_group == 'Data' and injected_data_flip_index is None) or \
                          (injected_error_group == 'Measurement' and injected_ancilla_flip_index is None)

    # 1. Z-안정자 재계산
    corrected_final_z_syndrome = calculate_syndrome_from_res(corrected_res_bits, z_stabilizers, num_z_ancillas)
    
    # 2. X-논리 오류 확인
    logical_x_error_parity = corrected_res_bits[2] ^ corrected_res_bits[7] ^ corrected_res_bits[12]
    
    # 3. X-논리 오류 감지
    logical_x_error_detected = any(corrected_final_z_syndrome) or (logical_x_error_parity == 1)
    
    # 4. Z-논리 오류 감지
    logical_z_error_detected = any(corrected_final_x_syndrome)
    
    logical_error_detected = logical_x_error_detected or logical_z_error_detected
    
    # --- [디버그 프린트] ---
    if enable_debug_printing and logical_error_detected:
        print("--- 🐞 DECODER INTERNAL DUMP (UE) 🐞 ---")
        
        # (기존 디버그 프린트 내용)
        injected_error_details = "None"
        if injected_error_group == 'Data' and injected_data_flip_index is not None:
            injected_error_details = f"Data d[{injected_data_flip_index}]"
        elif injected_error_group == 'Measurement' and injected_ancilla_flip_index is not None:
            injected_error_details = f"Meas (R0) Anc[{injected_ancilla_flip_index}]"
        print(f"DEBUG: Injected Error: {injected_error_details}")

        print(f"Parsed sx_bits (R0, R1, R2): {sx_bits}")
        print(f"Parsed sz_bits (R0, R1, R2): {sz_bits}")
        print(f"Parsed res_bits: {res_bits}")
        print(f"X-Defects (R0,R1,R2): {x_defects.T}")
        print(f"Z-Defects (R0,R1,R2): {z_defects.T}")
        print(f"Final X-Defects: {final_x_defects}")
        print(f"Final Z-Defects: {final_z_defects}")
        # <⭐️ [디버그 수정]> 'all_x_defects'를 출력하도록 수정 (함수 스코프 문제로 x_defect_nodes를 다시 계산)
        debug_x_nodes = []
        for r in range(num_rounds):
            for a in range(num_x_ancillas):
                if x_defects[r, a] == 1: debug_x_nodes.append(r*num_x_ancillas+a)
        for a in range(num_x_ancillas):
            if final_x_defects[a] == 1: debug_x_nodes.append((num_rounds-1)*num_x_ancillas+a)
        if len(debug_x_nodes) % 2 == 1: debug_x_nodes.append(x_boundary_node)
        
        debug_z_nodes = []
        for r in range(num_rounds):
            for a in range(num_z_ancillas):
                if z_defects[r, a] == 1: debug_z_nodes.append(r*num_z_ancillas+a)
        for a in range(num_z_ancillas):
            if final_z_defects[a] == 1: debug_z_nodes.append((num_rounds-1)*num_z_ancillas+a)
        if len(debug_z_nodes) % 2 == 1: debug_z_nodes.append(z_boundary_node)

        print(f"X-Defect Nodes (for MWPM): {debug_x_nodes}")
        print(f"Z-Defect Nodes (for MWPM): {debug_z_nodes}")
        
        print(f"X-Matching (edges): {x_matching}")
        print(f"Z-Matching (edges): {z_matching}")
        print(f"Original res_bits: {np.array(res_bits)}")
        print(f"Corrected res_bits: {corrected_res_bits}")
        print(f"Corrected X-Syndrome: {corrected_final_x_syndrome} (Any={any(corrected_final_x_syndrome)})")
        print(f"Corrected Z-Syndrome: {corrected_final_z_syndrome} (Any={any(corrected_final_z_syndrome)})")
        print(f"Logical X Parity (Z_L): {logical_x_error_parity}")
        print(f"-> Result: logical_x_error: {logical_x_error_detected}, logical_z_error: {logical_z_error_detected}")
        print("---------------------------------------")
    # --- [END DEBUG] ---

    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error (에러 주입 O, 논리 에러 X)
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error (논리 에러 O)
    else:
        # (no_error_injected and logical_error_detected)
        return 'UE'