import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "ptit/iot/B23DCCN235/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Đã kết nối MQTT Broker thành công!")
        client.subscribe(MQTT_TOPIC)
        print(f"Đang lắng nghe dữ liệu từ topic: {MQTT_TOPIC}\n")
    else:
        print(f"Kết nối thất bại, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)
        
        print(f"Đã nhận gói dữ liệu: {data}")
        temp = data.get('temperature')
        hum = data.get('humidity')
        dist = data.get('distance_cm')
        print(f" -> Tách dữ liệu: Nhiệt độ {temp}°C | Độ ẩm {hum}% | Khoảng cách {dist}cm")
        print("-" * 50)
        
    except json.JSONDecodeError:
        print("Lỗi: Gói tin không đúng định dạng JSON")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Đang kết nối tới broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()