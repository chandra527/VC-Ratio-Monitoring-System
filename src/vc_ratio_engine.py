class VCRatioEngine:
    """
    Menghitung rasio volume terhadap kapasitas.

    Rumus:
        V/C = V / C
    """

    def calculate(
        self,
        volume,
        capacity,
    ):
        if capacity <= 0:
            return 0.0

        return (
            volume
            / capacity
        )