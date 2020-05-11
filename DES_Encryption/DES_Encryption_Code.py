import re
import datetime
import os
import shutil

#IP表，初始置换表
IP_Table=[58,50,42,34,26,18,10,2,
    60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6,
    64,56,48,40,32,24,16,8,
    57,49,41,33,25,17,9,1,
    59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5,
    63,55,47,39,31,23,15,7]
# E置换表，用于轮函数FR用到的膨胀函数FE，用来膨胀32变成48
E_Table=[32,1,2,3,4,5,
         4,5,6,7,8,9,
         8,9,10,11,12,13,
         12,13,14,15,16,17,
         16,17,18,19,20,21,
         20,21,22,23,24,25,
         24,25,26,27,28,29,
         28,29,30,31,32,1]
# S盒压缩，轮函数中通过查表进行S盒压缩，6位变4位
SBox_1_table=[[14, 4,  13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7],
              [0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8],
              [4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0],
              [15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13]]
SBox_2_table=[[15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10],
              [3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5],
              [0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15],
              [13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9]]
SBox_3_table=[[10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8],
              [13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1],
              [13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7],
              [1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12]]
SBox_4_table=[[7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15],
              [13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9],
              [10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4],
              [3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14]]
SBox_5_table=[[2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9],
              [14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6],
              [4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14],
              [11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3]]
SBox_6_table=[[12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11],
              [10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8],
              [9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6],
              [4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13]]
SBox_7_table=[[4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1],
              [13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6],
              [1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2],
              [6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12]]
SBox_8_table=[[13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7],
              [1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2],
              [7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8],
              [2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11]]
# P置换表，用于轮函数最后的置换
P_Replace_Table=[16,7,20,21,
                 29,12,28,17,
                 1,15,23,26,
                 5,18,31,10,
                 2,8,24,14,
                 32,27,3,9,
                 19,13,30,6,
                 22,11,4,25]
# 将DES的64位密钥置换成56位密钥的表，表中没有8,16,24，32,40,48,56和64这8位
K_Table_1=[57,49,41,33,25,17,9,1,58,50,42,34,26,18,
           10,2,59,51,43,35,27,19,11,3,60,52,44,36,
           63,55,47,39,31,23,15,7,62,54,46,38,30,22,
           14,6,61,53,45,37,29,21,13,5,28,20,12,4]
# 子密钥压缩置换选择表，从56位中选出48位。这个过程中，既置换了每位的顺序，又选择了子密钥,表中没有9，18，22，25，35，38，43和54这8位
K_Table_2=[14,17,11,24,1,5,3,28,15,6,21,10,
           23,19,12,4,26,8,16,7,27,20,13,2,
           41,52,31,37,47,55,30,40,51,45,33,48,
           44,49,39,56,34,53,46,42,50,36,29,32]

# 文件实例类
class FileInstance:
    def __init__(self,filename,filepath,filecontent):
        self.filename=filename
        self.filepath=filepath
        self.filecontent=filecontent
# 文件夹实例类
class DirInstance:
    def __init__(self,dirpath,auto_flag):
        self.dirpath=dirpath
        self.dircontent_file_list=[]
        self.dircontent_dir_list=[]
        if auto_flag:
            content_list=read_dir(dirpath)
            for item in content_list:
                if IsFile(item):
                    self.dircontent_file_list.append(FileInstance(item,self.dirpath+"/"+item,read_file(self.dirpath+"/"+item)))
                else:
                    self.dircontent_dir_list.append(DirInstance(self.dirpath+"/"+item,True))
    def append_file(self,fileinstance):
        self.dircontent_file_list.append(fileinstance)
    def append_dir(self,dirinstance):
        self.dircontent_dir_list.append(dirinstance)

# 采取广度优先遍历，对一个文件夹节点进行加密操作
def BFS_Encryption(init_di,isfirst,key):
    if isfirst:
        encryed_di=DirInstance("result/Encryption/"+init_di.dirpath,False)
    else:
        encryed_di = DirInstance("result/Encryption/" + init_di.dirpath, False)
        # encryed_di = DirInstance(init_di.dirpath, False)
    for item in init_di.dircontent_file_list:
        encryed_di.append_file(FileInstance(item.filename,encryed_di.dirpath+"/"+item.filename,DES_Go_Encryption(item.filecontent,key)))
    for item in init_di.dircontent_dir_list:
        encryed_di.append_dir(BFS_Encryption(item,False,key))
    return encryed_di
