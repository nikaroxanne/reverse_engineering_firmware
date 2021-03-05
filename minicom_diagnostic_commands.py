#!/usr/bin/python

import sys
import re
import os

#******************************************************************************
#                                                                             
# Python script to automate the creation of batch files to be supplied as input 
# to minicom serial console session
# 
# Takes two values of user input for the start and end of the address range
# from which to dump memory; uses this to calculate the total number of blocks
# of memory requested
#
# The address range and number of blocks are used to construct the appropriate
# number of strings to the output batch file
#
#
##*****************************************************************************
#
# mini_address_vals takes two parameters:
# 1. input_adr -- the start address of the address range requested by user
# 2. num_blocks -- number of blocks of memory to request, equivalent to the
# number of strings with the "D" command to be concatenated to the output 
# batch file
#
#
# Returns a list of strings, each element of which is a command to be sent
# to the diagnostic menu of the Seagate drive through the serial console
# which requests a block (512B) of memory to be dumped to the serial console
#
##***************************************************************************** 

def mini_address_vals(input_adr, num_blocks):
    new_commands = []
    start_adr = input_adr

    for i in range(num_blocks):
        adr_val = (512 * i) + start_adr
        new_adr = "{0:X}".format(adr_val)
        command_val="D" + new_adr
        new_break = r'        ! echo "{x}"'.format(x=command_val)
        new_commands.append(new_break)
	cmd_expect =r"""        expect {
                "Processor memory"
	        timeout 2 break
        }"""
        new_commands.append(cmd_expect)
        sleep_cmd = r"        sleep 2"
        new_commands.append(sleep_cmd)
    return new_commands

if __name__ =='__main__':
    input_adr = int(input())
    input_range_end = int(input())
    input_range_total= input_range_end - input_adr

    print("input range in dec: {0:d}".format(input_range_total))
    print("input range in hex: {0:x}".format(input_range_total))
    
    num_blocks = input_range_total / 512
    print("num blocks in dec: {0:d}".format(num_blocks))


    output_file="minicom_diag_commands_"+str(hex(input_adr))+".txt"
    fptr = open(output_file, "w")
  

    verbose_cmd="verbose on"
    fptr.write('\t'+verbose_cmd + '\n')

    timeout_val = (num_blocks * 4) + 10
    print("timeout_val is:", timeout_val)

    cmd_timeout="timeout {} \n\n".format(timeout_val)	
    print("cmd_timeout is:", cmd_timeout)

    fptr.write('\t'+cmd_timeout + '\n')
    
    diag_menu_string_1 = "send \^Z"
    fptr.write('\t'+diag_menu_string_1 + '\n')
    sleep_initial="sleep 5"
    fptr.write('\t'+sleep_initial+ '\n')
    diag_menu_string_2 = "send \\1"
    fptr.write('\t'+diag_menu_string_2 + '\n')
    
    cmd_goto_v1="goto v1\n\n"
    fptr.write('\t'+cmd_goto_v1)
    cmd_v1_label="v1:\n\n"
    fptr.write(cmd_v1_label)


    command_list=mini_address_vals(input_adr, num_blocks)

    for res in command_list:
        fptr.write(str(res) + '\n')
   
    last_call="exit"
    fptr.write('\t'+last_call)
    
    fptr.close()

