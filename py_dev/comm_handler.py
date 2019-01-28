class TypeID:
    POSITION = '\x00'
    ANGLE = '\x01'
    ANGLE_COLOR2WHITE = '\x02'
    ANGLE_COLOR2RED = '\x03'


class TypeName:
    POSITION = 'POSITION'
    ANGLE = 'ANGLE'
    ANGLE_COLOR2WHITE = 'ANGLE_COLOR2WHITE'
    ANGLE_COLOR2RED = 'ANGLE_COLOR2RED'


def bytes_arr2_int_arr(bytes_arr):
    data = []
    for i in bytes_arr:
        data.append(int.from_bytes(i, 'big'))
    return data


def data_resolve(read_data):
    read_data = read_data.decode()
    type_id = read_data[0]
    data = []
    for i in read_data[1:].encode():
        data.append(int.from_bytes(i, 'big'))
    if type_id == TypeID.POSITION:
        return TypeName.POSITION, data
    elif type_id == TypeID.ANGLE:
        return TypeName.ANGLE, data
    return None, []


# return binary packet with 17 chars
# data_type: TypeName
# write_data: (loc1, loc2) or angle or dummy 0
def data_packing(data_type, write_data):
    packet = data_type.encode()
    if data_type == TypeName.POSITION:
        loc1 = write_data[0].to_bytes(8, 'big')
        loc2 = write_data[1].to_bytes(8, 'big')
        packet = packet + loc1 + loc2
    elif data_type == TypeName.ANGLE:
        angl = write_data.to_bytes(16, 'big')
        packet = packet + angl
    elif data_type == TypeName.ANGLE_COLOR2RED or data_type == TypeName.ANGLE_COLOR2WHITE:
        packet = packet + (0).to_bytes(16, 'big')
    return packet


# return binary packet with 18 chars
def tagging_index(packet, index):
    return (chr(index).encode() + packet)
