#Connections
#Bridge FWD to point to ADC0 GP26
#              R 10k
#Bridge Gnd to GNDPt to AGND  GP27
#              R 10k
#Bridge RVS to point to ADC1 GP27
#  
#Display 
#GND to GND 
#VCC to 3Vs(out)
#SDA to I2C1 SDA GP2
#SCL to I2C1 SCL GP3 
from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
import  time 
from time import ticks_ms, sleep, ticks_diff
# Define the LCD I2C address and dimensions
I2C_ADDR = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20

# Initialize I2C and LCD objects
i2c = SoftI2C(sda=Pin(2), scl=Pin(3), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

analog_valuef = machine.ADC(26)
analog_valuer = machine.ADC(27)
cfactor = 3.3/(65535)

count=0
icount=0
maxc=15
vfa=0.0
vfp=0.0
start_ticks = ticks_ms()  # Record the start ticks
while (analog_valuef.read_u16() < 400):
    time.sleep_ms(2)
duration_ms = ticks_diff(ticks_ms(), start_ticks)
#print("time: {} ".format(duration_ms/100))
print(" ") 

start_ticks = ticks_ms()  # Record the start ticks
for count in range(1, 500):
    for icount in range(1, maxc):
        readingf = analog_valuef.read_u16()
#        print(" d ", readingf)
        vf = max(readingf * cfactor, 0.0)    
        vfa = vfa + vf
#        vfp = max(vfp, vf)   
    vfa=vfa/maxc
    wfa=max(4.5306*vfa*vfa+2.5*vfa-.0857, 0.0)
#    wfp=max(4.5306*vfp*vfp+2.5*vfp-.0857, 0.0)    
    icount=0
    duration_ms = ticks_diff(ticks_ms(), start_ticks)
#    print("time: {} ".format(duration_ms/100) ,"average", f"{wfa:.2f}","peak", f"{wfp:.2f}")
    print(" {}".format(duration_ms) ,",", f"{wfa:.2f}")
#    vfp=0
    time.sleep_ms(4)
end_ticks = ticks_ms()    # Record the end ticks
duration_ms = ticks_diff(end_ticks, start_ticks)  # Calculate the duration in milliseconds
#print("dt: {} ".format(duration_ms),f"{wfa:.2f}")
#print("average", f"{wfa:.2f}","peak", f"{wfp:.2f}")

