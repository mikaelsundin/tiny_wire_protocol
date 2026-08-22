# Tiny Wire Protocol
A protocol to read/write 16bit data to registers/memory on multiple nodes over UART.
Inspired from COBS.

Require only total 8 bytes including packet delimitor.


# Specifications
* 8bit Node addressing
* 16bit Address range
* 16bit Data read/write
* Write with ack with possible of error code
* Read with response with possible for error code.
* Fixed size packet size of 8 bytes.
* Extension flag make it possible to extend the protocol in the future.

# Extension
Current no extensions is defined.


# Protocol

---

## Packet start

| Byte | Bits | Description                       |
|------|------|-----------------------------------|
| SOF  | 7…0  | `0x00`                            |

---

## Byte 0 — HEADER
The header is constructed to not use 0x00.

| Bit  | Description                               |
|------|-------------------------------------------|
| 7    | Request(0) / Response(1)                  |
| 6    | REQ: Ack (0=Off,1=On) / RESP: Error flag  |
| 5    | Function (0=Write, 1=Read)                |
| 4    | Extension (0=no extension, 1=extension)   |
| 3..0 | Zero‑pointer/Extension-args               |

Bits 3..0 is set to 0x00 when calculating the CRC-8

Zero-pointer (extension=0):
Points to next zero in message, 
zero-pointer range: 0x01 to 0x0F

Extension (extension=1):
Used for future proof the protocol
Extension-args range: 0x00 to 0x0F

---

## Byte 1 — Node‑ID

| Bits | Description                       |
|------|-----------------------------------|
| 7…0  | Node‑ID bits                      |

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
| 7…0  | CRC8/SMBUS over bytes 0–5         |
