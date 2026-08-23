# TinyWire Protocol — Clean Layer 2 + Layer 3 APIs
# Pure Python / MicroPython compatible

SOF = 0x00

class TWPacket:
    def __init__(self):
        self.is_response = False
        self.ack_or_error = False
        self.is_read = False
        self.node_id = 0
        self.address = 0
        self.data = 0


# -------------------------------------------------------------
# CRC-8/SMBus
# -------------------------------------------------------------
def crc8_update(crc,  b):
    crc ^= b
    for _ in range(8):
        crc = ((crc << 1) & 0xFF) ^ 0x07 if (crc & 0x80) else ((crc << 1) & 0xFF)
    return crc




# =============================================================
# LAYER 2 — TRANSPORT / FRAMING
# =============================================================

def tw_frame_encode(frame):
    """
    Layer 2 encoder (in-place).
    Upper layer guarantees:
        frame[0]    = reserved for SOF
        frame[1..6] = Payload
        frame[7]    = reserved for CRC8
    """

    #start of frame
    frame[0] = SOF
    
    # CRC8 over masked header + payload
    crc = 0
    crc = crc8_update(crc, frame[1] & 0xF0)
    crc = crc8_update(crc, frame[2])
    crc = crc8_update(crc, frame[3])
    crc = crc8_update(crc, frame[4])
    crc = crc8_update(crc, frame[5])
    crc = crc8_update(crc, frame[6])
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


def tw_frame_decode(frame):
    """Decode framed TinyWire packet into restored payload."""
    if len(frame) != 8:
        return None
        
    if frame[0] != SOF:
        return None


        
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
    crc = crc8_update(crc, frame[1])
    crc = crc8_update(crc, frame[2])
    crc = crc8_update(crc, frame[3])
    crc = crc8_update(crc, frame[4])
    crc = crc8_update(crc, frame[5])
    crc = crc8_update(crc, frame[6])

    #check CRC is valid
    if frame[7] == crc:
        return frame
        
if __name__ == "__main__":
    
    #Test Layer2
    raw = bytearray(
    [
        0x00,    #SOF
        
        0x80,
        0x42,
        0x00,
        0x00,
        0x00,
        0x00,
        
        0x00,   #CRC8
    ])
    
    print(f"Raw: {raw.hex(sep=' ')}")
    frame = tw_frame_encode(raw)
    print(f"Frame: {frame.hex(sep=' ')}")
    
    dec = tw_frame_decode(frame)
    print(f"Decoded: {dec.hex(sep=' ')}")

    