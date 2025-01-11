import numpy as np
import random
import utils

def main(p_number, p_length, t):
    # 随机生成一个二进制矩阵作为秘密信息
    message_matrix = np.random.randint(0, 2, (p_number, p_length))

    # LTencoding
    # A为编码矩阵，B为A所对应的索引矩阵
    A, B = utils.LTencoding(message_matrix, t)

    # for i in message_matrix:
    #      print(i)
    # LTdecoding
    # watermarking_decode是解码后的水印，H_decode是解码过程中的索引矩阵
    watermarking_decode, H_decode, tag_decode = utils.LTdecoding(A, B)    
    
    if tag_decode == 1: 
            print('decoding success!')
            print('message_embedded:')
            watermarking =[]
            for i,j in enumerate(message_matrix):
                print(j)
                watermarking.append(watermarking_decode[i])
            print('message_extracted:')
            for i in watermarking:
                print(i)
            print('Is the decoded data consistent with the encoded data?')
            print(utils.are_matrices_equal(message_matrix, watermarking))

    else:
        print('decoding failed')


if __name__ == '__main__':
    # p_number代表原始数据矩阵的行数，p_length代表列数
    # t代表编码数据是原始数据的倍数(t>1)
    p_number = 20
    p_length = 4
    t = 3
    main(p_number, p_length, t)

    