# 采取广度优先遍历，对一个文件夹节点进行解密操作
def BFS_Decode(init_di,isfirst,key):
    if isfirst:
        decode_di=DirInstance("result/Decode/"+init_di.dirpath,False)
    else:
        decode_di = DirInstance("result/Decode/" + init_di.dirpath, False)
        # decode_di = DirInstance(init_di.dirpath, False)
    for item in init_di.dircontent_file_list:
        decode_di.append_file(FileInstance(item.filename,decode_di.dirpath+"/"+item.filename,DES_Go_Decode(item.filecontent,key)))
    for item in init_di.dircontent_dir_list:
        decode_di.append_dir(BFS_Decode(item,False,key))
    return decode_di

# 3DES采取广度优先遍历，对一个文件夹节点进行加密操作
def BFS_Encryption_3DES(init_di,isfirst,key1,key2):
    if isfirst:
        encryed_di=DirInstance("result/Encryption/"+init_di.dirpath,False)
    else:
        encryed_di = DirInstance("result/Encryption/" + init_di.dirpath, False)
        # encryed_di = DirInstance(init_di.dirpath, False)
    for item in init_di.dircontent_file_list:
        encryed_di.append_file(FileInstance(item.filename,encryed_di.dirpath+"/"+item.filename,DES3_Go_Encryption(item.filecontent,key1,key2)))
    for item in init_di.dircontent_dir_list:
        encryed_di.append_dir(BFS_Encryption(item,False,key))
    return encryed_di
# 3DES采取广度优先遍历，对一个文件夹节点进行解密操作
def BFS_Decode_3DES(init_di,isfirst,key1,key2):
    if isfirst:
        decode_di=DirInstance("result/Decode/"+init_di.dirpath,False)
    else:
        decode_di = DirInstance("result/Decode/" + init_di.dirpath, False)
        # decode_di = DirInstance(init_di.dirpath, False)
    for item in init_di.dircontent_file_list:
        decode_di.append_file(FileInstance(item.filename,decode_di.dirpath+"/"+item.filename,DES3_Go_Decode(item.filecontent,key1,key2)))
    for item in init_di.dircontent_dir_list:
        decode_di.append_dir(BFS_Decode(item,False,key))
    return decode_di


# 对一个文件夹节点进行还原工作
def Restore_DirInstance(di):
    mkdir(di.dirpath)
    for item in di.dircontent_file_list:
        mkfile(item.filepath,item.filecontent)
    for item in di.dircontent_dir_list:
        Restore_DirInstance(item)
# 创建文件夹，若原来就有返回False，若原来没有就创建返回Ture
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        return True
    else:
        return False
# 创建一个文件
def mkfile(path,content):
    file = open(path, 'w', encoding='utf-8')
    file.write(content)
    file.close()
    return file
# 给出名称判断是否是文件，若为文件返回Ture，若为文件夹返回False
def IsFile(filename):
    if "." in filename:
        return True
    else:
        return False
# 遍历指定目录，显示目录下的所有文件和文件夹的名字
def read_dir(filepath):
    result=[]
    pathDir =  os.listdir(filepath)
    for allDir in pathDir:
        child = os.path.join('%s' % (allDir))
        result.append(child)
    return result
# 读取文件，返回内容
def read_file(file_name):
    f = open(file_name, 'r', encoding='utf-8')
    message = f.read()
    f.close()
    return message
# 判断字节数并补零
def If_64bit(list_bin):
    p=len(list_bin)
    l=64-(p%64)
    result=[]
    result.extend(list_bin)
    for i in range(l):
        result.extend([0])
    return result

#字符串转二进制
def str_trans_bin(message):
    result = ""
    for i in message:
        tmp = bin(ord(i))[2:]
        for j in range(0, 8 - len(tmp)):
            tmp = '0' + tmp
        result += tmp
    return result
# 二进制转字符串
def bin_trans_str(bin_str):
    result = ""
    tmp = re.findall(r'.{8}', bin_str)  # 每8位表示一个字符
    for i in tmp:
        result += chr(int(i, 2))  # base参数的意思，将该字符串视作2进制转化为10进制
    return result
# 二进制字符串转二进制列表
def str_trans_list(str):
    result=[]
    for item in str:
        result.append(int(item))
    return  result
