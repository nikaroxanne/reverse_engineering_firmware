import sys
import pyBusPirateLite.SPI



### Instruction codes from Winbond datasheet
### WREN = Write Enable
### WRDI = Write Disable
### WRITE = Write, technically "Page Program" in the Winbond datasheet
### RDSR = Read Status Register
### WRSR = Write Status Register

WREN = 6
WRDI = 4
READ = 3
WRITE = 2
RDSR = 5
WRSR = 1


addresses = [0xc, 0xbce]

##patch_data = [[0b, 1b] ,[00,21,49,f2,49,f8,00,21,9f,a0,49,f2,45,f8,9e,48]]


###############################################################################
# References:
#
#  “Into to Hardware Hacking - DEF CON 27 Conference”
#  Philippe Laulheret
#  https://www.youtube.com/watch?v=HuCbr2588-w
#
#
# Winbond Datasheet:
# https://www.winbond.com/resource-files/w25x40cl_f%2020140325.pdf
# 
#
# Wrongbaud
# "BasicFUN-flashing"
# https://wrongbaud.github.io/BasicFUN-flashing/
#
# IBM Support Knowledge Center
# https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3.cbclx01/bitshe.htm
#
# Stack Overflow
# "What does AND 0xff do?"
# https://stackoverflow.com/questions/14713102/what-does-and-0xff-do
#
#
# PyBusPirateLite Documentation:
# https://pybuspiratelite.readthedocs.io/en/latest/_modules/pyBusPirateLite/SPI.html
#
# "SPI Interfacing experiments"
# R. X. Seger
# Medium
# https://medium.com/@rxseger/spi-interfacing-experiments-eeproms-bus-pirate-adc-opt101-with-raspberry-pi-9c819511efea
# 
# Stack OverFlow
# "How Do I Write to SPI Flash Memory?"
# https://electronics.stackexchange.com/questions/51229/how-do-i-write-to-spi-flash-memory
# 
# 
# River Loop Security
# "Hardware Hacking 101: Interfacing with SPI"
# https://www.riverloopsecurity.com/blog/2020/02/hw-101-spi/
# 
# 
# River Loop Security
# "Hardware Hacking 101: Identifying and Dumping eMMC Flash"
# https://www.riverloopsecurity.com/blog/2020/03/hw-101-emmc/
# 
# River Loop Security
# "Hardware Hacking 101: Getting a Root Shell via UART"
# https://www.riverloopsecurity.com/blog/2020/01/hw-101-uart/
# 
# 
# River Loop Security
# "Hardware Hacking 101: Glitching into Privileged Shells"
# https://www.riverloopsecurity.com/blog/2020/10/hw-101-glitching/
# 
# 
#
###############################################################################
## Notes on Winbond chip
##
##
## CS is active low (have to bring CS low to read/write to chip)
## WP is active low (have to bring WP low in order to write to chip)
##
##
###############################################################################






def read_flash(spi, address_data):
	##Have to bring CS pin low before transfer operation
	spi.cs = True
	adr_24_bit = address_data >> 8
	adr_zero_mask = address_data && 0xff
	data = spi.transfer([READ, adr_24_bit, adr_zero_mask, 0])
	##Have to bring CS pin high after last byte of transfer operation sent in order for transfer to work
	spi.cs = False
	return data



## Use Page Program instruction (from Winbond datasheet) to write to flash
## Page program will write between 1-256 bytes of data (256 bytes = 1 page)
## Note that if the last address byte is not 0, and if the number of clock cycles exceeds the remaining page length
## then the page program instruction will wrap around, and start writing data at the start address of the page
##
## Page Program format:
## 0x02 followed by 24-bit address, followed by data bytes of data to be transferred (written) to flash
## Address must be shifted right by 8, to align with 24-bit specification;
## Address must then be AND'ed with 0xff mask 
##


def write_flash(spi, address_data, patch_data):
	spi.cs = True
	##Have to bring CS pin low before transfer operation
	address_shifted_to_24_bit = address_data >> 8

	## Uses 0xff as mask to set the last byte of the address to be 0, 
	## in order to satisfy requirements as per Winbond datasheet

	address_last_byte_masked_to_zero = address_data && 0xff

	data = spi.transfer([WRITE, address_shifted_to_24_bit, address_last_byte_masked_to_zero, patch_data])

	##Have to bring CS pin high after last byte of transfer operation sent in order for transfer to work
	spi.cs = False



if __name__ == '__main__':
	spi = SPI()
	spi.pins = PIN_POWER | PIN_CS
	spi.config = CFG_PUSH_PULL | CFG_IDLE
	spi.speed = '1Mhz'

	for i, elem in enumerate(addresses):
		write_flash(spi, elem, patch_data[i])
		time.sleep(1)
		new_data = read_flash(spi, elem)
		if new_data == patch_data[i]:
			print("Correctly patched data at address: %d with value: %s \n", elem, f"0x{patch_data[i]:0x2x}")
		else:
			break


