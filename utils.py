import numpy as np
import random

# LTencoding
def LTencoding(message_matrix, t):
    # 获取水印矩阵的行数和列数
    packet_num, packet_length = message_matrix.shape

    # 编码数据包的数量是原始数据包数量的t倍
    packet_number = t * packet_num 

    # A为编码矩阵，B为A所对应的索引矩阵
    A = []
    B = []

    # 生成鲁棒孤波分布矩阵
    distribution_rs = robust_soliton(packet_num)
    # 将概率列表转换为np数组
    distribution_rs_np = np.array(distribution_rs)
    possible_values = np.arange(1, len(distribution_rs_np) + 1)

    # encoding
    for i in range(packet_number):
        # 根据给定的度概率分布选择度
        send_degree = np.random.choice(possible_values, p=distribution_rs_np)

        # 编码初始化
        # code_encode为一个编码包的数据
        # H表示在生成一个编码包时，所使用的序号为1，未使用的为0
        code_encode = [0] * packet_length
        H = [0] * packet_num

        # 选择哪几个原始数据包为编码包的异或结果
        message_encode_pos = []

        # 开始选择原始数据包         
        # 随机挑选度数个原始数据包          
        # send_degree为本次的度数        
        # 当i<=度数send_degree时，则一直保持循环，直到经过度数次
        i = 1
        # 使用 while 循环计算从 1 到 10 的数字之和
        while i <= send_degree:
            i += 1
            # 生成一个在 0 到 packet_num - 1 范围内的随机整数
            temp_pos = random.randint(0, packet_num - 1)
            if H[temp_pos] == 0:
                H[temp_pos] = 1     
                # 把用到的包的序号全部记录下来  
                message_encode_pos.append(temp_pos)
            # 如果这个包之前被选择过，则重新选择一次
            else:
                i = i - 1

        for i in message_encode_pos:
            code_encode = np.array(code_encode)
            code_encode = (code_encode + message_matrix[i, :]) % 2

        code_encode = code_encode.tolist()
        A.append(code_encode)
        B.append(H)

    return A, B

# LTdecoding
def LTdecoding(A, B):
    
    
    # watermarking_decode是解码后的水印，H_decode是解码过程中的索引矩阵
    watermarking_decode = [[0 for _ in range(len(A[0]))] for _ in range(len(B[0]))]
    H_decode = [[0 for _ in range(len(B[0]))] for _ in range(len(B[0]))]
    
    rank_statistic=[]
    # tag_decode = 0代表解码失败，= 1代表成功
    tag_decode=0

    watermarking_decode, H_decode, tag_decode = LT_decode_BP(A, B, watermarking_decode, H_decode)
    return watermarking_decode, H_decode, tag_decode
    

# 生成鲁棒孤波分布
def robust_soliton(packet_num):
    # 理想孤波分布
    p_ideal = [0] * packet_num
    for i in range(packet_num):
        if i == 0:
            p_ideal[i] = 1/packet_num
        else:
            p_ideal[i] = 1/((i+1)*i)

    # 鲁棒孤波分布
    r = 0.05
    delta = 0.05
    R = r * np.log(packet_num / delta) * np.sqrt(packet_num)
    degree_max = round(packet_num / R)

    p = [0] * degree_max
    p_robust = p_ideal
    for i in range(degree_max):
        if i == degree_max-1:
            p[i] = R*np.log(R/delta)/packet_num
        else:
            p[i] = R / ((i+1)*packet_num) 

    
    for i in range(degree_max):
        p_robust[i] = p_ideal[i] + p[i]

    # 归一化
    total_sum = sum(p_robust)
    p_robust = [x / total_sum for x in p_robust]
    
    threshold = 0.1 / packet_num
    max_num = degree_max
    
    for i in range(len(p_robust) - 1, -1, -1):
        if p_robust[i] > threshold:
            max_num = i + 1
            break
          
    distribution_rs = p_robust[:max_num]
    temp_sum = sum(distribution_rs)
    distribution_rs = [x / temp_sum for x in distribution_rs]

    return distribution_rs

# 求对矩阵对角元素为一的个数
def find_rank(H):
    rank_value = 0
    num_rows = len(H)
    num_cols = len(H[0]) if len(H) > 0 else 0
    # 获取行数和列数中的较小值
    min_size = min(num_rows, num_cols)
    
    for i in range(min_size):
        if H[i][i] == 1:
            rank_value += 1
    return rank_value


# 判断矩阵是否相同
def are_matrices_equal(matrix1, matrix2):
    return (len(matrix1) == len(matrix2) and
            all(len(row1) == len(row2) for row1, row2 in zip(matrix1, matrix2)) and
            all(elem1 == elem2 for row1, row2 in zip(matrix1, matrix2) for elem1, elem2 in zip(row1, row2)))

def set_element(lst, index, value):
    # 如果索引超出了当前列表长度，扩展列表
    if index >= len(lst):
        lst.extend([None] * (index + 1 - len(lst)))
    lst[index] = value

# BP解码
def LT_decode_BP(code, H, watermark_decode, H_decode):
    tag_decode = 0
    
    # 记录度为1的编码数据包在数组中的下标
    degree_1 = []
    for i, j in enumerate(H):
        if j.count(1) == 1:
            degree_1.append(i)

    # 记录解码过程中每个数据包的使用情况，0代表未被使用，1代表已被使用
    used_code = [0] * len(H)
    
    # 如果没有度为一的包，则解码失败
    if len(degree_1) == 0:
        return watermark_decode, H_decode, tag_decode
    
    full_rank = len(H_decode)
    # 如果H_decode是单位矩阵或degree_1中已没有元素时结束解码
    while(find_rank(H_decode) != full_rank and len(degree_1) != 0):
        
        # 检查degree_1中的元素的度是否为1,如果不是1则从degree_1中删除并跳出本次循环
        if H[degree_1[0]].count(1) != 1:
            del degree_1[0]
            continue

        # 处理每个度为一的数据
        # print('='*100)
        # print('H:',H)
        # print('code:',code)
        # print('degree_1:',degree_1)
        # print('H[degree]:', H[degree_1[0]])
        
        # 确定度为一的下标
        index_of_one = H[degree_1[0]].index(1)
        # print('index_of_one:',index_of_one)
        # 添加
        H_decode[index_of_one][index_of_one] = 1
        # print('H_decode[index_of_one]:', H_decode[index_of_one])
        watermark_decode[index_of_one] = code[degree_1[0]]
        # print('watermark_decode[index_of_one]:', watermark_decode[index_of_one])
        

        # 消度
        for a, b in enumerate(H):
            if (b[index_of_one] == 1) and (a != degree_1[0]):
                # print('b:',b)
                H[a][index_of_one] = 0
                code[a] = [x ^ y for x, y in zip(code[a], code[degree_1[0]])]
        
        
        for x, y in enumerate(H):
            if (y.count(1) == 1) and (x not in degree_1) and (used_code[x] == 0):
                degree_1.append(x)

        used_code[degree_1[0]] = 1
        del degree_1[0]

    if find_rank(H_decode) == full_rank:
        tag_decode = 1
    return watermark_decode, H_decode, tag_decode
            

def LT_decode_Gaussian():
    pass

