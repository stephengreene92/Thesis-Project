#code for reading in information from shaft encoder to
#calculate omega and theta


from mcculw import ul
from mcculw.enmus import DigitalIODirection, DigitalPortType
from examples.console import util
import time
import matplotlib.pyplot as plt
import numpy as np

Total_Sample_Size = 700
board_num = 0
BitLow = 0
BitHigh = 1
loop_counter = 0
High_Byte = 0
Low_Byte = 0
Theta_i = 0.0

f = open("results.txt", "w+")

#create 3 arrays so data can be saved/exported if needed
time_array = np.zeros(Total_Sample_Size)
Omega_array = np.zeros(Total_Sample_Size)
Theta_f_array = np.zeros(Total_Sample_Size)
Theta_r_array = np.zeros(Total_Sample_Size)

use_device_detection = True

if use_device_detection:
    ul.ignore_instacal()
    if not util.config_first_detected_device(board_num):
        print("Could not find device.")
        
plt.ion()

#configure PORT A as an output port and PORT B as an input port
ul.d_config_port(board_num, DigitalPortType.FIRSTPORTA, DigitalIODirection.OUT)
ul.d_config_port(board_num, DigitalPortType.FIRSTPORTB, DigitalIODirection.IN)

#Set Output Enable(EO) and Select(SEL) in PORT A HIGH to initalise
ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,0,BitHigh)#EO
ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,1,BitHigh)#SEL

#two different variables needed as one of them is updated in the loop
#and one is needed to remain constant
start_program_time = start_loop_time = time.time()

#f.write("Time(s)\t\tTheta_0(rad)\t\t\tOmega(rads/s)\n")

while loop_counter < Total_Sample_Size:
    
    #Set Output Enable (EO) and Select(SEL) in PORT A LOW so the HIGH Byte can be read
    ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,0,BitHigh)#EO
    ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,1,BitHigh)#SEL
    
    #save the previous high byte, used later in calculations
    Previous_High_Byte = High_Byte
    
    #Read the first byte in PORT B
    #front of binary numbers so it is easier to add them later
    High_Byte = ul.d_in(board_num, DigitalPortType.FIRSTPORTB)
    
    #Set the SEL line HIGH to read the LOW Byte
    ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,1,BitHigh)
    
    #Read the second Byte in PORT B
    Low_Byte = ul.d_in(board_num, DigitalPortType.FIRSTPORTB)
    
    #Set EO and SEL HIGH again
    ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,0,BitHigh)#EO
    ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA,1,BitHigh)#SEL
    
    #concatenate the two binary values
    Full_Byte = (High_Byte<<8) | Low_Byte
    
    if (loop_counter == 0):
        n = 0
    if (Previous_High_Byte-High_Byte >= 9):
        n += 1
    if (High_Byte-Previous_High_Byte >= 9):
        n -= 1
        
    Theta_f = ( (Full_Byte + (4096*n))*0.036)
    Theta_r = np.radians(Theta_f)
    if(loop_counter ==0):
        Theta_i = Theta_f
        
    d_Theta = np.radians(Theta_f-Theta_i)
    current_time = time.time()
    d_t = (current_time-start_loop_time)
    Omega =(d_Theta/d_t)
    Theta_i = Theta_f
    start_loop_time = current_time
    time_since_start = (time.time() - start_program_time)
    
    time_array[loop_counter] = time_since_start
    Omega_array[loop_counter] = Omega
    Theta_f_array[loop_counter] = Theta_f
    Theta_r_array[loop_counter] = Theta_r
    
    f.write('%s\t%s\t\t%s\n'%(time_array[loop_counter],
                                Theta_r_array[loop_counter]
                                ,Omega_array[loop_counter]))
                                
    #comment out real time graph for better resolution
    """
    plt.subplot(2,1,1)
    plt.scatter(time_since_start, Theta_r, c='k', alpha = 0.5, linewidths=0)
    plt.ylabel('Theta_r')
    plt.xlabel('time(s)')
    #plt.ylim(-1000,1000)
    plt.subplot(2,1,2)
    plt.scatter(time_since_start, Omega, c='g', alpha = 0.5, linewidths=0)
    plt.xlabel('time(s)')
    plt.ylabel('Omega')
    #plt.ylim(-2.5,2.5)
    plt.pause(0.001)
    plt.show()
    """
    #end commen-out section
    
    loop_counter+=1
    
f.close()
plt.subplot(2,1,1)
plt.plot(time_array,Theta_r_array,'k',label='Theta (Radians)')
plt.grid()
plt.legend()
plt.subplot(2,1,2)
plt.plot(time_array,Omega_array,'b',label='Omega')
plt.grid()
plt.legend()