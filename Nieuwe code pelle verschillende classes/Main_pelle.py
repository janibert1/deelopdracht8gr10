"""Hoofdingang voor het class-gebaseerde scheepsrekenproject.

Dit script doet drie dingen:
1. Definieert een invoerscenario.
2. Rekent de drie scheepstypen door voor dat scenario.
3. Slaat resultaten op als JSON en grafiek in de lokale map `output/`.
"""

from copy import deepcopy
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from AlleskunnerClass import Alleskunner
from KraanschipClass import KraanSchip
from TransportschipClass import TransportSchip


def print_result(name, ship):
    """Print een compacte samenvatting van de belangrijkste uitkomsten.

    Parameters
    ----------
    name : str
        Weergavenaam van het scheepstype.
    ship : Ship
        Geïnstantieerd scheepsobject met berekende resultaten.
    """
    result = ship.to_dict()
    print(f"\n{name}")
    print(f"  Tank 1 vulling [%]: {result['tank1_percentage']:.4f}")
    print(f"  Tank 2 vulling [%]: {result['tank2_percentage']:.4f}")
    print(f"  Tank 2 lcg [m]: {result['tank2_lcg']:.4f}")
    print(f"  GM [m]: {result['GM']:.4f}")


def build_result_payload(file_id, constants, ship_results):
    """Bouw een JSON-serialiseerbare structuur voor opslag in `output/`."""
    payload = {
        "scenario": {
            "file_id": file_id,
            "constants": constants,
        },
        "results": ship_results,
    }
    return payload


