from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
import  time 

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

#print (" x ",adc)
#value = adc.read(0, 0)
#print(value)


#LCD
lcd = I2cLcd(i2c, 0x27, 4, 20)
# Clear display
lcd.clear()

# Display text on different lines
lcd.move_to(0, 0)  # Column 0, Row 0
lcd.putstr("KD8CGH PWR/SWR")
time.sleep(1)
lcd.clear()

count=0
maxc=10
vfa=0.0
vfp=0.0
vra=0.0
vrp=0.0
vswr=0.0

while True:
    readingf = analog_valuef.read_u16()
    vf = max(readingf * cfactor, 0.0)
    
    readingr = analog_valuer.read_u16()
    vr = max(readingr * cfactor, 0.0)
    
    vfa = vfa + vf
    vfp = max(vfp, vf)
    
    vra = vra + vr
    vrp = max(vrp, vr)
    
    count = count+1
    
    if count == maxc-1:
        vfa=vfa/maxc
        vra = vra/maxc
        wfa=max(4.5306*vfa*vfa+2.5*vfa-.0857, 0.0)
        wra=max(4.29*vra*vra+3.277*vra-.0502, 0.0)
        if wfa > .1 :
            vswr = (vfa+vra)/(vfa-vra)
        else:
            vswr = 1.0
            
        print("average", f"{wfa:.2f}", "  ", f"{wra:.2f}", "  ",f"{vswr:.2f}")
        
        wfp=max(4.5306*vfp*vfp+2.5*vfp-.0857, 0.0)
        wrp=max(4.29*vrp*vrp+3.277*vrp-.0502, 0.0)      
        print("peak", f"{wfp:.2f}", "  ", f"{wrp:.2f}")
        
        lcd.clear()
        lcd.move_to(0, 0)  # Row 0
        lcd.putstr("AV FW %.1f"% wfa)
        lcd.putstr(" RV %.1f"% wra)
        lcd.move_to(0, 1)  # Row 1
        lcd.putstr("PK FW %.1f"% wfp)
        lcd.putstr(" RV %.1f"% wrp)
        lcd.move_to(0, 2)  # Row 2
        lcd.putstr("vswr %.1f:1"% vswr)

        
        wfa=0.0
        wra=0.0
        vfa = 0.0
        vra = 0.0
        vfp = 0.0
        vrp = 0.0
        vswr = 0.0
        count=0
    time.sleep(0.1)