# 二进制列表转二进制字符串
def list_trans_str(list):
    result=""
    temp_list=[str(i) for i in list]
    result="".join(temp_list)
    return result
# 将二进制列表切割成64比特列表
def init_trans_64bit(init_list):
    result=[]
    j=0
    for i in range(1,len(init_list)+1):
        if i%64==0:
            result.append(init_list[i-64:i])
    return result
# 64比特列表还原成二进制列表
def bit64_trans_init(bit64_list):
    result=[]
    for item in bit64_list:
        result.extend(item)
    return result
# 将一个int类型的数转换成二进制列表
def int_trans_binary(int_num,len_bin):
    result=[]
    temp=list(bin(int_num).replace('0b', ''))
    for i in range(len_bin-len(temp)):
        result.append(0)
    for item in temp:
        result.append(int(item))
    return result
# 将二进制列表转换成十进制
def binary_trans_int(bin_num):
    temp=[]
    for item in bin_num:
        temp.append(str(item))
    temp_str="".join(temp)
    return int(temp_str,2)
# 将两个相同长度的列表进行异或运算，返回他们异或后的结果
def Xor_List_List(data_list_1,data_list_2):
    result=[]
    for i in range(len(data_list_1)):
        result.append(data_list_1[i]^data_list_2[i])
    return result
# 返回IP表
def Show_IP(ip_table):
    return ip_table
# 返回IP表的逆
def Show_IP_Inverse(ip_table):
    result=[]
    temp_count=0
    for i in range(len(ip_table)):
        temp_count=0
        for item in ip_table:
            if(i+1==item):
                result.append(temp_count+1)
            temp_count=temp_count+1
    return result
# 返回表的左边
def Show_Ln(table):
    mid=int(len(table)/2)
    result=table[0:mid]
    return result
# 返回表的右边
def Show_Rn(table):
    mid=int(len(table)/2)
    result=table[mid:]
    return result
# 进行IP置换
def IP_Replace(data_temp,ip_table):
    result=[]
    for ip_item in ip_table:
        result.append(data_temp[ip_item-1])
    return result
# 迭代函数以完成16（15）次迭代交叉运算,每次函数只进行一次交叉，返回拼接后的64位比特列表
def Func_Iteration(data_temp_l,data_temp_R,round_key):
    result=[]
    result_l=data_temp_R
    result_R=Xor_List_List(data_temp_l,Func_Round(data_temp_R,round_key))
    result.extend(result_l)
    result.extend(result_R)
    return result
# 轮函数，用于迭代函数FI中与data_temp_l相异或
def Func_Round(data_temp_r,round_key):
    data_xored=Xor_List_List(Func_Expansion(data_temp_r,E_Table),round_key)
    data_Sed=[]
    data_Sed.extend(Func_SBox_Compress(data_xored[:6], SBox_1_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[6:12], SBox_2_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[12:18], SBox_3_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[18:24], SBox_4_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[24:30], SBox_5_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[30:36], SBox_6_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[36:42], SBox_7_table))
    data_Sed.extend(Func_SBox_Compress(data_xored[42:], SBox_8_table))
    return P_Replace(data_Sed,P_Replace_Table)
# 扩展函数，将32位数据扩展成48为数据，用于函数FR
def Func_Expansion(data_temp_R,e_table):
    result=[]
    for item in e_table:
        result.append(data_temp_R[item-1])
    return result
# S盒压缩处理函数，将FE与Key异或后的48位数据按照S盒压缩处理，接收6位返回4位，用于函数FR
def Func_SBox_Compress(data_six_bits,sbox_n_table):
    result=[]
    temp_list=[]
    temp_list.append(data_six_bits[0])
    temp_list.append(data_six_bits[5])
    row=binary_trans_int(temp_list)
    temp_list.clear()
    temp_list=data_six_bits[1:5]
    line=binary_trans_int(temp_list)
    result=int_trans_binary(sbox_n_table[row][line],4)
    return result
# 按照P表进行置换，同函数IP_Replace，这里重新写了一遍有些重复，主要已经命名了不好改
def P_Replace(data_temp,p_table):
    result=[]
    for p_item in p_table:
        result.append(data_temp[p_item-1])
    return result
# 查询子密钥函数，用到函数FS
def Func_find_Subkey(subkey_list,round):
    return subkey_list[round]
