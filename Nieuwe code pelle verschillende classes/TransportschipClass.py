"""Transportschip-klasse (alleen deklading, geen kraan)."""

from Ship_pelle import Ship


class TransportSchip(Ship):
    """Transportconditie: geen kraan, transition pieces aan dek.

    Deze subklasse zet alleen invoerdefaults; alle berekeningen blijven in `Ship`.
    """

    def __init__(self, file, deck_tp_position, deck_tp_mass_kg, deck_tp_amount, **kwargs):
        kwargs.setdefault("slewing_angle", 0.0)
        kwargs.setdefault("jib_angle", 0.0)

        super().__init__(
            file=file,
            deck_tp_position=deck_tp_position,
            deck_tp_mass_kg=deck_tp_mass_kg,
            deck_tp_amount=deck_tp_amount,
            crane_position=None,
            jib_length=None,
            hook_tp_mass_kg=0.0,
            crane_swl_mass_kg=0.0,
            **kwargs,
        )
