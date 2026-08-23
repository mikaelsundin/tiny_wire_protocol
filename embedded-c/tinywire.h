#ifndef TINYWIRE_H
#define TINYWIRE_H

#include <stdint.h>
#include <stdbool.h>

#define TW_SOF          (0x00u)
#define TW_FRAME_SIZE   (8u)

/* ============================================================
   Standard error codes, Use >= 0x0100 for custom codes.
   ============================================================ */
#define TW_ERR_NONE             (0x0000u)
#define TW_ERR_INVALID_REGISTER (0x0001u)
#define TW_ERR_WRITE_PROTECTED  (0x0002u)
#define TW_ERR_OUT_OF_RANGE     (0x0003u)
#define TW_ERR_BUSY             (0x0004u)
#define TW_ERR_CRC_MISMATCH     (0x0005u)
#define TW_ERR_HW_FAULT         (0x0006u)


//FLAGS
#define TW_FLAG_REQUEST       0x01
#define TW_FLAG_RESPONSE      0x02
#define TW_FLAG_READ          0x04
#define TW_FLAG_WRITE         0x08
#define TW_FLAG_ERROR         0x10
#define TW_FLAG_ACK_REQUIRED  0x20


/* ============================================================
   Layer 3: Packet decoders
   ============================================================ */
   
typedef struct {
    uint8_t  flags;        /* bitmask: request/response/read/write/error/ack */
    uint8_t  node;         /* node ID */
    uint16_t index;        /* register index */
    uint16_t value;        /* payload value (or 0 if error) */
    uint16_t error_code;   /* error code (0 = no error) */
} tw_packet_t;

void tw_packet_decode(tw_packet_t *pkt, const uint8_t *buf);
void tw_packet_encode(uint8_t *buf, const tw_packet_t *pkt);



/* ============================================================
   Layer 3: Packet Creation (write directly into uint8_t* buf)
   ============================================================ */

void tw_create_write_request(uint8_t *buf,
                             uint8_t node,
                             uint16_t index,
                             uint16_t data,
                             bool ack);

void tw_create_read_request(uint8_t *buf,
                            uint8_t node,
                            uint16_t index);

void tw_create_write_response(uint8_t *buf,
                              uint8_t node,
                              uint16_t index,
                              uint16_t data,
                              uint16_t error_code);

void tw_create_read_response(uint8_t *buf,
                             uint8_t node,
                             uint16_t index,
                             uint16_t data,
                             uint16_t error_code);

/* ============================================================
   Layer 2: Frame Encode/Decode, run in-place
   ============================================================ */

void tw_frame_encode(uint8_t *frame);
bool tw_frame_decode(uint8_t *frame);

/* ============================================================
   Stream Receiver (byte-by-byte)
   ============================================================ */

typedef struct {
    uint8_t buf[TW_FRAME_SIZE];
    uint8_t pos;
} tw_stream_rx_t;

void tw_stream_init(tw_stream_rx_t *rx);
void tw_stream_reset(tw_stream_rx_t *rx);

/* Returns true when a full valid frame is decoded into rx->buf */
bool tw_stream_feed(tw_stream_rx_t *rx, uint8_t byte);

#endif /* TINYWIRE_H */
