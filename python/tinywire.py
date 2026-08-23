# TinyWire Protocol — Clean Layer 2 + Layer 3 APIs
# Pure Python / MicroPython compatible

SOF = 0x00

class TWPacket:
    """Tiny-wire packet. Use >= 0x0100 for custom errors"""
    TW_ERR_NONE             = 0x0000
    TW_ERR_INVALID_REGISTER = 0x0001
    TW_ERR_WRITE_PROTECTED  = 0x0002
    TW_ERR_OUT_OF_RANGE     = 0x0003
    TW_ERR_BUSY             = 0x0004
    TW_ERR_CRC_MISMATCH     = 0x0005
    TW_ERR_HW_FAULT         = 0x0006
    
    def __init__(self):
        self._raw = bytearray(8)
    
    @property
    def is_response(self):
        return not self.is_request
        
    @property
    def is_request(self):
        return (self._raw[1] & 0x80) == 0
        
    @property
    def is_read_request(self):
        
        return (self._raw[1] & 0xA0) == 0x20

    @property
    def is_write_request(self):
        """Check if a write"""
        return (self._raw[1] & 0xA0) == 0x00
    
    @property
    def is_read_response(self):
        
        return (self._raw[1] & 0xA0) == 0xA0

    @property
    def is_write_response(self):
        """Check if a write"""
        return (self._raw[1] & 0xA0) == 0x80
    
    @property
    def is_error(self):
        """Check if we got a error back"""
        return (self._raw[1] & 0xC0) == 0xC0

    @property
    def is_ack_required(self):
        """Return true if ack is required"""
        return (self._raw[1] & 0xC0) == 0x40
        
    @property
    def error_code(self):
        if self.is_request:
            return None
        
        if not self.is_error:
            return None
        
        #extract error code.
        return self._raw[5]<<8 | self._raw[6]
        
    @property
    def node(self):
        return self._raw[2]
        
    @property
    def index(self):
        return self._raw[3]<<8 | self._raw[4]

    @property
    def value(self):
        if self.is_error:
            return None
        return self._raw[5]<<8 | self._raw[6]
    
    def as_bytes(self):
        """Get the packet as bytes"""
        return self._raw
    
    @staticmethod
    def create_write_request(node, index, data, ack=False, pkt=None):
        pkt = pkt or TWPacket()

        pkt._raw[0] = 0x00   #Reset Start of frame pos

        #header write request
        if ack:
            pkt._raw[1] = 0x40
        else:
            pkt._raw[1] = 0x00
            
        pkt._raw[2] = node
        pkt._raw[3] = (index>>8) & 0xFF
        pkt._raw[4] = (index>>0) & 0xFF
        pkt._raw[5] = (data>>8) & 0xFF
        pkt._raw[6] = (data>>0) & 0xFF
        pkt._raw[7] = 0x00   #Reset CRC8 pos
        
        return pkt
        
    @staticmethod
    def create_read_request(node, index, pkt=None):
        pkt = pkt or TWPacket()

        pkt._raw[0] = 0x00   #Reset Start of frame pos
    
        #header - Read request
        pkt._raw[1] = 0x20
            
        pkt._raw[2] = node
        pkt._raw[3] = (index>>8) & 0xFF
        pkt._raw[4] = (index>>0) & 0xFF
        pkt._raw[5] = 0x00   #Not used
        pkt._raw[6] = 0x00   #Not used
        pkt._raw[7] = 0x00   #Reset CRC8 pos
        
        return pkt
        
    @staticmethod
    def create_write_response(node, index, data=None, error_code=None, pkt=None):
        pkt = pkt or TWPacket()

        pkt._raw[0] = 0x00   #Reset Start of frame pos

        #header write response
        if error_code:
            pkt._raw[1] = 0xC0
        else:
            pkt._raw[1] = 0x80
            
        pkt._raw[2] = node
        pkt._raw[3] = (index>>8) & 0xFF
        pkt._raw[4] = (index>>0) & 0xFF
        if error_code:
            pkt._raw[5] = (error_code>>8) & 0xFF
            pkt._raw[6] = (error_code>>0) & 0xFF
        else:
            pkt._raw[5] = (data>>8) & 0xFF
            pkt._raw[6] = (data>>0) & 0xFF
        pkt._raw[7] = 0x00   #Reset CRC8 pos

        return pkt
    
    @staticmethod
    def create_read_response(node, index, data=None, error_code=None, pkt=None):
        pkt = pkt or TWPacket()

        pkt._raw[0] = 0x00   #Reset Start of frame pos

        #header read response
        if error_code:
            pkt._raw[1] = 0xE0
        else:
            pkt._raw[1] = 0xA0
            
        pkt._raw[2] = node
        pkt._raw[3] = (index>>8) & 0xFF
        pkt._raw[4] = (index>>0) & 0xFF
        if error_code:
            pkt._raw[5] = (error_code>>8) & 0xFF
            pkt._raw[6] = (error_code>>0) & 0xFF
        else:
            pkt._raw[5] = (data>>8) & 0xFF
            pkt._raw[6] = (data>>0) & 0xFF
        pkt._raw[7] = 0x00   #Reset CRC8 pos

        return pkt

    @staticmethod 
    def decode(frame, pkt=None):
        pkt = pkt or TWPacket()
        
        if len(frame) != 8:
            raise ValueError("frame not 8byte long")
        
        pkt._raw = frame        
        return pkt
        
    def __str__(self):
        """Show info"""
        l = [
            "Packet:",
            f"  ------ Metadata ------",
            f"  Write req: {self.is_write_request}",
            f"  Read req: {self.is_read_request}",
            f"  Ack Req: {self.is_ack_required}",
            f"  Write resp: {self.is_write_response}",
            f"  Read resp: {self.is_read_response}",
            f"  Error code: {self.error_code}",
            f"  ------ Content -------",
            f"  Node:{self.node}",
            f"  Index:{self.index}",
            f"  Value:{self.value}",
        ]
        
        return '\n'.join(l)
        
