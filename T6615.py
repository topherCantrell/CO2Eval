
class T6615:

    def __init__(self,uart,address):
        self._uart = uart
        self._address = bytes([address])

    def _read_response(self):        
        #header = [-1,-1,-1]
        #a = self._uart.read(1)
        #print('>>a ',a)
        #b = self._uart.read(1)
        #print('>>b ',b)
        #c = self._uart.read(1)
        #print('>>c ',c)
        #header[0] = a[0]
        #header[1] = b[0]
        #header[2] = c[0]        
        header = self._uart.read(3)
        #print('HEADER:',header)
        data = self._uart.read(header[2])
        #print('DATA:',data)
        return header,data        

    def _send_request(self,data):
        cmd = b'\xFF' + self._address + bytes([len(data)]) + bytes(data)
        #print('SENDING:',list(cmd))
        self._uart.write(cmd)
        
    def get_status(self):        
        self._send_request([0xB6])
        _,data = self._read_response()
        # print(list(header),list(data))
        return data[0]

    def get_CO2(self):
        self._send_request([0x02,0x03])
        _,data = self._read_response()
        # print(list(header),list(data))
        return data[0]*256+data[1]

    def get_serial_number(self):
        self._send_request([0x02,0x01])
        _,data = self._read_response()
        # print(list(header),list(data))
        if b'\x00' in data:
            data = data[0:data.index(b'\x00')]
        return data.decode()

    def get_compile_subvol(self):
        self._send_request([0x02,0x0D])
        _,data = self._read_response()
        # print(list(header),list(data))
        return data.decode()

    def get_compile_date(self):
        self._send_request([0x02,0x0C])
        _,data = self._read_response()
        # print(list(header),list(data))
        return data.decode()

    def get_elevation(self):
        self._send_request([0x02,0x0F])
        _,data = self._read_response()
        # print(list(header),list(data))
        return data[0]*256+data[1]    

    def get_abc_logic_enabled(self):
        self._send_request([0xB7,0x00])
        _,data = self._read_response()
        return data[0]==1

    def set_reference_ppm(self,v):
        a = (v>>8)&0xFF
        b = v&0xFF
        self._send_request([0x03,0x11,a,b])
        _,_ = self._read_response()        

    def do_single_point_calibration(self):
        # Set the reference GAS value        
        self._send_request([0x9B])
        _,_ = self._read_response()
    
    def get_single_point_calibration(self):
        self._send_request([0x02,0x11])
        _,data = self._read_response()    
        return data[0]*256+data[1]         

    # The Telaire T6615 does not have ABC
    
    """
    def reset_abc_logic(self):
        self._send_request([0xB7,0x03])
        _,data = self._read_response()
        return data[0]==1

    def set_abc_logic_enabled(self, en=True):
        if en:
            self._send_request([0xB7,0x01])
            _,data = self._read_response()
            return data[0]==1
        else:
            self._send_request([0xB7,0x02])
            _,data = self._read_response()
            return data[0]==2   
    """

    def enable_idle(self,en=True):
        if en:
            self._send_request([0xB9,0x01])
            _,data = self._read_response()
        else:
            self._send_request([0xB9,0x02])
            _,data = self._read_response()

    def do_warmup(self):
        raise NotImplementedError()

    def set_elevation(self,v):
        raise NotImplementedError()

    

    

