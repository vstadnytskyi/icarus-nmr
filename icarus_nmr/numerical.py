def int_to_binary(value):
    return bin(value+128)[-7:][::-1]

def int_to_binary_array(value):
    from numpy import asarray
    a = bin(value+128)[-7:][::-1]
    lst = []
    for i in a:
        lst.append(int(i))
    return asarray(lst)

def binary_array_to_int(array):
    num = 0
    for i in range(len(array)):
        num += (2**i) * array[i]
    return num
