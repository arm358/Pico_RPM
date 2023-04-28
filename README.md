# Pico_RPM
Reads tachometer signal from an engine using PIO state machines with built-in hour meter written in MicroPython.

### How it works
When first powered on, the display will show the current total hours (left-aligned). After a few seconds, the tachometer will start (right-aligned). When the RPM value is greater than a threshold (implying the engine is on), the engine-on time value (in seconds) saved in the `hours.json` file will increment by 1 every second. 

### Config
* `rpm_divider` should be adjusted specifically to your engine. In my case, the frequency from the tach signal at idle was reading ~120Hz. This would equate to 7200RPM at idle -- way too high. My engine idles between 900-1000 according to the owners manual. Dividing the final RPM value by 8 then produces an RPM of 900 at idle.
* 

### Schematic

![Screenshot from 2023-04-27 20-22-01](https://user-images.githubusercontent.com/76705649/235019060-49054e1f-ad04-4bd8-a86c-fb571c3a071c.png)



