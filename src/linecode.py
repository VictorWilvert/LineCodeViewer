
def generate_ami_b8zs_base(binary_list, init_cond, is_b8zs, is_pseudoternary=False):

    last = 1 if init_cond else -1
    zeroes = 0

    result = []
    for bit in binary_list:

        if bool(bit) is not is_pseudoternary:
            zeroes = 0
            last = -last
            code_value = last
        else:
            zeroes += 1
            code_value = 0

        result.append(code_value)

        if is_b8zs and zeroes == 8:
            result[-5] = result[-1] = last
            result[-4] = result[-2] = -last
            zeroes = 0

    return result

def generate_ami(binary_list, init_cond):

    return generate_ami_b8zs_base(binary_list, init_cond, False)

def generate_machester_differential(binary_list, init_cond):

    result = [1]
    if init_cond is not None:
        result = [int(init_cond)]
    for bit in binary_list:
        result.append(result[-1] if bit else (result[-1] + 1) % 2)
        result.append(0 if result[-1] else 1)

    return result[1:]

def generate_manchester(binary_list, _):

    result = []
    for bit in binary_list:
        result.append(0 if bit else 1)
        result.append(bit)

    return result

def generate_nrz_polar_l(binary_list, _):

    return [-1 if bit else 1 for bit in binary_list]    #NRZ-L

def generate_nrz_unipolar(binary_list, _):

    return binary_list

def generate_nrz_polar_i(binary_list, init_cond):

    result = [1]
    if init_cond is not None:
        result = [int(init_cond)]
    for bit in binary_list:
        result.append(result[-1] if not bit else (result[-1] + 1) % 2)

    return result[1:]

def generate_nrz_4b5b(binary_list, _):

    dicionary = {
        "0000" : [1, 1, 1, 1, 0],
        "0001" : [0, 1, 0, 0, 1],
        "0010" : [1, 0, 1, 0, 0],
        "0011" : [1, 0, 1, 0, 1],
        "0100" : [0, 1, 0, 1, 0],
        "0101" : [0, 1, 0, 1, 1],
        "0110" : [0, 1, 1, 1, 0],
        "0111" : [0, 1, 1, 1, 1],
        "1000" : [1, 0, 0, 1, 0],
        "1001" : [1, 0, 0, 1, 1],
        "1010" : [1, 0, 1, 1, 0],
        "1011" : [1, 0, 1, 1, 1],
        "1100" : [1, 1, 0, 1, 0],
        "1101" : [1, 1, 0, 1, 1],
        "1110" : [1, 1, 1, 0, 0],
        "1111" : [1, 1, 1, 0, 1]
        }

    str_list = ''.join(str(bit) for bit in binary_list)

    result = []
    for i in range(0, len(str_list), 4):
        result += dicionary[str_list[i: i + 4]]


    return result

def generate_rz(binary_list, _):

    result = [0]*len(binary_list)*2

    for i, val in enumerate(binary_list):
        result[2*i] = 1 if val else -1

    return result

def generate_b8zs(binary_list, init_cond):

    return generate_ami_b8zs_base(binary_list, init_cond, True)

def generate_2b1q(binary_list, _):

    result = []
    for i in range(0, len(binary_list)-1, 2):
        result.append(1 if binary_list[i] else -1)
        if binary_list[i+1] == 0:
            result[-1] *= 3

    return result

def generate_mlt3(binary_list, init_cond):

    growing = (init_cond == 1)

    if init_cond == 0:
        last = 1
    elif init_cond == 3:
        last = -1
    else:
        last = 0

    result = []
    for bit in binary_list:
        if bit:
            if growing:
                last += 1
            else:
                last -= 1

            if last > 1 or last < -1:
                last = 0
                growing = not growing

        result.append(last)

    return result

def generate_pseudoternary(binary_list, init_cond):

    return generate_ami_b8zs_base(binary_list, init_cond, False, True)

def function_vector():
    #
    ret_val = {"Unipolar NRZ-L" : generate_nrz_unipolar,
               "Bipolar NRZ-L" : generate_nrz_polar_l,
               #"Unipolar NRZ-I" : ,
               "Bipolar NRZ-I" : generate_nrz_polar_i,
               #"Unipolar NRZ-M" : ,
               #"Bipolar NRZ-M" : ,
               #"Unipolar NRZ-S" : ,
               #"Bipolar NRZ-S" : ,
               "Bipolar RZ" : generate_rz,
               "AMI" : generate_ami,
               "Pseudoternay" : generate_pseudoternary,
               "Manchester" : generate_manchester,
               "Differential Manchester" : generate_machester_differential,
               "MLT-3" : generate_mlt3,
               "2B1Q" : generate_2b1q,}
    return ret_val