# 密钥置换函数，用于生成子密钥48位，所有结果存成列表
def Func_Subkey(key):
    round_num=1
    result=[]
    result_temp=[]
    temp_56bit=Create_56bit(key, K_Table_1)
    temp_64_l = Show_Ln(temp_56bit)
    temp_64_r = Show_Rn(temp_56bit)
    for round_num in range(16):
        if (round_num==0)or(round_num==1)or(round_num==8)or(round_num==15):
            temp_64_l=list_loop(temp_64_l,1)
            temp_64_r=list_loop(temp_64_r,1)
        else:
            temp_64_l = list_loop(temp_64_l, 2)
            temp_64_r = list_loop(temp_64_r, 2)
        result_temp=temp_64_l+temp_64_r
        result.append(Create_56bit(result_temp,K_Table_2))
    return result
# 密钥置换函数(求解密，需右移)，用于生成子密钥48位，所有结果存成列表
def Func_Subkey_Encryption(key):
    # round_num=1
    #     # result=[]
    #     # result_temp=[]
    #     # temp_56bit=Create_56bit(key, K_Table_1)
    #     # temp_64_l = Show_Ln(temp_56bit)
    #     # temp_64_r = Show_Rn(temp_56bit)
    #     # for round_num in range(16):
    #     #     if (round_num==0)or(round_num==7)or(round_num==14)or(round_num==15):
    #     #         temp_64_l=list_loop(temp_64_l,-1)
    #     #         temp_64_r=list_loop(temp_64_r,-1)
    #     #     else:
    #     #         temp_64_l = list_loop(temp_64_l, -2)
    #     #         temp_64_r = list_loop(temp_64_r, -2)
    #     #     result_temp=temp_64_l+temp_64_r
    #     #     result.append(Create_56bit(result_temp,K_Table_2))
    result=[]
    temp_result=[]
    temp_result=Func_Subkey(key)
    for i in range(len(temp_result)):
        result.append(temp_result[len(temp_result)-i-1])
    return result
# 密钥置换中将64位密钥置换成56位密钥,56转48，同函数IP_Replace,，，，，哭了，要不把这个专门弄成一个函数。。。
def Create_56bit(key,k_table_1):
    result = []
    for k_item in k_table_1:
        result.append(key[k_item - 1])
    return result
# 函数实现列表循环左移（>0）和列表循环右移（<0）
def list_loop(data_list,num):
    return data_list[num:]+data_list[:num]
# 一次64位加密过程
def Encryption_64bit(data,key):
    key_list = Func_Subkey(key)
    temp_64 = IP_Replace(data, Show_IP(IP_Table))
    for loop_i in range(15):
        temp_64 = Func_Iteration(Show_Ln(temp_64), Show_Rn(temp_64), Func_find_Subkey(key_list, loop_i))
    temp_64_r = Show_Rn(temp_64)
    temp_64_l = Xor_List_List(Show_Ln(temp_64), Func_Round(Show_Rn(temp_64), Func_find_Subkey(key_list, 15)))
    temp_64 = temp_64_l + temp_64_r
    result = IP_Replace(temp_64, Show_IP_Inverse(IP_Table))
    return result
# 三次DES加密过程
def DES3_Encryption_64bit(data,key1,key2):
    temp_1 = Encryption_64bit(data, key1)
    temp_2 = Decode_64bit(temp_1, key2)
    result = Encryption_64bit(temp_2, key1)
    return result
# 一次64位解密过程
def Decode_64bit(data,key):
    key_list = Func_Subkey_Encryption(key)
    temp_64 = IP_Replace(data, Show_IP(IP_Table))
    for loop_i in range(15):
        temp_64 = Func_Iteration(Show_Ln(temp_64), Show_Rn(temp_64), Func_find_Subkey(key_list, loop_i))
    temp_64_r = Show_Rn(temp_64)
    temp_64_l = Xor_List_List(Show_Ln(temp_64), Func_Round(Show_Rn(temp_64), Func_find_Subkey(key_list, 15)))
    temp_64 = temp_64_l + temp_64_r
    result = IP_Replace(temp_64, Show_IP_Inverse(IP_Table))
    return result
# 三次DES解密过程
def DES3_Decode_64bit(data,key1,key2):
    temp_1 = Decode_64bit(data, key1)
    temp_2 = Encryption_64bit(temp_1, key2)
    result = Decode_64bit(temp_2,key1)
    return result
