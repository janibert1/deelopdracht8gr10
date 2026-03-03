"""Alleskunner class (crane operation + deck cargo)."""

from Ship_pelle import Ship


class Alleskunner(Ship):
    """Combined condition with crane load and transition pieces on deck."""

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        slewing_angle,
        jib_angle,
        TP_position,
        TP_mass,
        TP_amount,
        **kwargs,
    ):
        super().__init__(
            file=file,
            crane_position=crane_position,
            jib_length=jib_length,
            TP_position=TP_position,
            TP_mass=TP_mass,
            TP_amount=TP_amount,
            slewing_angle=slewing_angle,
            jib_angle=jib_angle,
            **kwargs,
        )
        
