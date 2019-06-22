# Protocol
Information about how the Tello's protocol work. It can be really useful in order to understand how the projects works inside. 

## List of commands
```python
START_OF_PACKET                     = 0xcc
WIFI_MSG                            = 0x001a
VIDEO_ENCODER_RATE_CMD              = 0x0020
VIDEO_START_CMD                     = 0x0025
VIDEO_RATE_QUERY                    = 0x0028
TAKE_PICTURE_COMMAND                = 0x0030
VIDEO_MODE_CMD                      = 0x0031
EXPOSURE_CMD                        = 0x0034
LIGHT_MSG                           = 0x0035
TIME_CMD                            = 0x0046
STICK_CMD                           = 0x0050
TAKEOFF_CMD                         = 0x0054
LAND_CMD                            = 0x0055
FLIGHT_MSG                          = 0x0056
SET_ALT_LIMIT_CMD                   = 0x0058
FLIP_CMD                            = 0x005c
THROW_AND_GO_CMD                    = 0x005d
PALM_LAND_CMD                       = 0x005e
TELLO_CMD_FILE_SIZE                 = 0x0062
TELLO_CMD_FILE_DATA                 = 0x0063
TELLO_CMD_FILE_COMPLETE             = 0x0064
LOG_HEADER_MSG                      = 0x1050
LOG_DATA_MSG                        = 0x1051
LOG_CONFIG_MSG                      = 0x1052
```
## Packet
The packet really varies depending on the command that wants to be send. Mainly there are 3 different packets depending on the content of code:

- If it is a tuple of bytearrays and bytes
```python
code
```
- If it is a string
```python 
[ord(c) for c in code]
```
- Else
```python
bytearray([0xcc,0,0,0,0x68,code & 0xff,(code >> 8) & 0xff, 0,0])
```

## Sending packets
The drone address is **192.168.10.1** and the port depends on what we want to do. The default is **9000**, but for exemple to send a connnection request we have **9617,150 (port0 = (int(port/1000)%10) << 4 | (int(port/100)%10)), 23 (port1 = (int(port/10) % 10) << 4 | (int(port/1) % 10)
),** or 6038 for video stuff. We communicate with the drone by UDP sockets. 

## Things I do need for Yello
- Protocol
- Crc
- Utils
- Videostream

## Misteries by now
- Throw and go, send exposure 0x48?
- Why they need fixup?
- Send time commands, send ack log, 0x50?
- Send start video and move(send stick command) 0x60?
- Flips, 0x70 + byte(type of flip)
- Dafuq is doig fixup?!
- DAFUQ IS DOING CRC?!??!!?
