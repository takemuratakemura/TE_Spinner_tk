from bluepy.btle import DefaultDelegate, Peripheral,ADDR_TYPE_RANDOM

# MicrobitのMAC
MAC_ADDRESS = 'F3:52:BC:B2:86:72'

#ACCELEROMETER SERVICE/CHARACTERISTICS UUID
ACC_SERVICE_UUID = 'E95D0753251D470AA062FA1922DFA9A8'
ACC_CHARACTERISTICS_UUID = 'E95DCA4B251D470AA062FA1922DFA9A8'

#BUTTON SERVICE/BUTTON A CHARACTERISTICS UUID
BTN_SERVICE_UUID = 'E95D9882251D470AA062FA1922DFA9A8'
BTN_A_CHARACTERISTICS_UUID = 'E95DDA90251D470AA062FA1922DFA9A8'
BTN_B_CHARACTERISTICS_UUID = 'E95DDA91251D470AA062FA1922DFA9A8'

#TEMPATURE SERVICE/CHARACTERISTICS UUID
TMP_SERVICE_UUID = 'E95D6100251D470AA062FA1922DFA9A8'
TMP_CHARACTERISTICS_UUID = 'E95D9250251D470AA062FA1922DFA9A8'


def read_mbit():
    # 接続設定
    peripheral = Peripheral(MAC_ADDRESS, ADDR_TYPE_RANDOM)
    # - 加速度センサー
    acc_service = peripheral.getServiceByUUID(ACC_SERVICE_UUID)
    acc_characteristic = peripheral.getCharacteristics(uuid=ACC_CHARACTERISTICS_UUID)
    # - ボタン
    btn_service = peripheral.getServiceByUUID(BTN_SERVICE_UUID)
    btn_A_characteristic = peripheral.getCharacteristics(uuid=BTN_A_CHARACTERISTICS_UUID)
    btn_B_characteristic = peripheral.getCharacteristics(uuid=BTN_B_CHARACTERISTICS_UUID)
    # - 温度センサー
    tmp_service = peripheral.getServiceByUUID(TMP_SERVICE_UUID)
    tmp_characteristic = peripheral.getCharacteristics(uuid=TMP_CHARACTERISTICS_UUID)

    '''
    print("<" * 20)
    '''
    
    # 値の読み取り
    acc_read_data = acc_characteristic[0].read()
    btna_read_data =btn_A_characteristic[0].read()
    btnb_read_data =btn_B_characteristic[0].read()
    tmp_read_data = tmp_characteristic[0].read()

    # 加速度センサー
    x = int.from_bytes(acc_read_data[0:2], byteorder='little', signed=True)
    y = int.from_bytes(acc_read_data[2:4], byteorder='little', signed=True)
    z = int.from_bytes(acc_read_data[4:6], byteorder='little', signed=True)

    '''
    # 加速度の表示
    print(f"ACCELEROMETER - x:{int(x/10)}, y:{y/10}, z:{z/10}")

    # ボタン状態の表示
    print(f"btn A:{btna_read_data[0]}")
    print(f"btn B:{btnb_read_data[0]}")

    # 温度の表示
    print(f"temp:{tmp_read_data[0]}")
    '''

    return x, y, z, btna_read_data[0], btnb_read_data[0], tmp_read_data[0]


'''
if __name__ == "__main__":
    main()
'''
