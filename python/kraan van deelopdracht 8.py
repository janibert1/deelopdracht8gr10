#kraan
import math

def kraanmoment_tcg(TCG, graden, slewing_angle, SWL_max, lengte_boom, gewicht_transistion_piece=230000):
    """
    Berekent het totale dwarsscheepse moment (TCG-moment) van de kraan.

    Parameters
    ----------
    TCG : float
        Transversale zwaartepuntpositie van het kraanhuis [m].
    graden : float
        Giekhoek t.o.v. horizontaal [graden].
    SWL_max : float
        Safe Working Load (maximale hijslast) [kg].
    lengte_boom : float
        Lengte van de giek [m].
    gewicht_transistion_piece : float, optional
        Gewicht van transition piece [kg]. Default = 230000.

    Returns
    -------
    float
        Totaal dwarsscheeps moment rond referentiepunt [kg·m].
    """

    # bepaal teken (bakboord / stuurboord)
    if slewing_angle <= 180:
        sign = 1
    else:
        sign = -1

    angle_180 = slewing_angle if slewing_angle <= 180 else 360 - slewing_angle

    angle_90 = angle_180 if angle_180 <= 90 else 180 - angle_180

    TCG_boom = sign * 0.5 * (math.cos(math.radians(graden)) * lengte_boom) * math.sin(math.radians(angle_90))
    TCG_lading = TCG_boom * 2

    massa_lading = 0.06 * SWL_max + gewicht_transistion_piece
    massa_boom = 0.17 * SWL_max
    massa_huis = 0.34 * SWL_max

    return massa_lading * TCG_lading + massa_boom * TCG_boom + massa_huis * TCG


def kraanmoment_vcg(VCG, graden , SWL_max, lengte_boom, gewicht_transistion_piece=230000):
    """
    Berekent het totale verticale moment (VCG-moment) van de kraan.

    Parameters
    ----------
    VCG : float
        Verticale zwaartepuntpositie van het kraanhuis [m].
    graden : float
        Giekhoek t.o.v. horizontaal [graden].
    SWL_max : float
        Safe Working Load (maximale hijslast) [kg].
    lengte_boom : float
        Lengte van de giek [m].
    gewicht_transistion_piece : float, optional
        Gewicht van transition piece [kg]. Default = 230000.

    Returns
    -------
    float
        Totaal verticaal moment rond referentiepunt [kg·m].
    """

    VCG_boom = 0.5 * math.sin(math.radians(graden)) * lengte_boom + 1
    VCG_lading = VCG_boom * 2

    massa_lading = 0.06 * SWL_max + gewicht_transistion_piece
    massa_boom = 0.17 * SWL_max
    massa_huis = 0.34 * SWL_max

    return massa_lading * VCG_lading + massa_boom * VCG_boom + massa_huis * VCG

TCG = 2
SWL_max = 230000/0.94
lengte_boom = 30
graden = 45
VCG = 10
slewing_angle = 90

kraanmoment1 = kraanmoment_tcg(TCG, graden,slewing_angle, SWL_max=SWL_max, lengte_boom=lengte_boom, gewicht_transistion_piece=230000)
kraanmoment2 = kraanmoment_vcg(VCG, graden, SWL_max=SWL_max, lengte_boom=lengte_boom, gewicht_transistion_piece=230000)
    
print("Kraanmoment TCG:", kraanmoment1)
print("Kraanmoment VCG:", kraanmoment2)
