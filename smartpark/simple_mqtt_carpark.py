from datetime import datetime
from paho.mqtt.client import MQTTMessage
import mqtt_device
from config_parser import parse_config

CONFIG_FILE = "Configs.json"

class CarPark(mqtt_device.MqttDevice):
    """Creates a carpark object to store the state of cars in the lot"""

    def __init__(self, config):
        super().__init__(config)
        self.total_spaces = int(config['total-spaces'])
        self.total_cars = int(config['total-cars'])
        self.client.on_message = self.on_message
        self.client.subscribe('sensor')
        self._temperature = None
        self.client.loop_forever()

    @property
    def available_spaces(self):
        available = min(self.total_spaces - self.total_cars,self.total_spaces)
        return max(available, 0)

    @property
    def temperature(self):
        self._temperature
    
    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        
    def _publish_event(self):
        readable_time = datetime.now().strftime('%H:%M')
        print(
            (
                f"TIME: {readable_time}, "
                + f"SPACES: {self.available_spaces}, "
                + f"TEMP: {self._temperature} ℃"
            )
        )
        message = (
            f"TIME: {readable_time}, "
            + f"SPACES: {self.available_spaces}, "
            + f"TEMP: {self._temperature} ℃"
        )
        self.client.publish('display', message)

    def on_car_entry(self):
        self.total_cars += 1
        self._publish_event()



    def on_car_exit(self):
        self.total_cars = max(self.total_cars - 1,0)
        self._publish_event()

    def on_message(self, client, userdata, msg: MQTTMessage):
        payload = msg.payload.decode().split(',')

        print(msg.payload.decode())

        temp = payload[1].rstrip(" ")
        self.temperature = temp
        if 'exit' in payload[0]:
            self.on_car_exit()
        else:
            self.on_car_entry()


if __name__ == '__main__':
    car_park = CarPark(parse_config(CONFIG_FILE)["Carpark"])
    print("Carpark initialized")