# 读取文件，返回内容字符串                                     def read_file(file_name):
# 字符串转二进制字符串                                         def str_trans_bin(message):
# 二进制字符串转二进制列表                                     def str_trans_list(str):
# 二进制列表转二进制字符串                                     def list_trans_str(list):
# 将二进制列表切割成64比特列表                                 def init_trans_64bit(init_list):
# 64比特列表还原成二进制列表                                   def bit64_trans_init(bit64_list):
# 将一个int类型的数转换成二进制列表                            def int_trans_binary(int_num,len_bin):
# 将二进制列表转换成十进制                                     def binary_trans_int(bin_num):
# 将两个相同长度的列表进行异或运算，返回他们异或后的结果       def Xor_List_List(data_list_1,data_list_2):
# 返回IP表                                                     def Show_IP(ip_table):
# 返回IP表的逆                                                 def Show_IP_Inverse(ip_table):
# 返回表的左边                                                 def Show_Ln(table):
# 返回表的右边                                                 def Show_Rn(table):
# 进行IP置换                                                   def IP_Replace(data_temp,ip_table):
# 迭代函数以完成16（15）次迭代交叉运算,每次函数只进行一次交叉，返回拼接后的64位比特列表
#                                                              def Func_Iteration(data_temp_l,data_temp_R,round_key):
# 轮函数，用于迭代函数FI中与data_temp_l相异或                  def Func_Round(data_temp_r,round_key):
# 扩展函数，将32位数据扩展成48为数据，用于函数FR               def Func_Expansion(data_temp_R,e_table):
# S盒压缩处理函数，将FE与Key异或后的48位数据按照S盒压缩处理，接收6位返回4位，用于函数FR
#                                                              def Func_SBox_Compress(data_six_bits,sbox_n_table):
# 按照P表进行置换，同函数IP_Replace                            def P_Replace(data_temp,p_table):
# 查询子密钥函数，用到函数FS                                   def Func_find_Subkey(subkey_list,round):
# 密钥置换函数，用于生成子密钥48位，所有结果存成列表           def Func_Subkey(key):
# 密钥置换中将64位密钥置换成56位密钥,56转48                    def Create_56bit(key,k_table_1):
# 函数实现列表循环左移（>0）和列表循环右移（<0）               def list_loop(data_list,num):
# 一次64位加密过程                                             def Encryption_64bit(data,key):
# 一次64位解密过程                                             def Decode_64bit(data,key):

# 函数开始
def DES_Go_Encryption(filetxt,key):
    Data_64bit=[]
    Data_Inital=[]
    Data_Temp_64bit_Encrypted=[]

    Data_Encrypted=[]
    Data_Decoded=[]
    Txt_Init=""
    Txt_Encrypted=""
    Txt_Decode=""
    Key=[]
    Txt_Init=filetxt
    Key=key
    # print("文件内容：",Txt_Init)
    Data_Inital=str_trans_list(str_trans_bin(Txt_Init))
    # print("加密前的比特流：",Data_Inital)
    # print("加密前的比特流：",len(Data_Inital))
    Data_Inital=If_64bit(Data_Inital)
    Data=init_trans_64bit(Data_Inital)
    for data_item in Data:
        Data_Temp_64bit_Encrypted.append(Encryption_64bit(data_item,Key))
    Data_Encrypted=bit64_trans_init(Data_Temp_64bit_Encrypted)
    # print("加密后得到比特流：",Data_Encrypted)
    # print("加密后得到比特流：",len(Data_Encrypted))
    Txt_Encrypted=bin_trans_str(list_trans_str(Data_Encrypted))
    # print("加密后得到字符流：",Txt_Encrypted)
    return Txt_Encrypted

def DES_Go_Decode(Txt_Encrypted,key):
    Key=key
    Data_Temp_64bit_Decoded = []
    Data_little64 = init_trans_64bit(If_64bit(str_trans_list(str_trans_bin(Txt_Encrypted))))
    # Data_little64=init_trans_64bit(Data_Encrypted)
    for item in Data_little64:
        Data_Temp_64bit_Decoded.extend(Decode_64bit(item,Key))
    Data_Decoded=Data_Temp_64bit_Decoded
    # print("解密后得到比特流：",Data_Decoded)
    Txt_Decode=bin_trans_str(list_trans_str(Data_Decoded))
    # print("解密后得到字符流：",Txt_Decode)
    return Txt_Decode


