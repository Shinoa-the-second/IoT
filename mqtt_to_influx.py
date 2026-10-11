import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "fUJYXngtBwre2U9xWKeGMUIPZ4sYM3si2VisYpiwGDONmOio6gr5m1cTS9QUsM9a2MSFfYyvQo74J9ADRccG9A==" 
INFLUX_ORG = "Organization"                         
INFLUX_BUCKET = "Bucket"               

db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "ptit/iot/B23DCCN235/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Đã kết nối MQTT. Đang lắng nghe dữ liệu...")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Kết nối MQTT thất bại (Mã lỗi {rc})")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        temp = data.get('temperature')
        hum = data.get('humidity')
        dist = data.get('distance_cm')
        
        if temp is not None and hum is not None and dist is not None:
            point = (
                Point("sensor_environment") 
                .tag("device_id", "ESP32_B23DCCN235") 
                .field("temperature", float(temp))
                .field("humidity", float(hum))
                .field("distance_cm", float(dist))
            )
            
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"Đã ghi vào DB: Temp={temp}°C, Hum={hum}%, Dist={dist}cm")

    except json.JSONDecodeError:
        print("Lỗi: Gói tin không phải JSON hợp lệ.")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("Đang khởi động hệ thống thu thập dữ liệu...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()