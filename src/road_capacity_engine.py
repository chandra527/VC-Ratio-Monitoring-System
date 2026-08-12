class RoadCapacityEngine:
    """
    Menghitung kapasitas jalan.

    Rumus:
        C = C0 * FCw * FCsp * FCsf * FCcs
    """

    def __init__(
        self,
        base_capacity,
        fc_width,
        fc_direction,
        fc_side_friction,
        fc_city_size,
    ):
        self.base_capacity = base_capacity
        self.fc_width = fc_width
        self.fc_direction = fc_direction
        self.fc_side_friction = fc_side_friction
        self.fc_city_size = fc_city_size

    def get_capacity(self):
        """
        Menghasilkan kapasitas jalan
        dalam smp/jam.
        """

        return (
            self.base_capacity
            * self.fc_width
            * self.fc_direction
            * self.fc_side_friction
            * self.fc_city_size
        )