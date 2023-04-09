from machine import Pin
import _thread
import rp2
import utime
from lib.tm1637 import TM1637Decimal
import ujson

#signal input pin
GPIO_INPUT_PIN = 22

#display pins
GPIO_SEG_CLK = 27
GPIO_SEG_DIO = 26

#global to hold rpm
global rpm
rpm = 0
rpm_divider = 8

#initialize the display
tm = TM1637Decimal(clk=Pin(GPIO_SEG_CLK), dio=Pin(GPIO_SEG_DIO))

def startup():
    tm.scroll("hello", delay=250)
    with open("./hours.json") as hours:
        data = ujson.loads(hours.read())
        hours = str(round(data["seconds"] / 3600,1))
        tm.show(hours)
        utime.sleep(2)


#create PIOASM program to count clock cyles between rising edges
@rp2.asm_pio()
def read_pwm():
    set(x,0)            # set scratch register to 0;
    wait(0, pin, 0)     # Do {} While ( pin == 1 ); start off by knowing we're at a low
    wait(1, pin, 0)     # Do {} While ( pin == 0 ); wait until it goes high, confirming leading edge has happened

    label("highloop")      #   <--.
    jmp(x_dec, "highnext") # 1    | x-- if x non-zero --.
    label("highnext")      #      |                  <--- 
    jmp(pin, "highloop")   # 2 ---' if pin still high, loop again
    
    label("lowloop")       #   <--. else pin is confirmed low
    jmp(pin, "done")       # 1    | if pin back to high, jump to done label, 
    jmp(x_dec, "lowloop")  # 2 ---' else x-- if x non-zero

    label("done")
    mov(isr, x)            # move the value of x to the isr
    push(isr, block)       # push the isr to the TX FIFO if not full


def update_hours():
    with open("./hours.json", "r") as json:
        data = ujson.loads(json.read())
        data["seconds"] += 1
    with open("./hours.json", "w") as json:
        updated_data = ujson.dumps(data)
        json.write(updated_data)


def core1_routine():
    """
    constantly read the TX FIFO of statemachine
    convert the clock cycles to time
    calculate rpm and update global rpm value
    """
    global rpm
    while True:
        val = sm0.get()
        cnt = ((1 << 32) - val)
        tms = cnt / 62500 #calculates total miliseconds the count of clocks took
        rps = 1000 / tms
        rpm = round(rps*60) / rpm_divider
        
def loop():
    """
    update display with rpm value every second
    """
    while True:
        tm.number(rpm)
        if rpm > 0:
            update_hours()
        utime.sleep_ms(1000)


if __name__ == "__main__":
    #build and activate the statemachine running the PIOASM program
    sm0 = rp2.StateMachine(0, read_pwm, freq = 125_000_000, in_base=Pin(GPIO_INPUT_PIN, Pin.IN), jmp_pin=Pin(GPIO_INPUT_PIN))
    sm0.active(1)

    #start thread on core1
    core1 = _thread.start_new_thread(core1_routine,())

    #show welcome message and total hours
    startup()
    
    #start main loop on core0
    loop()



