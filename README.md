# Tiny Wire Protocol
A protocol to read/write 16bit data to registers on multiple nodes over UART.
Inspired from COBS.

# Specifications
* 10bit Node addressing
* 16bit Address range
* 16bit Data
* Write with ack with possible of error code
* Read with response and possible for error code.
* Fixed size packet size of 8 bytes.
* Extension flag make it possible to extend the protocol in the future.
