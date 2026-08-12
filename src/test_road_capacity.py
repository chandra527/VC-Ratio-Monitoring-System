from road_capacity_engine import RoadCapacityEngine


engine = RoadCapacityEngine(
    base_capacity=1650,
    fc_width=0.91,
    fc_direction=1.0,
    fc_side_friction=0.77,
    fc_city_size=0.94,
)

capacity = engine.get_capacity()

print("HASIL TEST ROAD CAPACITY")
print("========================")
print("Capacity :", capacity, "smp/jam")