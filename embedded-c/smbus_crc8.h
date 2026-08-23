#ifndef SMBUS_CRC8
#define SMBUS_CRC8

#include <stdint.h>

//Setting: Use CRC8 Precalculated Tabel (0=on, 1=off)
//Speeds up calculation, but take more flash.
#define SMBUS_CRC8_USE_TABLE (1)

//CRC8 SMBus start value.
#define SMBUS_CRC8_INIT (0x00u)

/**
 * @brief Calculate one byte of CRC8/SMBUS
 */
uint8_t smbus_crc8_update(uint8_t crc, uint8_t data);

#endif

