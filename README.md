# ArduController

ArduController is a GUI that allows you to tune a PID controller running on an Arduino. The GUI is written using Tkinter and Matplotlib for graphing, and communicates with the Arduino with pyserial. The Arduino is running custom firmware that reads messages from a computer (in my case a Jetson Nano) that can tune the PID controller and update its setpoint. The message passing software and PID controller are all hand written, although I do use a library for reading QuadratureEncoder counts.

Video Presentation: https://youtu.be/eopoMrKM5vc

## Functionality
![Main GUI](https://github.com/user-attachments/assets/802da3bd-2128-4fd6-94bc-eaf567802bb8)

The GUI contains two graphs, a column of labeled entry fields, and a row of buttons.

The graphs are implemented in Matplotlib, and allow for live, continuous plotting of the last 10 seconds of the motors position. Data is collected from the Arduino asynchronously in a separate thread to allow for a smooth graph without adding too much latency. One graph shows encoder position and setpoint, and the other shows error (the difference between position and setpoint). The graph that shows error automatically adjusts its bounds with the minimum and maximum values of the data, but the graph that shows absolute position won’t shrink its bounds by default to allow a more stable sense of the motor’s trajectory. There is a button labeled “Reset view” that readjusts this graph's bounds.

The entry fields are validated to only take acceptable inputs, which is either an integer between -255 and 255 or a float depending on the field. There are 8 parameters that describe the PID controller:

- KP (float): proportional gain
- KI (float): integral gain
- KD (float): derivative gain
- Min (int): minimum PID output
- Max (int): maximum PID output
- Cutoff (float): the PID output that is considered zero
- Int region (int): the region of integration
- Int max (float): the maximum value of the integrator

Once set as desired, these can be sent to the Arduino using the button “Send PID”. The Arduino runs the PID controller itself using my own implementation.

When you’re ready to move the motor, there are two buttons to do so. One is “Direct set”, which bypasses the PID controller and directly sends the analog signal in the “Analog signal” entry to the motor controller. The other is “Setpoint,” which updates the setpoint of the PID controller and enters it into PID mode.

![setpoint](https://github.com/user-attachments/assets/2fb064d0-e649-4771-a459-f97e224dd9b4)

There are “Load” and “Save” buttons that allow you to save and load JSON config files containing PID parameters. They’re guarded against non-JSON files, permission errors, and non-existing files, and report these errors without crashing the program. They use Tkinter’s default file dialog functions to allow a user to navigate to the desired file, but by default open in a dedicated “config” folder.

![invalid JSON](https://github.com/user-attachments/assets/d37b2945-d9a8-41bc-8ca5-cb76cd82bb4f)
![load screen](https://github.com/user-attachments/assets/1c1cc26d-85ef-488f-aec1-5f0804f83bec)
![successful load](https://github.com/user-attachments/assets/e8334f47-f54f-4343-8e48-8779952b509a)

Communication between the Arduino and Jetson is done using serial communication. The Arduino generates a message (a sequence of bytes, where the first byte is a command and the following bytes are data) and uses COBS encoding to turn it into a data packet and send it to the Arduino over pyserial. It’s then read by the Arduino and decoded, and the Arduino COBS encodes its reply and sends it back.

The most difficult parts of the project were communicating with the Arduino and graphing live data in Matplotlib. Serial communication is the primary method of debugging Arduino programs, so when it’s already in use it’s very inconvenient to probe the state of the Arduino program. Small mistakes are very difficult to locate, and being off by a single byte is often a subtle enough issue that it can go unnoticed. Matplotlib is simply not well suited to animation, and I found the documentation difficult to navigate. Even something as simple as resizing the axis dynamically was quite a challenge.
