import tellopy

drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(30.0)
protocol = tellopy._internal.protocol


def commandsAPI():
    drone.takeoff()
    time.sleep(2)
    print("Let's make a flip")
    drone.flip_forwardright() 
    sleep(4)
    drone.land()


def commandsPacket():
    pkt = protocol.Packet(0x0054)
    pkt.fixup()
    drone.send_packet(pkt)
    time.sleep(2)
    print("Let's make a flip")
    pkt = protocol.Packet(0x005c, 0x70)
    pkt.add_byte(4)
    pkt.fixup()
    drone.send_packet(pkt)
    time.sleep(4)
    pkt = protocol.Packet(0x0055)
    pkt.add_byte(0x00)
    pkt.fixup()
    drone.send_packet(pkt)


def main():
   print('Commands run by sending packets UDP')
   commandsPacket()
   print('Commands run by API')
   commandsAPI()


if __name__ == '__main__':
    main()
