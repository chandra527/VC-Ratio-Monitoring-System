from traffic_volume_engine import TrafficVolumeEngine


engine = TrafficVolumeEngine(
    window_seconds=60
)

# Simulasi kendaraan selama 1 menit
for _ in range(10):
    engine.add_vehicle("motor")

for _ in range(4):
    engine.add_vehicle("mobil")

engine.add_vehicle("bus")
engine.add_vehicle("truk")


print("HASIL TEST TRAFFIC VOLUME")
print("=========================")
print("Jumlah kendaraan :", engine.counts)
print("Total SMP        :", engine.get_total_smp())
print("Volume           :", engine.get_volume_per_hour(), "smp/jam")

print()
print("TEST RESET")
print("=========================")

engine.reset()

print("Jumlah kendaraan :", engine.counts)
print("Total SMP        :", engine.get_total_smp())
print(
    "Volume           :",
    engine.get_volume_per_hour(),
    "smp/jam",
)

print()
print("TEST UNKNOWN VEHICLE")
print("=========================")

engine.add_vehicle("ambulans")
engine.add_vehicle("sepeda")

print("Jumlah kendaraan :", engine.counts)
print("Total SMP        :", engine.get_total_smp())
print(
    "Volume           :",
    engine.get_volume_per_hour(),
    "smp/jam",
)