class TWStreamReceiver:
    """A stream receiver for tiny-wire"""
    def __init__(self):
        self._buf = bytearray(8)
        self._pos = 0

    def reset(self):
        self._pos = 0

    def feed(self, b):
        """Feed one byte. Return decoded frame or None."""
        # SOF always resets state
        if b == 0x00:
            self._buf[0] = 0x00
            self._pos = 1
            return None

        # If we haven't seen SOF yet, ignore bytes
        if self._pos == 0:
            return None

        # Store byte
        self._buf[self._pos] = b
        self._pos += 1

        # Frame complete?
        if self._pos == 8:
            frame = TWFrame.decode(self._buf)
            self._pos = 0
            return frame

        #Not complete frame
        return None

    


class TWFrame:
    """Frame handling for the tinywire protocol"""
    _TABLE = [
        0x00,0x07,0x0E,0x09,0x1C,0x1B,0x12,0x15,0x38,0x3F,0x36,0x31,0x24,
        0x23,0x2A,0x2D,0x70,0x77,0x7E,0x79,0x6C,0x6B,0x62,0x65,0x48,0x4F,
        0x46,0x41,0x54,0x53,0x5A,0x5D,0xE0,0xE7,0xEE,0xE9,0xFC,0xFB,0xF2,
        0xF5,0xD8,0xDF,0xD6,0xD1,0xC4,0xC3,0xCA,0xCD,0x90,0x97,0x9E,0x99,
        0x8C,0x8B,0x82,0x85,0xA8,0xAF,0xA6,0xA1,0xB4,0xB3,0xBA,0xBD,0xC7,
        0xC0,0xC9,0xCE,0xDB,0xDC,0xD5,0xD2,0xFF,0xF8,0xF1,0xF6,0xE3,0xE4,
        0xED,0xEA,0xB7,0xB0,0xB9,0xBE,0xAB,0xAC,0xA5,0xA2,0x8F,0x88,0x81,
        0x86,0x93,0x94,0x9D,0x9A,0x27,0x20,0x29,0x2E,0x3B,0x3C,0x35,0x32,
        0x1F,0x18,0x11,0x16,0x03,0x04,0x0D,0x0A,0x57,0x50,0x59,0x5E,0x4B,
        0x4C,0x45,0x42,0x6F,0x68,0x61,0x66,0x73,0x74,0x7D,0x7A,0x89,0x8E,
        0x87,0x80,0x95,0x92,0x9B,0x9C,0xB1,0xB6,0xBF,0xB8,0xAD,0xAA,0xA3,
        0xA4,0xF9,0xFE,0xF7,0xF0,0xE5,0xE2,0xEB,0xEC,0xC1,0xC6,0xCF,0xC8,
        0xDD,0xDA,0xD3,0xD4,0x69,0x6E,0x67,0x60,0x75,0x72,0x7B,0x7C,0x51,
        0x56,0x5F,0x58,0x4D,0x4A,0x43,0x44,0x19,0x1E,0x17,0x10,0x05,0x02,
        0x0B,0x0C,0x21,0x26,0x2F,0x28,0x3D,0x3A,0x33,0x34,0x4E,0x49,0x40,
        0x47,0x52,0x55,0x5C,0x5B,0x76,0x71,0x78,0x7F,0x6A,0x6D,0x64,0x63,
        0x3E,0x39,0x30,0x37,0x22,0x25,0x2C,0x2B,0x06,0x01,0x08,0x0F,0x1A,
        0x1D,0x14,0x13,0xAE,0xA9,0xA0,0xA7,0xB2,0xB5,0xBC,0xBB,0x96,0x91,
        0x98,0x9F,0x8A,0x8D,0x84,0x83,0xDE,0xD9,0xD0,0xD7,0xC2,0xC5,0xCC,
        0xCB,0xE6,0xE1,0xE8,0xEF,0xFA,0xFD,0xF4,0xF3,
    ]

    
    
    @staticmethod
    def _crc8_update(crc,  b):
        """Update a CRC-8/SMBus value, fixed table for speed"""
        return TWFrame._TABLE[(crc ^ b) & 0xFF]


    @staticmethod
    def encode(frame):
        """
        encode frame (in-place).
        Upper layer guarantees:
            frame[0]    = reserved for SOF
            frame[1..6] = Payload
            frame[7]    = reserved for CRC8
        """
        crcfn = TWFrame._crc8_update

        #start of frame
        frame[0] = SOF
        
        # CRC8 over masked header + payload
        crc = 0
        crc = crcfn(crc, frame[1] & 0xF0)
        crc = crcfn(crc, frame[2])
        crc = crcfn(crc, frame[3])
        crc = crcfn(crc, frame[4])
        crc = crcfn(crc, frame[5])
        crc = crcfn(crc, frame[6])
        frame[7] = crc
        
        #handle zero positions.
        zeropos=0
        for i in range(7,1,-1):
            zeropos += 1
            if frame[i] == 0:
                frame[i] = zeropos
                zeropos = 0
            
        #Header zero-pos
        frame[1] |= zeropos+1;

        return frame


    def decode(frame):
        """Decode framed (in-place)"""
        if len(frame) != 8:
            return None
            
        if frame[0] != SOF:
            return None

        crcfn = TWFrame._crc8_update
        
        #Decode zeros
        zeropos = frame[1] & 0x0F
        for i in range(2,7):
            zeropos -= 1
            if zeropos == 0:
                zeropos = frame[i]
                frame[i] = 0
                
        #Clear zero-pointer
        frame[1] &= 0xF0
        
        #calculate crc
        crc = 0
        crc = crcfn(crc, frame[1])
        crc = crcfn(crc, frame[2])
        crc = crcfn(crc, frame[3])
        crc = crcfn(crc, frame[4])
        crc = crcfn(crc, frame[5])
        crc = crcfn(crc, frame[6])

        #check CRC is valid
        if frame[7] == crc:
            return frame
            
if __name__ == "__main__":
    
    #Test Frame handling
    raw = bytearray(
    [
        0x00,    #SOF
        
        0x80 + 0x00,
        0x42,
        0x00,
        0x00,
        0x12,
        0x34,
        
        0x00,   #CRC8
    ])
    
    print(f"Raw: {raw.hex(sep=' ')}")
    frame = TWFrame.encode(raw)
    print(f"Frame: {frame.hex(sep=' ')}")
    
    dec = TWFrame.decode(frame)
    print(f"Decoded: {dec.hex(sep=' ')}")

    pkt_dec  = TWPacket.decode(frame)
    print(pkt_dec)


    packet1 = TWPacket.create_write_request(0x55, 0x1234, 0x0000, ack=False)
    packet2 = TWPacket.create_write_request(0x55, 0x1234, 0x0000, ack=True)
    packet3 = TWPacket.create_read_request(0x55, 0x1234, 0x0000)
    
    print(packet1)
    print(packet2)
    print(packet3)