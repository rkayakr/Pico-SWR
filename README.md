# Pico-SWR
MicroPython code for Pi Pico power/SWR meter

Simple RF power and SWR meter using a Pi Pico 2, kits-n-parts bridge and a 20x4 LCD
Be careful to get a display that runs on 3.3 volts
The program main.py normally runs to sample RF and display results. It needs the pico_i2c_lcd.py and lcd_api.py library programs.
A second program is in the repo that bypasses the duisplay to report forward power every one ms for high sampling rate applications. 
Since these are MicrPython programs you can easily change them however you like.

Build notes:
I wound my sampling toroids with 16 turns to lower the voltage to less than 3.3 volts for the Pico ADC for inputs up to 50 watts.
If you are going to put this in a case adjust the bridge pots first.
I calibrated mine using an oscilloscope to neasure the RF voltage and then did a 2nd order polynomial to fit to the measured power vs sampled voltage plot whicl had a fit coeff of .999.
