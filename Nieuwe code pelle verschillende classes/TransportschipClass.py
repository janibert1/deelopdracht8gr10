"""Transportschip-klasse (alleen deklading, geen kraan)."""

from Ship_pelle import Ship


class TransportSchip(Ship):
    """Transportconditie: geen kraan, transition pieces aan dek.

    Deze subklasse zet alleen invoerdefaults; alle berekeningen blijven in `Ship`.
    """

    def __init__(self, file, TP_position, TP_mass, TP_amount, **kwargs):
        kwargs.setdefault("slewing_angle", 0.0)
        kwargs.setdefault("jib_angle", 0.0)

        super().__init__(
            file=file,
            TP_position=TP_position,
            TP_mass=TP_mass,
            TP_amount=TP_amount,
            crane_position=None,
            jib_length=None,
            **kwargs,
        )
