#include "tinywire.h"
#include "smbus_crc8.h"


/**
 * @brief Decode packet
 */
bool tw_packet_decode(tw_packet_t *pkt, const uint8_t *buf)
{
    uint8_t h = buf[1];

    pkt->flags = 0x00;

    /* Request/response flag */
    if ((h & 0x80) == 0) 
    {
        pkt->flags |= TW_FLAG_REQUEST;
    }
    else 
    {
        pkt->flags |= TW_FLAG_RESPONSE;
    }

    /* read/write function */
    if ((h & 0x20) == 0x20) {
        pkt->flags |= TW_FLAG_READ;
    } 
    else 
    {
        pkt->flags |= TW_FLAG_WRITE;
    }

    /* error */
    if ((h & 0xC0) == 0xC0) 
    {
        pkt->flags |= TW_FLAG_ERROR;
    }

    /* ack required */
    if ((h & 0xC0) == 0x40) 
    {
        pkt->flags |= TW_FLAG_ACK_REQUIRED;
    }
    
    pkt->node  = buf[2];
    pkt->index = ((uint16_t)buf[3] << 8) | buf[4];

    if (pkt->flags & TW_FLAG_ERROR) {
        pkt->error_code = ((uint16_t)buf[5] << 8) | buf[6];
        pkt->value      = 0;
    } else {
        pkt->error_code = 0;
        pkt->value      = ((uint16_t)buf[5] << 8) | buf[6];
    }
    
    return true;
}

/**
 * @brief Encode packet.
 */ 
bool tw_packet_encode(uint8_t *buf, const tw_packet_t *pkt)
{
    /* SOF is set later by tw_frame_encode() */
    uint8_t h = 0;
    
    /* request/response */
    if (pkt->flags & TW_FLAG_REQUEST) 
    {
        h |= 0x00;
    } 
    else 
    {
        h |= 0x80;
    }

    /* read/write request/response */
    if (pkt->flags & TW_FLAG_READ) 
    {
        h |= 0x20;
    } 
    else if (pkt->flags & TW_FLAG_WRITE) 
    {
        h |= 0x00;
    }

    /* error */
    if (pkt->error_code != TW_ERR_NONE) 
    {
        h |= 0x40;
    }
    else if (pkt->flags & (TW_FLAG_ACK_REQUIRED))
    {
        h |= 0x40;
    }

    buf[0] = TW_SOF;
    buf[1] = h;

    /* -----------------------------
       Encode node / index / value
       ----------------------------- */

    buf[2] = pkt->node;
    buf[3] = (pkt->index >> 8) & 0xFF;
    buf[4] = (pkt->index >> 0) & 0xFF;

    if (pkt->error_code != TW_ERR_NONE) 
    {
        buf[5] = (pkt->error_code >> 8) & 0xFF;
        buf[6] = (pkt->error_code >> 0) & 0xFF;
    } 
    else 
    {
        buf[5] = (pkt->value >> 8) & 0xFF;
        buf[6] = (pkt->value >> 0) & 0xFF;
    }

    buf[7] = 0; //CRC is handled on lower layers.
    
    return true;
}


/* ============================================================
   Layer 2: Frame Encode
   ============================================================ */

void tw_frame_encode(uint8_t *frame)
{
    uint8_t crc = SMBUS_CRC8_INIT;

    frame[0] = TW_SOF;
    crc = smbus_crc8_update(crc, frame[1] & 0xF0);
    crc = smbus_crc8_update(crc, frame[2]);
    crc = smbus_crc8_update(crc, frame[3]);
    crc = smbus_crc8_update(crc, frame[4]);
    crc = smbus_crc8_update(crc, frame[5]);
    crc = smbus_crc8_update(crc, frame[6]);
    frame[7] = crc;

    //Handle zeros in buffer.
    uint8_t zp = 0;
    for (int i = 7; i >= 2; i--) {
        zp++;
        if (frame[i] == 0) {
            frame[i] = zp;
            zp = 0;
        }
    }

    //update zero-pointer in header.
    frame[1] |= (zp + 1);
}

/* ============================================================
   Layer 2: Frame Decode
   ============================================================ */

bool tw_frame_decode(uint8_t *frame)
{
    if (frame[0] != TW_SOF) {
        return false;
    }

    //Handle zero-pointer
    uint8_t zp = frame[1] & 0x0F;
    for (int i = 2; i <= 6; i++) {
        zp--;
        if (zp == 0) {
            zp = frame[i];
            frame[i] = 0;
        }
    }

    //Clear zero-pointer
    frame[1] &= 0xF0;

    uint8_t crc = SMBUS_CRC8_INIT;
    crc = smbus_crc8_update(crc, frame[1]);
    crc = smbus_crc8_update(crc, frame[2]);
    crc = smbus_crc8_update(crc, frame[3]);
    crc = smbus_crc8_update(crc, frame[4]);
    crc = smbus_crc8_update(crc, frame[5]);
    crc = smbus_crc8_update(crc, frame[6]);

    //Check CRC8
    return (crc == frame[7]);
}

/* ============================================================
   Stream Receiver (byte-by-byte)
   ============================================================ */

void tw_stream_init(tw_stream_rx_t *rx) {
    rx->pos = 0;
}

void tw_stream_reset(tw_stream_rx_t *rx) {
    rx->pos = 0;
}

/**
 * @brief Handle byte by byte,
 * @return True when a frame is received.
 */
bool tw_stream_feed(tw_stream_rx_t *rx, uint8_t byte)
{
    if (byte == TW_SOF) {
        //Start of frame received
        rx->buf[0] = TW_SOF;
        rx->pos = 1;
        return false;
    }else if (rx->pos == 0) {
        //No start of frame received.
        return false;
    }

    rx->buf[rx->pos++] = byte;

    //Check if full frame is received + decode the frame.
    if (rx->pos == TW_FRAME_SIZE) {
        rx->pos = 0;
        return (tw_frame_decode(rx->buf));
    }

    //No enough data is received.
    return false;
}
