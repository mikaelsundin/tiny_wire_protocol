# Tiny Wire Protocol
A protocol to read/write 16bit data to registers on multiple nodes over UART.
Inspired from COBS.

# Specifications
* 10bit Node addressing
* 16bit Address range
* 16bit Data
* Write with ack with possible of error code
* Read with response with possible for error code.
* Fixed size packet size of 8 bytes.
* Extension flag make it possible to extend the protocol in the future.

# Protocol


---

## Packet start

| Byte | Bits | Description                       |
|------|------|-----------------------------------|
| SOF  | 7…0  | `0x00`                            |

---

## Byte 0 — HEADER

| Bit  | Description                               |
|------|-------------------------------------------|
| 7    | Request(0) / Response(1)                  |
| 6    | REQ: Ack (0=Off,1=On) / RESP: Error flag  |
| 5    | Function (0=Write, 1=Read)                |
| 4..3 | Node‑ID bit 9,8                           |
| 2..0 | Zero‑pointer                              |

Zero‑pointer range: `0x01`–`0x07`  
Reserved extension pattern: bits 5..0 = `0b11000`

---

## Byte 1 — Node‑ID

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | Node‑ID bits 0..7                 |

---

## Byte 2 — ADR‑HI

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | Register address MSB              |

---

## Byte 3 — ADR‑LO

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | Register address LSB              |

---

## Byte 4 — DATA‑HI (lower 7 bits)

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | DATA MSB (7‑bit) / Error MSB      |

---

## Byte 5 — DATA‑LO (lower 7 bits)

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | DATA LSB (7‑bit) / Error LSB      |

---

## Byte 6 — CRC8/SMBUS

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | CRC8/SMBUS over bytes 0–6         |
