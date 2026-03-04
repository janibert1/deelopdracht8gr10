"""Alleskunner-klasse (kraanoperatie + deklading)."""

from Ship_pelle import Ship


class Alleskunner(Ship):
    """Gecombineerde conditie met kraanlast en transition pieces aan dek.

    Deze klasse representeert de "alleskunner"-beladingsconditie uit de opdracht.
    """

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        slewing_angle,
        jib_angle,
        deck_tp_position,
        deck_tp_mass_kg,
        deck_tp_amount,
        hook_tp_mass_kg,
        crane_swl_mass_kg,
        hook_position=None,
        **kwargs,
    ):
        super().__init__(
            file=file,
            crane_position=crane_position,
            jib_length=jib_length,
            deck_tp_position=deck_tp_position,
            deck_tp_mass_kg=deck_tp_mass_kg,
            deck_tp_amount=deck_tp_amount,
            slewing_angle=slewing_angle,
            jib_angle=jib_angle,
            hook_tp_mass_kg=hook_tp_mass_kg,
            crane_swl_mass_kg=crane_swl_mass_kg,
            hook_position=hook_position,
            **kwargs,
        )
        
