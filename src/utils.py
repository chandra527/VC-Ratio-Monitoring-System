
def create_vehicle_data():

    return {
        "motor":0,
        "mobil":0,
        "bus":0,
        "truk":0,
        "ambulans":0
    }

def calculate_total(vehicle_data):

    total = (
        vehicle_data["motor"]
        + vehicle_data["mobil"]
        + vehicle_data["bus"]
        + vehicle_data["truk"]
        + vehicle_data["ambulans"]
    )

    return total


def create_traffic_data():

     return {
        "volume": 0,
        "capacity": 320,
        "vc_ratio": 0
    }


def calculate_vc_ratio(volume, capacity):

    if capacity == 0:
        return 0

    return volume / capacity


def get_traffic_status(vc_ratio):

    if vc_ratio < 0.60:
        return "LANCAR", (0,255,0)

    elif vc_ratio < 0.85:
        return "PADAT", (0,255,255)

    else:
        return "MACET", (0,0,255)
    


def get_center_x(container_width, object_width):
    """
    Menghitung posisi X agar objek berada tepat di tengah.
    """

    return (container_width - object_width) // 2

