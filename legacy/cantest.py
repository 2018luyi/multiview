import can

bus=can.Bus(interface='socketcan', channel='can0')

for msg in bus:
    print(msg.arbitration_id, msg.data)

#print(bus.msg.arbitration_id, bus.msg.data)

#notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])
