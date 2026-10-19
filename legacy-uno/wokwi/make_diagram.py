"""Generates diagram.json. Run: python make_diagram.py  (then: wokwi-cli lint diagram.json)"""
import json
P = lambda i,t,l,tp,a=None,r=None: dict(id=i,type=t,top=tp,left=l,attrs=a or {}, **({'rotate':r} if r else {}))
parts = [
 P("bb1","wokwi-breadboard-half",-40,0),
 P("uno","wokwi-arduino-uno",0,300),
 P("led1","wokwi-rgb-led",30,50,{"common":"cathode"}),
 P("r1","wokwi-resistor",75,45,{"value":"220"}),
 P("r2","wokwi-resistor",75,75,{"value":"220"}),
 P("r3","wokwi-resistor",75,105,{"value":"220"}),
 P("btn1","wokwi-pushbutton",20,150,{"color":"green","label":"HOUR","key":"1"}),
 P("btn2","wokwi-pushbutton",110,150,{"color":"blue","label":"MIN","key":"2"}),
 P("btn3","wokwi-pushbutton",200,150,{"color":"red","label":"SNOOZE","key":"3"}),
 P("bz1","wokwi-buzzer",250,60,{"volume":"0.5"}),
 P("tm1","wokwi-tm1637-7segment",400,20,{"color":"red"}),
 P("rtc1","wokwi-ds1307",340,380,{}),
]
c = []
def w(a,b,col,h=None): c.append([a,b,col,h or []])
# power: Uno 5V / GND.2 -> breadboard top rails (tp = + , tn = -)
w("uno:5V","bb1:tp.1","red",["v30","h-60","v-210"])
w("uno:GND.2","bb1:tn.1","black",["v45","h-75","v-225"])
# TM1637 (CLK->D2, DIO->D4, power from rails)
w("tm1:CLK","uno:2","gold",["h-40","v200"])
w("tm1:DIO","uno:4","white",["h-30","v190"])
w("tm1:VCC","bb1:tp.22","red",["h-20"])
w("tm1:GND","bb1:tn.22","black",["h-10"])
# DS1307 stand-in for DS3231 (A4=SDA, A5=SCL)
w("rtc1:SDA","uno:A4","purple",["v20"])
w("rtc1:SCL","uno:A5","cyan",["v30"])
w("rtc1:5V","bb1:tp.25","red",["h30","v-300"])
w("rtc1:GND","bb1:tn.25","black",["h40","v-300"])
# RGB LED: common cathode to GND rail; each colour via 220 ohm to PWM pin
w("led1:COM","bb1:tn.3","black",["v-20"])
w("led1:R","r1:1","orange",[])
w("led1:G","r2:1","green",[])
w("led1:B","r3:1","blue",[])
w("r1:2","uno:5","orange",["h20"])
w("r2:2","uno:6","green",["h30"])
w("r3:2","uno:9","blue",["h40"])
# buttons: one side to pin (INPUT_PULLUP), other side to GND rail
for n,(pin,rail) in enumerate([(10,8),(11,12),(12,16)],1):
    w(f"btn{n}:1.l",f"uno:{pin}","gray",["v10"])
    w(f"btn{n}:2.l",f"bb1:tn.{rail}","black",["v-10"])
# buzzer: pin 1 (neg) to GND rail, pin 2 (pos) to D8
w("bz1:1","bb1:tn.18","black",["v-10"])
w("bz1:2","uno:8","brown",["v10"])
json.dump(dict(version=1,author="UNSW CES workshop",editor="wokwi",parts=parts,connections=c),open("diagram.json","w"),indent=2)
