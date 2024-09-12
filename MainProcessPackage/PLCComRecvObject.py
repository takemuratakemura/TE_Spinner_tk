
from struct import unpack_from

class PLCComRecvObject:
    def __init__(self):
        self.f4s_p2_MotSpeed_FR : float = 0.0
        self.f4s_p2_MotSpeed_FL : float = 0.0
        self.f4s_p2_MotSpeed_RR : float = 0.0
        self.f4s_p2_MotSpeed_RL : float = 0.0
        self.us2s_p2_PLC_error : int = 0x00
        self.f4s_p2_WeightPos_LR : float = 0.0
        self.f4s_p2_WeightPos_BF : float = 0.0
        self.us2s_p2_Calib_state : int = 0x00
    
    
    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def decode_recvdata(self, buffer):
        RECV_DATA_SIZE = 30
        bufsize = len(buffer)
        buff_read_point = 0
        if bufsize == RECV_DATA_SIZE * 3:
            buff_read_point = RECV_DATA_SIZE * 2
        elif bufsize == RECV_DATA_SIZE * 2:
            buff_read_point = RECV_DATA_SIZE
        elif bufsize == RECV_DATA_SIZE:
            buff_read_point = 0
        else:
            pass

        self.f4s_p2_MotSpeed_FR,self.f4s_p2_MotSpeed_FL,self.f4s_p2_MotSpeed_RR,self.f4s_p2_MotSpeed_RL,\
        self.us2s_p2_PLC_error,self.f4s_p2_WeightPos_LR,self.f4s_p2_WeightPos_BF,self.us2s_p2_Calib_state \
        = unpack_from('ffffHffH',buffer,buff_read_point)

        #print([self.f4s_p2_MotSpeed_FR,self.f4s_p2_MotSpeed_FL,self.f4s_p2_MotSpeed_RR,self.f4s_p2_MotSpeed_RL,self.us2s_p2_PLC_error,self.f4s_p2_WeightPos_LR,self.f4s_p2_WeightPos_BF])
