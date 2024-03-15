def LEHexStringToInt(hex_string):

    """
    Usage:
        Given a hex string "hex_sting" it will calculate the little endian
        integer interpretation of the value "int_out" and return that value.
    Args:
        hex_string: the Hex String to be interpretted
    returns:
        int_out: integer derived from "hex_string"
    """

    byte_list = [int(hex_string[i:i + 2], 16) for i in range(0, len(hex_string), 2)]
    significance = 1
    int_out = 0
    for byte in byte_list:
        int_out += byte * significance
        significance *= 256
    return int_out
