import tellopy
from time import sleep

drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(30.0)
protocol = tellopy._internal.protocol


def commandsAPI():
    drone.takeoff()
    sleep(2)
    # UNCOMMENT THESE LINES IF THE DRONE IS FULLY CHARGED 
    print("Let's make a flip")
    drone.flip_forwardright() 
    sleep(4)
    drone.land()
    sleep(2)
    drone.quit()

def commandsPacket():
    pkt = protocol.Packet(0x0054)
    pkt.fixup()
    drone.send_packet(pkt)
    sleep(2)
    
    # UNCOMMENT THESE LINES IF THE DRONE IS FULLY CHARGED 
    print("Let's make a flip")
    pkt = protocol.Packet(0x005c, 0x70)
    pkt.add_byte(4)
    pkt.fixup()
    drone.send_packet(pkt)
    sleep(4)
    pkt = protocol.Packet(0x0055)
    pkt.add_byte(0x00)
    pkt.fixup()
    drone.send_packet(pkt)
    sleep(2)
    drone.quit()

def main():
   print('Commands run by sending packets UDP')
   commandsPacket()
   print('Commands run by API')
   commandsAPI()


if __name__ == '__main__':
    main()
