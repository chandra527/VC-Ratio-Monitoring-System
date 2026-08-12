from vc_ratio_engine import VCRatioEngine


engine = VCRatioEngine()

volume = 636.0
capacity = 1087.35

vc_ratio = engine.calculate(
    volume=volume,
    capacity=capacity,
)

print("HASIL TEST VC RATIO")
print("===================")
print("Volume   :", volume, "smp/jam")
print("Capacity :", capacity, "smp/jam")
print("V/C      :", vc_ratio)
print("V/C      :", f"{vc_ratio:.2f}")