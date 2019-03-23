import can

bus=can.Bus(interface='socketcan', channel='can0')

for msg in bus:
    print(msg.arbitration_id, msg.data)

#notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])
