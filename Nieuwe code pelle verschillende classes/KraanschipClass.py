"""Crane ship class (crane + TP in hook, no deck cargo)."""

from Ship_pelle import Ship


class KraanSchip(Ship):
    """Crane operating condition with one TP in the hook.

    Deck cargo amount is forced to zero for this load case.
    """

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        slewing_angle,
        jib_angle,
        TP_mass,
        TP_position=None,
        **kwargs,
    ):
        super().__init__(
            file=file,
            TP_position=TP_position,
            TP_mass=TP_mass,
            TP_amount=0,
            crane_position=crane_position,
            jib_length=jib_length,
            slewing_angle=slewing_angle,
            jib_angle=jib_angle,
            **kwargs,
        )