def lees_input_data(file_id, data_dir):
    """Lees de InputData-json als deze aanwezig is."""
    path = data_dir / f"InputData_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def lees_antwoordenblad_template(data_dir):
    """Lees antwoordenblad-template vanuit data-map of bekende fallbacklocaties."""
    module_dir = Path(__file__).resolve().parent
    candidates = [
        data_dir / "antwoordenblad.json",
        Path.home() / "Downloads" / "antwoordenblad.json",
        module_dir.parent / "imports" / "group14" / "MT1466_Q3_1017PM" / "antwoordenblad.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as handle:
                return json.load(handle)
    raise FileNotFoundError(
        "Geen antwoordenblad-template gevonden. Plaats antwoordenblad.json in de data-map."
    )


def bereken_scheepseigenschappen(ship):
    """Bereken afgeleide krachten, momenten en totale zwaartepunten."""
    g = 9.81
    massa = np.asarray(ship.ship_data[0], dtype=float)
    lcg = np.asarray(ship.ship_data[1], dtype=float)
    tcg = np.asarray(ship.ship_data[2], dtype=float)
    vcg = np.asarray(ship.ship_data[3], dtype=float)

    totale_massa = np.sum(massa)
    deplacement_n = totale_massa * g
    lcg_tot = np.sum(massa * lcg) / totale_massa
    tcg_tot = np.sum(massa * tcg) / totale_massa
    vcg_tot = np.sum(massa * vcg) / totale_massa

    buoyancy_n = ship.buoyant_mass * g
    verticaal_afwijking = buoyancy_n - deplacement_n

    neer_m_long = np.sum((massa * g) * (lcg - ship.COV[0]))
    op_m_long = buoyancy_n * (ship.COB[0] - ship.COV[0])
    afwijking_long = op_m_long - neer_m_long

    neer_m_trans = np.sum((massa * g) * tcg)
    op_m_trans = buoyancy_n * ship.COB[1]
    afwijking_trans = op_m_trans - neer_m_trans

    return {
        "deplacement_n": float(deplacement_n),
        "lcg_tot": float(lcg_tot),
        "tcg_tot": float(tcg_tot),
        "vcg_tot": float(vcg_tot),
        "buoyancy_n": float(buoyancy_n),
        "verticaal_afwijking": float(verticaal_afwijking),
        "afwijking_long": float(afwijking_long),
        "afwijking_trans": float(afwijking_trans),
    }


def vul_antwoordenblad_in(template, ship_name, ship, constants, input_data, group_number):
    """Vul antwoordenblad in met berekende waarden zonder keys te wijzigen."""
    data = deepcopy(template)
    props = bereken_scheepseigenschappen(ship)

    data["Project_info"]["Groepsnummer #[-]"] = group_number
    data["Project_info"]["MT #[jaar]"] = "MT1466"
    data["Project_info"]["Groepsversie #[naam/nummer]"] = (
        f"{group_number}.{ship.file[1]}.{ship.file[2]}_{ship_name}"
    )

    data["Stabiliteit"]["GM_aanvangsstabiliteit #[m]"] = round(float(ship.GM), 4)

    if input_data:
        toggle = input_data.get("INPUT DATA", {}).get("Toggle_1_ship/0_barge")
        if toggle is not None:
            data["Geometrie"]["Toggle_Ship_1_Barge_0 #[1/0]"] = str(int(toggle))

    draught = ship.main_data.get("DRAUGHT DATA", {}).get("T_moulded_m", data["Geometrie"]["Diepgang #[m]"])
    data["Geometrie"]["Lengte #[m]"] = round(float(ship.LOA), 4)
    data["Geometrie"]["Breedte #[m]"] = round(float(ship.width), 4)
    data["Geometrie"]["Holte #[m]"] = round(float(ship.height), 4)
    data["Geometrie"]["Diepgang #[m]"] = round(float(draught), 4)
    data["Geometrie"]["Trim #[graden]"] = 0
    data["Geometrie"]["Hellingshoek #[graden]"] = 0

    data["Constructie"]["Huid_en_dek_dikte #[mm]"] = float(max(constants["hull_thickness"]) * 1000.0)

    tank_percentages = [ship.tank1_percentage, ship.tank2_percentage, ship.tank3_initial]
    data["Waterballast"]["Aantal_WB_tanks #[-]"] = 3
    data["Waterballast"]["WB_tank_gevuld #[Ja/Nee]"] = (
        "ja" if any(p > 0 for p in tank_percentages) else "nee"
    )
    data["Waterballast"]["WB_tank_gedeeltelijk_gevuld #[Ja/Nee]"] = (
        "ja" if any(0 < p < 100 for p in tank_percentages) else "nee"
    )

    data["Materiaal"]["Soortelijk_gewicht_staal #[kg/m3]"] = constants["material_density"]
    data["Materiaal"]["Soortelijk_gewicht_zeewater #[kg/m3]"] = constants["water_density"]

    data["Neerwaartse_krachten"]["Deplacement #[N]"] = round(props["deplacement_n"], 3)
    data["Neerwaartse_krachten"]["LCG #[m]"] = round(props["lcg_tot"], 4)
    data["Neerwaartse_krachten"]["TCG #[m]"] = round(props["tcg_tot"], 4)
    data["Neerwaartse_krachten"]["VCG #[m]"] = round(props["vcg_tot"], 4)

    data["Opwaartse_krachten"]["Buoyancy #[N]"] = round(props["buoyancy_n"], 3)
    data["Opwaartse_krachten"]["LCB #[m]"] = round(float(ship.COB[0]), 4)
    data["Opwaartse_krachten"]["TCB #[m]"] = round(float(ship.COB[1]), 4)
    data["Opwaartse_krachten"]["VCB #[m]"] = round(float(ship.COB[2]), 4)

    data["Evenwichtsafwijkingen"]["Afwijking_verticaal_krachtevenwicht #[N]"] = round(
        props["verticaal_afwijking"], 3
    )
    data["Evenwichtsafwijkingen"]["Afwijking_longitudinaal_momentevenwicht #[Nm]"] = round(
        props["afwijking_long"], 3
    )
    data["Evenwichtsafwijkingen"]["Afwijking_transversaal_momentevenwicht #[Nm]"] = round(
        props["afwijking_trans"], 3
    )

    tp_amount = int(constants["TP_amount"]) if ship_name in ("TransportSchip", "Alleskunner") else 0
    data["Deklast_transition_pieces"]["Aantal_transition_pieces #[-]"] = tp_amount
    data["Deklast_transition_pieces"]["Gewicht_per_transition_piece #[N]"] = float(constants["TP_mass"])
    data["Deklast_transition_pieces"]["LCG_transition_pieces #[m]"] = float(constants["TP_position"][0])
    data["Deklast_transition_pieces"]["TCG_transition_pieces #[m]"] = float(constants["TP_position"][1])
    data["Deklast_transition_pieces"]["VCG_transition_pieces #[m]"] = float(constants["TP_position"][2])

    has_crane = ship_name in ("KraanSchip", "Alleskunner")
    swlmax = float(constants["TP_mass"] / 0.94)
    data["Kraan_beladingsconditie"]["SWLmax_kraan #[N]"] = swlmax
    data["Kraan_beladingsconditie"]["Aantal_TP_in_kraan #[-]"] = 1 if has_crane else 0
    data["Kraan_beladingsconditie"]["Gewicht_per_TP #[N]"] = float(constants["TP_mass"])
    data["Kraan_beladingsconditie"]["Draaihoogte_kraan #[m]"] = float(constants["pivot_height"])
    data["Kraan_beladingsconditie"]["Kraanboom_lengte #[m]"] = float(constants["jib_length"])
    data["Kraan_beladingsconditie"]["Zwenkhoek #[graden]"] = float(constants["slewing_angle"])
    data["Kraan_beladingsconditie"]["Giekhoek #[graden]"] = float(constants["jib_angle"])

    if has_crane and ship.deck_data.shape[1] >= 3:
        data["Zwaartepunten_kraanlast"]["LCG_kraanlast #[m]"] = round(float(ship.deck_data[1][2]), 4)
        data["Zwaartepunten_kraanlast"]["TCG_kraanlast #[m]"] = round(float(ship.deck_data[2][2]), 4)
        data["Zwaartepunten_kraanlast"]["VCG_kraanlast #[m]"] = round(float(ship.deck_data[3][2]), 4)
        data["Zwaartepunten_kraanlast"]["LCG_kraanhuis #[m]"] = round(float(ship.deck_data[1][0]), 4)
        data["Zwaartepunten_kraanlast"]["TCG_kraanhuis #[m]"] = round(float(ship.deck_data[2][0]), 4)
        data["Zwaartepunten_kraanlast"]["VCG_kraanhuis #[m]"] = round(float(ship.deck_data[3][0]), 4)
        data["Zwaartepunten_kraanlast"]["LCG_kraanboom #[m]"] = round(float(ship.deck_data[1][1]), 4)
        data["Zwaartepunten_kraanlast"]["TCG_kraanboom #[m]"] = round(float(ship.deck_data[2][1]), 4)
        data["Zwaartepunten_kraanlast"]["VCG_kraanboom #[m]"] = round(float(ship.deck_data[3][1]), 4)
        data["Zwaartepunten_kraanlast"]["LCG_hijsgerei #[m]"] = round(float(ship.deck_data[1][2]), 4)
        data["Zwaartepunten_kraanlast"]["TCG_hijsgerei #[m]"] = round(float(ship.deck_data[2][2]), 4)
        data["Zwaartepunten_kraanlast"]["VCG_hijsgerei #[m]"] = round(float(ship.deck_data[3][2]), 4)

    lading_locaties = data.get("Lading_locaties", {})
    for i in range(1, 5):
        key = f"Transition_piece_{i}"
        if key in lading_locaties and i <= tp_amount:
            lading_locaties[key]["LCG #[m]"] = float(constants["TP_position"][0])
            lading_locaties[key]["TCG #[m]"] = float(constants["TP_position"][1])
            lading_locaties[key]["VCG #[m]"] = float(constants["TP_position"][2])

    return data


def schrijf_antwoordenbladen(output_dir, template, ship_objects, constants, input_data, group_number):
    """Schrijf ingevulde antwoordenbladen per scheepstype naar de output-map."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paden = {}
    for ship_name, ship in ship_objects.items():
        ingevuld = vul_antwoordenblad_in(
            template=template,
            ship_name=ship_name,
            ship=ship,
            constants=constants,
            input_data=input_data,
            group_number=group_number,
        )
        pad = output_dir / f"antwoordenblad_{ship_name}.json"
        with open(pad, "w", encoding="utf-8") as handle:
            json.dump(ingevuld, handle, indent=4)
        paden[ship_name] = pad

    # Standaard outputbestand volgens opdrachtconventie.
    default_path = output_dir / "antwoordenblad.json"
    with open(paden["Alleskunner"], "r", encoding="utf-8") as handle:
        default_data = json.load(handle)
    with open(default_path, "w", encoding="utf-8") as handle:
        json.dump(default_data, handle, indent=4)
    paden["default"] = default_path
    return paden


def write_results_json(output_dir, payload):
    """Schrijf modeluitvoer naar JSON voor traceerbaarheid en vergelijking."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ship_results.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)
    return output_path


def write_results_graph(output_dir, ship_results):
    """Maak en bewaar een PNG-grafiek met berekende scheepskengetallen.

    De grafiek toont:
    - GM per scheepstype
    - Vullingspercentage van tank 1 en 2 per scheepstype
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    names = list(ship_results.keys())
    gm_values = [ship_results[name]["GM"] for name in names]
    tank1_values = [ship_results[name]["tank1_percentage"] for name in names]
    tank2_values = [ship_results[name]["tank2_percentage"] for name in names]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    axes[0].bar(names, gm_values, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    axes[0].set_title("Aanvangsstabiliteit (GM) per scheepstype")
    axes[0].set_ylabel("GM [m]")
    axes[0].axhline(0.0, color="black", linewidth=1)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    x = np.arange(len(names))
    width = 0.35
    axes[1].bar(x - width / 2, tank1_values, width=width, label="Tank 1 vulling [%]")
    axes[1].bar(x + width / 2, tank2_values, width=width, label="Tank 2 vulling [%]")
    axes[1].set_title("Berekende tankvullingspercentages")
    axes[1].set_ylabel("Vulling [% van h_tank]")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    output_path = output_dir / "ship_results_graph.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main():
    """Bouw en run de drie scheepstypen voor één scenario.

    Returns
    -------
    tuple[pathlib.Path, pathlib.Path]
        Paden naar het gegenereerde JSON-bestand en de PNG-grafiek.
    """
    groepsnummer = 14
    file_id = [98, 1, 0]  # [groep-data, versie, subversie]
    data_dir = Path(__file__).resolve().parent / "data"
    output_dir = Path(__file__).resolve().parent / "output"

    # Constanten
    tank3_initial = 70
    hull_thickness = np.array([0.012, 0.012, 0.012])  # [spiegel, huid, dek]
    BHD_thickness = 0.012
    mass_factor = 2.1
    material_density = 7850
    water_density = 1025

    crane_position = [11, 0, 6]
    TP_position = [76.0925, 0, 18]
    TP_mass = 2256300.0
    TP_amount = 4
    jib_length = 40
    jib_angle = 45
    slewing_angle = 180
    pivot_height = 1.0

    # Gedeelde modelinvoer die door elk scheepstype wordt gebruikt.
    shared_kwargs = dict(
        hull_thickness=hull_thickness,
        BHD_thickness=BHD_thickness,
        tank3_initial=tank3_initial,
        water_density=water_density,
        material_density=material_density,
        mass_factor=mass_factor,
        data_dir=data_dir,
    )

    # Bouw scheepstype-specifieke objecten met hergebruik van dezelfde `Ship`-logica.
    transport = TransportSchip(
        file=file_id,
        TP_position=TP_position,
        TP_mass=TP_mass,
        TP_amount=TP_amount,
        **shared_kwargs,
    )

    kraanschip = KraanSchip(
        file=file_id,
        crane_position=crane_position,
        jib_length=jib_length,
        slewing_angle=slewing_angle,
        jib_angle=jib_angle,
        TP_mass=TP_mass,
        TP_position=TP_position,
        pivot_height=pivot_height,
        **shared_kwargs,
    )

    alleskunner = Alleskunner(
        file=file_id,
        crane_position=crane_position,
        jib_length=jib_length,
        slewing_angle=slewing_angle,
        jib_angle=jib_angle,
        TP_position=TP_position,
        TP_mass=TP_mass,
        TP_amount=TP_amount,
        pivot_height=pivot_height,
        **shared_kwargs,
    )

    # Print een korte samenvatting in de terminal.
    print_result("TransportSchip", transport)
    print_result("KraanSchip", kraanschip)
    print_result("Alleskunner", alleskunner)

    ship_results = {
        "TransportSchip": transport.to_dict(),
        "KraanSchip": kraanschip.to_dict(),
        "Alleskunner": alleskunner.to_dict(),
    }
    constants = {
        "tank3_initial": tank3_initial,
        "hull_thickness": hull_thickness.tolist(),
        "BHD_thickness": BHD_thickness,
        "mass_factor": mass_factor,
        "material_density": material_density,
        "water_density": water_density,
        "crane_position": crane_position,
        "TP_position": TP_position,
        "TP_mass": TP_mass,
        "TP_amount": TP_amount,
        "jib_length": jib_length,
        "jib_angle": jib_angle,
        "slewing_angle": slewing_angle,
        "pivot_height": pivot_height,
    }
    payload = build_result_payload(file_id, constants, ship_results)
    json_path = write_results_json(output_dir, payload)
    graph_path = write_results_graph(output_dir, ship_results)
    input_data = lees_input_data(file_id, data_dir)
    template = lees_antwoordenblad_template(data_dir)
    antwoordenblad_paden = schrijf_antwoordenbladen(
        output_dir=output_dir,
        template=template,
        ship_objects={
            "TransportSchip": transport,
            "KraanSchip": kraanschip,
            "Alleskunner": alleskunner,
        },
        constants=constants,
        input_data=input_data,
        group_number=groepsnummer,
    )

    print(f"\nJSON-resultaten opgeslagen in: {json_path}")
    print(f"PNG-grafiek opgeslagen in:    {graph_path}")
    print(f"Antwoordenblad opgeslagen in: {antwoordenblad_paden['default']}")
    return json_path, graph_path, antwoordenblad_paden["default"]


if __name__ == "__main__":
    main()
