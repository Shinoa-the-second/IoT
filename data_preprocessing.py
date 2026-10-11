import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.preprocessing import StandardScaler

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "fUJYXngtBwre2U9xWKeGMUIPZ4sYM3si2VisYpiwGDONmOio6gr5m1cTS9QUsM9a2MSFfYyvQo74J9ADRccG9A==" 
INFLUX_ORG = "Organization"                         
INFLUX_BUCKET = "Bucket"     

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=30000)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

print("Đang truy xuất dữ liệu từ InfluxDB...")
query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_environment")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
df = query_api.query_data_frame(query)

if not df.empty:
    cols_to_drop = ['result', 'table', '_start', '_stop', '_measurement']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    df.set_index('_time', inplace=True)
    df.index = df.index.tz_convert(None)
    
    print("\nDỮ LIỆU THÔ (5 dòng đầu):")
    print(df.head())

    df.ffill(inplace=True)

    for col in ['temperature', 'humidity', 'distance_cm']:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df[col] = np.where((df[col] < lower) | (df[col] > upper), df[col].median(), df[col])

    df_resampled = df[['temperature', 'humidity', 'distance_cm']].resample('10s').mean().dropna()

    df_resampled['temp_rolling_mean'] = df_resampled['temperature'].rolling(window=3).mean()
    df_resampled.dropna(inplace=True)

    scaler = StandardScaler()
    df_resampled['temp_scaled'] = scaler.fit_transform(df_resampled[['temperature']])

    print("\nDỮ LIỆU SAU TIỀN XỬ LÝ (5 dòng đầu):")
    print(df_resampled[['temperature', 'temp_rolling_mean', 'temp_scaled']].head())

    print("\nĐang ghi dữ liệu sạch vào measurement 'sensor_processed'...")
    for index, row in df_resampled.iterrows():
        p = Point("sensor_processed") \
            .tag("device_id", "ESP32_B23DCCN235") \
            .field("temperature", float(row['temperature'])) \
            .field("humidity", float(row['humidity'])) \
            .field("distance_cm", float(row['distance_cm'])) \
            .field("temp_rolling_mean", float(row['temp_rolling_mean'])) \
            .field("temp_scaled", float(row['temp_scaled'])) \
            .time(index, write_precision='s') # Ghi kèm nhãn thời gian cũ
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)
    print("Hoàn tất quy trình Tiền xử lý!")
else:
    print("Không tìm thấy dữ liệu trong 1 giờ qua. Hãy chạy MQTT script để thu thập thêm.")