def DES3_Go_Encryption(filetxt,key1,key2):
    Data_64bit = []
    Data_Inital = []
    Data_Temp_64bit_Encrypted = []
    Data_Encrypted = []
    Data_Decoded = []
    Txt_Init = ""
    Txt_Encrypted = ""
    Txt_Decode = ""
    Key = []

    Txt_Init = filetxt
    Key1 = key1
    Key2 = key2
    # print("文件内容：", Txt_Init)
    Data_Inital = str_trans_list(str_trans_bin(Txt_Init))
    # print("加密前的比特流：", Data_Inital)
    # print("加密前的比特流：", len(Data_Inital))
    Data_Inital = If_64bit(Data_Inital)
    Data = init_trans_64bit(Data_Inital)
    for data_item in Data:
        Data_Temp_64bit_Encrypted.append(DES3_Encryption_64bit(data_item, Key1,Key2))
    Data_Encrypted = bit64_trans_init(Data_Temp_64bit_Encrypted)
    # print("加密后得到比特流：", Data_Encrypted)
    # print("加密后得到比特流：", len(Data_Encrypted))
    Txt_Encrypted = bin_trans_str(list_trans_str(Data_Encrypted))
    # print("加密后得到字符流：", Txt_Encrypted)
    return Txt_Encrypted

def DES3_Go_Decode(Txt_Encrypted, key1,key2):
    Data_Temp_64bit_Decoded = []
    Key1 = key1
    Key2 = key2
    Data_little64 = init_trans_64bit(If_64bit(str_trans_list(str_trans_bin(Txt_Encrypted))))
    # Data_little64 = init_trans_64bit(Data_Encrypted)
    for item in Data_little64:
        Data_Temp_64bit_Decoded.extend(DES3_Decode_64bit(item,  Key1,Key2))
    Data_Decoded = Data_Temp_64bit_Decoded
    # print("解密后得到比特流：", Data_Decoded)
    Txt_Decode = bin_trans_str(list_trans_str(Data_Decoded))
    # print("解密后得到字符流：", Txt_Decode)
    return Txt_Decode


# 对于本实验专门的文件夹移动删除操作
def Move_Dir():
    shutil.copytree("result/Encryption/result/init", "result/Encryption_result")
    shutil.copytree("result/Decode/result/Encryption/result/init", "result/Descryption_result")
    if os.path.exists("result/Encryption"):
        shutil.rmtree("result/Encryption")
    if os.path.exists("result/Decode"):
        shutil.rmtree("result/Decode")
def Delect_Dir():
    print("需要加密的文件目录是result/init")
    print("加密完成后的文件目录是result/Encryption_result，程序是先在result/Encryption/result/init目录下完成对文件夹的加密，然后将其迁移到result/Encryption_result")
    print("解密完成后的目录是result/Descryption_result，程序是先在result/Decode/result/Encryption/result/init目录下完成对文件夹的解密，然后将其迁移到result/Descryption_result")
    print("加密前程序会删除除目录result/init外所有的目录")
    print("加密完成后程序会删除目录result/Encryption和目录result/Decode，所以您看不到中间过程的目录")
    if os.path.exists("result/Encryption_result"):
        shutil.rmtree("result/Encryption_result")
    if os.path.exists("result/Descryption_result"):
        shutil.rmtree("result/Descryption_result")
    if os.path.exists("result/Encryption"):
        shutil.rmtree("result/Encryption")
    if os.path.exists("result/Decode"):
        shutil.rmtree("result/Decode")

# 主函数开始
# 如果需要使用3DES加密，请把最下面的注释去掉
Delect_Dir()
num=int(input("请输入一个数字："))
key=int_trans_binary(num,64)
init_di=DirInstance("result/init",True)
encry_di=BFS_Encryption(init_di,True,key)
Restore_DirInstance(encry_di)
Restore_DirInstance(BFS_Decode(encry_di,True,key))
Move_Dir()




# 3DES
# Delect_Dir()
# num1=int(input("请输入一个数字："))
# key1=int_trans_binary(num1,64)
# num2=int(input("请输入一个数字："))
# key2=int_trans_binary(num2,64)
# init_di=DirInstance("result/init",True)
# encry_di=BFS_Encryption_3DES(init_di,True,key1,key2)
# Restore_DirInstance(encry_di)
# Restore_DirInstance(BFS_Decode_3DES(encry_di,True,key1,key2))
# Move_Dir()
