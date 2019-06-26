import tellopy

drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(30.0)
protocol = tellopy._internal.protocol

def commands():
    pkt = protocol.Packet(0x0054)
    pkt.fixup()
    drone.send_packet(pkt)
    # drone.takeoff()

    time.sleep(2)
    print("2 secs")


    pkt = protocol.Packet(0x005c, 0x70)
    pkt.add_byte(4)
    pkt.fixup()
    drone.send_packet(pkt)


    time.sleep(4)
    print("4 secs")

    pkt = protocol.Packet(0x0055)
    pkt.add_byte(0x00)
    pkt.fixup()
    drone.send_packet(pkt)


def main():
   commands()


if __name__ == '__main__':
    main()
