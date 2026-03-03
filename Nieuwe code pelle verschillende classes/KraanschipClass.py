"""Kraanschip-klasse (kraan + TP in de haak, geen deklading)."""

from Ship_pelle import Ship


class KraanSchip(Ship):
    """Kraanconditie met één TP in de haak.

    Deklading wordt in deze load case geforceerd op nul gezet.
    """

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        slewing_angle,
        jib_angle,
        hook_tp_mass_kg,
        crane_swl_mass_kg,
        hook_position=None,
        **kwargs,
    ):
        super().__init__(
            file=file,
            deck_tp_position=None,
            deck_tp_mass_kg=0.0,
            deck_tp_amount=0,
            crane_position=crane_position,
            jib_length=jib_length,
            slewing_angle=slewing_angle,
            jib_angle=jib_angle,
            hook_tp_mass_kg=hook_tp_mass_kg,
            crane_swl_mass_kg=crane_swl_mass_kg,
            hook_position=hook_position,
            **kwargs,
        )
