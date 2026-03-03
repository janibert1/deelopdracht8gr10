"""Hoofdingang voor het class-gebaseerde scheepsrekenproject.

Belangrijkste keuzes in deze versie:
- interne rekeneenheden zijn strikt kg, m, kgm;
- kraan-SWL bepaalt alleen kraanhuis/giekmassa;
- gehesen TP-massa wordt apart gemodelleerd;
- tankoplossingen zijn begrensd (geen extrapolatie buiten diagrammen);
- output wordt geschreven naar het antwoordenblad-format.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from AlleskunnerClass import Alleskunner
from Functions_pelle import DataValidatieFout, InfeasibleLoadCaseError
from KraanschipClass import KraanSchip
from TransportschipClass import TransportSchip

G = 9.81


@dataclass
class BasisScenarioConfig:
    """Gezamenlijke invoer voor alle load cases."""

    groepsnummer: int
    file_id: list[int]
    data_dir: Path
    fallback_data_dir: Path
    allow_fallback: bool

    hull_thickness_m: float
    BHD_thickness_m: float
    mass_factor: float
    material_density: float
    water_density: float
    tank3_initial: float

    crane_position: list[float]
    hook_position: list[float] | None
    deck_tp_positions: list[list[float]]

    deck_tp_weight_n: float
    deck_tp_mass_kg: float
    deck_tp_amount: int

    hook_tp_weight_n: float
    hook_tp_mass_kg: float

    crane_swl_weight_n: float
    crane_swl_mass_kg: float

    jib_length: float
    jib_angle: float
    slewing_angle: float
    pivot_height: float
    tank2_is_movable: bool
    strict_residuen: bool


@dataclass
class LoadCaseConfig:
    """Invoerconfiguratie voor één scheepstype/load case."""

    naam: str
    heeft_kraan: bool
    deck_tp_amount: int
    hook_tp_mass_kg: float


def gewicht_n_naar_massa_kg(gewicht_n):
    """Converteer gewicht [N] naar massa [kg]."""
    return float(gewicht_n) / G


def massa_kg_naar_gewicht_n(massa_kg):
    """Converteer massa [kg] naar gewicht [N]."""
    return float(massa_kg) * G


def parse_file_id_uit_template(template):
    """Lees file_id uit Groepsversie (bijv. '98.1.0')."""
    groepsversie = str(template["Project_info"].get("Groepsversie #[naam/nummer]", "98.1.0"))
    kern = groepsversie.split("_")[0].strip()
    delen = kern.split(".")
    if len(delen) < 3:
        raise DataValidatieFout(
            f"Ongeldige Groepsversie in antwoordenblad: '{groepsversie}'. Verwacht 'gr.ver.sub'."
        )
    try:
        return [int(delen[0]), int(delen[1]), int(delen[2])]
    except ValueError as exc:
        raise DataValidatieFout(
            f"Groepsversie bevat niet-numerieke delen: '{groepsversie}'."
        ) from exc


def lees_json(path):
    """Lees JSON-bestand naar dictionary."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def lees_antwoordenblad_template(data_dir):
    """Lees antwoordenblad-template vanuit data-map (strikt vereist)."""
    path = data_dir / "antwoordenblad.json"
    if not path.exists():
        raise DataValidatieFout(
            f"Template ontbreekt: {path}. Plaats antwoordenblad.json in de data-map."
        )
    return lees_json(path)


def lees_input_data(file_id, data_dir):
    """Lees InputData json voor de opgegeven file_id."""
    path = data_dir / f"InputData_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.json"
    if not path.exists():
        raise DataValidatieFout(f"InputData ontbreekt: {path}")
    return lees_json(path)


def bouw_basis_scenario_config(
    data_dir, fallback_data_dir, allow_fallback, tank2_is_movable, strict_residuen
):
    """Bouw basisconfig uit antwoordenblad.json en InputData_*.json."""
    template = lees_antwoordenblad_template(data_dir)
    file_id = parse_file_id_uit_template(template)
    input_data = lees_input_data(file_id, data_dir)

    groepsnummer = int(template["Project_info"].get("Groepsnummer #[-]", 14))
    constructie = template["Constructie"]
    materiaal = template["Materiaal"]
    kraan = template["Kraan_beladingsconditie"]
    kraanzp = template["Zwaartepunten_kraanlast"]
    deklast = template["Deklast_transition_pieces"]

    huid_dikte_mm = float(constructie["Huid_en_dek_dikte #[mm]"])
    hull_thickness_m = huid_dikte_mm / 1000.0

    tank3_initial = float(input_data["INPUT DATA"]["Filling_Tank_3_%h3"])
    water_density = float(materiaal["Soortelijk_gewicht_zeewater #[kg/m3]"])
    material_density = float(materiaal["Soortelijk_gewicht_staal #[kg/m3]"])

    deck_tp_weight_n = float(deklast["Gewicht_per_transition_piece #[N]"])
    deck_tp_mass_kg = gewicht_n_naar_massa_kg(deck_tp_weight_n)
    deck_tp_amount = int(deklast["Aantal_transition_pieces #[-]"])

    lading_locaties = template.get("Lading_locaties", {})
    deck_tp_positions = []
    for i in range(1, deck_tp_amount + 1):
        key = f"Transition_piece_{i}"
        if key in lading_locaties:
            deck_tp_positions.append(
                [
                    float(lading_locaties[key]["LCG #[m]"]),
                    float(lading_locaties[key]["TCG #[m]"]),
                    float(lading_locaties[key]["VCG #[m]"]),
                ]
            )
    if len(deck_tp_positions) != deck_tp_amount:
        # Fallback op geaggregeerde deklastpositie als individuele TP-posities ontbreken.
        deck_tp_positions = [
            [
                float(deklast["LCG_transition_pieces #[m]"]),
                float(deklast["TCG_transition_pieces #[m]"]),
                float(deklast["VCG_transition_pieces #[m]"]),
            ]
            for _ in range(deck_tp_amount)
        ]

    hook_tp_weight_n = float(kraan["Gewicht_per_TP #[N]"])
    hook_tp_mass_kg = gewicht_n_naar_massa_kg(hook_tp_weight_n)
    crane_swl_weight_n = float(kraan["SWLmax_kraan #[N]"])
    crane_swl_mass_kg = gewicht_n_naar_massa_kg(crane_swl_weight_n)

    return BasisScenarioConfig(
        groepsnummer=groepsnummer,
        file_id=file_id,
        data_dir=data_dir,
        fallback_data_dir=fallback_data_dir,
        allow_fallback=allow_fallback,
        hull_thickness_m=hull_thickness_m,
        BHD_thickness_m=0.01,
        mass_factor=2.1,
        material_density=material_density,
        water_density=water_density,
        tank3_initial=tank3_initial,
        crane_position=[
            float(kraanzp["LCG_kraanhuis #[m]"]),
            float(kraanzp["TCG_kraanhuis #[m]"]),
            float(kraanzp["VCG_kraanhuis #[m]"]),
        ],
        hook_position=[
            float(kraanzp["LCG_kraanlast #[m]"]),
            float(kraanzp["TCG_kraanlast #[m]"]),
            float(kraanzp["VCG_kraanlast #[m]"]),
        ],
        deck_tp_positions=deck_tp_positions,
        deck_tp_weight_n=deck_tp_weight_n,
        deck_tp_mass_kg=deck_tp_mass_kg,
        deck_tp_amount=deck_tp_amount,
        hook_tp_weight_n=hook_tp_weight_n,
        hook_tp_mass_kg=hook_tp_mass_kg,
        crane_swl_weight_n=crane_swl_weight_n,
        crane_swl_mass_kg=crane_swl_mass_kg,
        jib_length=float(kraan["Kraanboom_lengte #[m]"]),
        jib_angle=float(kraan["Giekhoek #[graden]"]),
        slewing_angle=float(kraan["Zwenkhoek #[graden]"]),
        pivot_height=float(kraan["Draaihoogte_kraan #[m]"]),
        tank2_is_movable=bool(tank2_is_movable),
        strict_residuen=bool(strict_residuen),
    )


def bouw_loadcases(basis):
    """Definieer de drie verplichte scheepstypen."""
    return {
        "TransportSchip": LoadCaseConfig(
            naam="TransportSchip",
            heeft_kraan=False,
            deck_tp_amount=basis.deck_tp_amount,
            hook_tp_mass_kg=0.0,
        ),
        "KraanSchip": LoadCaseConfig(
            naam="KraanSchip",
            heeft_kraan=True,
            deck_tp_amount=0,
            hook_tp_mass_kg=basis.hook_tp_mass_kg,
        ),
        "Alleskunner": LoadCaseConfig(
            naam="Alleskunner",
            heeft_kraan=True,
            deck_tp_amount=basis.deck_tp_amount,
            hook_tp_mass_kg=basis.hook_tp_mass_kg,
        ),
    }


def maak_ship_object(loadcase, basis):
    """Maak ship-object voor één load case."""
    gedeeld = dict(
        file=basis.file_id,
        hull_thickness=np.array([basis.hull_thickness_m, basis.hull_thickness_m, basis.hull_thickness_m]),
        BHD_thickness=basis.BHD_thickness_m,
        tank3_initial=basis.tank3_initial,
        water_density=basis.water_density,
        material_density=basis.material_density,
        mass_factor=basis.mass_factor,
        data_dir=basis.data_dir,
        fallback_data_dir=basis.fallback_data_dir,
        allow_fallback=basis.allow_fallback,
        pivot_height=basis.pivot_height,
        tank2_is_movable=basis.tank2_is_movable,
        strict_residuen=basis.strict_residuen,
    )

    if loadcase.naam == "TransportSchip":
        return TransportSchip(
            deck_tp_position=basis.deck_tp_positions,
            deck_tp_mass_kg=basis.deck_tp_mass_kg,
            deck_tp_amount=loadcase.deck_tp_amount,
            **gedeeld,
        )

    if loadcase.naam == "KraanSchip":
        return KraanSchip(
            crane_position=basis.crane_position,
            jib_length=basis.jib_length,
            slewing_angle=basis.slewing_angle,
            jib_angle=basis.jib_angle,
            hook_tp_mass_kg=loadcase.hook_tp_mass_kg,
            crane_swl_mass_kg=basis.crane_swl_mass_kg,
            hook_position=basis.hook_position,
            **gedeeld,
        )

    if loadcase.naam == "Alleskunner":
        return Alleskunner(
            crane_position=basis.crane_position,
            jib_length=basis.jib_length,
            slewing_angle=basis.slewing_angle,
            jib_angle=basis.jib_angle,
            deck_tp_position=basis.deck_tp_positions,
            deck_tp_mass_kg=basis.deck_tp_mass_kg,
            deck_tp_amount=loadcase.deck_tp_amount,
            hook_tp_mass_kg=loadcase.hook_tp_mass_kg,
            crane_swl_mass_kg=basis.crane_swl_mass_kg,
            hook_position=basis.hook_position,
            **gedeeld,
        )

    raise DataValidatieFout(f"Onbekende load case: {loadcase.naam}")


def print_result(name, ship):
    """Print compacte samenvatting van een load case."""
    result = ship.to_dict()
    print(f"\n{name}")
    print(f"  Tank 1 vulling [%]: {result['tank1_percentage']:.4f}")
    print(f"  Tank 2 vulling [%]: {result['tank2_percentage']:.4f}")
    print(f"  Tank 2 lcg [m]: {result['tank2_lcg']:.4f}")
    print(f"  GM [m]: {result['GM']:.4f}")
    print(f"  Residu kracht [kg]: {result['force_residual_kg']:.4f}")


def build_result_payload(basis, ship_results):
    """Bouw JSON-serialiseerbare payload met scenario en resultaten."""
    return {
        "scenario": {
            "groepsnummer": basis.groepsnummer,
            "file_id": basis.file_id,
            "hull_thickness_m": basis.hull_thickness_m,
            "BHD_thickness_m": basis.BHD_thickness_m,
            "mass_factor": basis.mass_factor,
            "material_density": basis.material_density,
            "water_density": basis.water_density,
            "tank3_initial": basis.tank3_initial,
            "deck_tp_weight_n": basis.deck_tp_weight_n,
            "deck_tp_mass_kg": basis.deck_tp_mass_kg,
            "hook_tp_weight_n": basis.hook_tp_weight_n,
            "hook_tp_mass_kg": basis.hook_tp_mass_kg,
            "crane_swl_weight_n": basis.crane_swl_weight_n,
            "crane_swl_mass_kg": basis.crane_swl_mass_kg,
            "jib_length": basis.jib_length,
            "jib_angle": basis.jib_angle,
            "slewing_angle": basis.slewing_angle,
            "pivot_height": basis.pivot_height,
            "allow_fallback": basis.allow_fallback,
            "tank2_is_movable": basis.tank2_is_movable,
            "strict_residuen": basis.strict_residuen,
        },
        "results": ship_results,
    }


def write_results_json(output_dir, payload):
    """Schrijf modeluitvoer naar JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ship_results.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)
    return output_path


def write_results_graph(output_dir, ship_results):
    """Maak en bewaar PNG-grafiek met GM en tankvullingspercentages."""
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


def bereken_scheepseigenschappen(ship):
    """Bereken afgeleide kracht- en momentgrootheden."""
    massa = np.asarray(ship.ship_data[0], dtype=float)
    lcg = np.asarray(ship.ship_data[1], dtype=float)
    tcg = np.asarray(ship.ship_data[2], dtype=float)
    vcg = np.asarray(ship.ship_data[3], dtype=float)

    totale_massa = float(np.sum(massa))
    deplacement_n = massa_kg_naar_gewicht_n(totale_massa)
    lcg_tot = float(np.sum(massa * lcg) / totale_massa)
    tcg_tot = float(np.sum(massa * tcg) / totale_massa)
    vcg_tot = float(np.sum(massa * vcg) / totale_massa)

    buoyancy_n = massa_kg_naar_gewicht_n(ship.buoyant_mass)
    verticaal_afwijking_n = buoyancy_n - deplacement_n

    neer_m_long_nm = float(np.sum((massa * G) * (lcg - ship.COV[0])))
    op_m_long_nm = float(buoyancy_n * (ship.COB[0] - ship.COV[0]))
    afwijking_long_nm = op_m_long_nm - neer_m_long_nm

    neer_m_trans_nm = float(np.sum((massa * G) * tcg))
    op_m_trans_nm = float(buoyancy_n * ship.COB[1])
    afwijking_trans_nm = op_m_trans_nm - neer_m_trans_nm

    return {
        "deplacement_n": deplacement_n,
        "lcg_tot": lcg_tot,
        "tcg_tot": tcg_tot,
        "vcg_tot": vcg_tot,
        "buoyancy_n": buoyancy_n,
        "verticaal_afwijking_n": verticaal_afwijking_n,
        "afwijking_long_nm": afwijking_long_nm,
        "afwijking_trans_nm": afwijking_trans_nm,
    }


def vul_antwoordenblad_in(template, ship_name, ship, basis, loadcase):
    """Vul antwoordenblad in zonder key-structuur te wijzigen."""
    data = deepcopy(template)
    props = bereken_scheepseigenschappen(ship)

    data["Project_info"]["Groepsnummer #[-]"] = basis.groepsnummer
    data["Project_info"]["MT #[jaar]"] = "MT1466"
    data["Project_info"]["Groepsversie #[naam/nummer]"] = (
        f"{basis.groepsnummer}.{basis.file_id[1]}.{basis.file_id[2]}_{ship_name}"
    )

    data["Stabiliteit"]["GM_aanvangsstabiliteit #[m]"] = round(float(ship.GM), 4)

    data["Geometrie"]["Lengte #[m]"] = round(float(ship.LOA), 4)
    data["Geometrie"]["Breedte #[m]"] = round(float(ship.width), 4)
    data["Geometrie"]["Holte #[m]"] = round(float(ship.height), 4)
    data["Geometrie"]["Trim #[graden]"] = 0
    data["Geometrie"]["Hellingshoek #[graden]"] = 0

    data["Constructie"]["Huid_en_dek_dikte #[mm]"] = round(basis.hull_thickness_m * 1000.0, 3)
    data["Materiaal"]["Soortelijk_gewicht_staal #[kg/m3]"] = basis.material_density
    data["Materiaal"]["Soortelijk_gewicht_zeewater #[kg/m3]"] = basis.water_density

    tank_percentages = [ship.tank1_percentage, ship.tank2_percentage, ship.tank3_initial]
    data["Waterballast"]["Aantal_WB_tanks #[-]"] = 3
    data["Waterballast"]["WB_tank_gevuld #[Ja/Nee]"] = (
        "ja" if any(p > 0 for p in tank_percentages) else "nee"
    )
    data["Waterballast"]["WB_tank_gedeeltelijk_gevuld #[Ja/Nee]"] = (
        "ja" if any(0 < p < 100 for p in tank_percentages) else "nee"
    )

    data["Neerwaartse_krachten"]["Deplacement #[N]"] = round(props["deplacement_n"], 3)
    data["Neerwaartse_krachten"]["LCG #[m]"] = round(props["lcg_tot"], 4)
    data["Neerwaartse_krachten"]["TCG #[m]"] = round(props["tcg_tot"], 4)
    data["Neerwaartse_krachten"]["VCG #[m]"] = round(props["vcg_tot"], 4)

    data["Opwaartse_krachten"]["Buoyancy #[N]"] = round(props["buoyancy_n"], 3)
    data["Opwaartse_krachten"]["LCB #[m]"] = round(float(ship.COB[0]), 4)
    data["Opwaartse_krachten"]["TCB #[m]"] = round(float(ship.COB[1]), 4)
    data["Opwaartse_krachten"]["VCB #[m]"] = round(float(ship.COB[2]), 4)

    data["Evenwichtsafwijkingen"]["Afwijking_verticaal_krachtevenwicht #[N]"] = round(
        props["verticaal_afwijking_n"], 3
    )
    data["Evenwichtsafwijkingen"]["Afwijking_longitudinaal_momentevenwicht #[Nm]"] = round(
        props["afwijking_long_nm"], 3
    )
    data["Evenwichtsafwijkingen"]["Afwijking_transversaal_momentevenwicht #[Nm]"] = round(
        props["afwijking_trans_nm"], 3
    )

    data["Deklast_transition_pieces"]["Aantal_transition_pieces #[-]"] = int(loadcase.deck_tp_amount)
    data["Deklast_transition_pieces"]["Gewicht_per_transition_piece #[N]"] = round(
        basis.deck_tp_weight_n, 3
    )
    if loadcase.deck_tp_amount > 0:
        lcg_avg = float(np.mean([p[0] for p in basis.deck_tp_positions[: loadcase.deck_tp_amount]]))
        tcg_avg = float(np.mean([p[1] for p in basis.deck_tp_positions[: loadcase.deck_tp_amount]]))
        vcg_avg = float(np.mean([p[2] for p in basis.deck_tp_positions[: loadcase.deck_tp_amount]]))
    else:
        lcg_avg = tcg_avg = vcg_avg = 0.0
    data["Deklast_transition_pieces"]["LCG_transition_pieces #[m]"] = round(lcg_avg, 4)
    data["Deklast_transition_pieces"]["TCG_transition_pieces #[m]"] = round(tcg_avg, 4)
    data["Deklast_transition_pieces"]["VCG_transition_pieces #[m]"] = round(vcg_avg, 4)

    data["Kraan_beladingsconditie"]["SWLmax_kraan #[N]"] = round(basis.crane_swl_weight_n, 3)
    data["Kraan_beladingsconditie"]["Aantal_TP_in_kraan #[-]"] = (
        1 if loadcase.hook_tp_mass_kg > 0 else 0
    )
    data["Kraan_beladingsconditie"]["Gewicht_per_TP #[N]"] = round(
        basis.hook_tp_weight_n, 3
    )
    data["Kraan_beladingsconditie"]["Draaihoogte_kraan #[m]"] = round(basis.pivot_height, 4)
    data["Kraan_beladingsconditie"]["Kraanboom_lengte #[m]"] = round(basis.jib_length, 4)
    data["Kraan_beladingsconditie"]["Zwenkhoek #[graden]"] = round(basis.slewing_angle, 4)
    data["Kraan_beladingsconditie"]["Giekhoek #[graden]"] = round(basis.jib_angle, 4)

    if loadcase.heeft_kraan and ship.deck_data.shape[1] >= 3:
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
        if key in lading_locaties:
            if i <= loadcase.deck_tp_amount:
                pos = basis.deck_tp_positions[i - 1]
                lading_locaties[key]["LCG #[m]"] = round(pos[0], 4)
                lading_locaties[key]["TCG #[m]"] = round(pos[1], 4)
                lading_locaties[key]["VCG #[m]"] = round(pos[2], 4)
            else:
                lading_locaties[key]["LCG #[m]"] = 0.0
                lading_locaties[key]["TCG #[m]"] = 0.0
                lading_locaties[key]["VCG #[m]"] = 0.0

    return data


def schrijf_antwoordenbladen(output_dir, template, ship_objects, basis, loadcases):
    """Schrijf ingevulde antwoordenbladen per scheepstype en standaardbestand."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verwijder oude antwoordenbladen zodat alleen actuele output overblijft.
    for oud in output_dir.glob("antwoordenblad*.json"):
        oud.unlink(missing_ok=True)

    paden = {}
    for ship_name, ship in ship_objects.items():
        ingevuld = vul_antwoordenblad_in(
            template=template,
            ship_name=ship_name,
            ship=ship,
            basis=basis,
            loadcase=loadcases[ship_name],
        )
        pad = output_dir / f"antwoordenblad_{ship_name}.json"
        with open(pad, "w", encoding="utf-8") as handle:
            json.dump(ingevuld, handle, indent=4)
        paden[ship_name] = pad

    if not paden:
        return paden

    # Conventie: standaard antwoordenblad = alleskunner (of eerste beschikbare case).
    default_path = output_dir / "antwoordenblad.json"
    default_source = paden["Alleskunner"] if "Alleskunner" in paden else paden[next(iter(paden))]
    with open(default_source, "r", encoding="utf-8") as handle:
        default_data = json.load(handle)
    with open(default_path, "w", encoding="utf-8") as handle:
        json.dump(default_data, handle, indent=4)
    paden["default"] = default_path
    return paden


def voer_regressiecheck_uit(ship_objects, template):
    """Regressiecheck tegen bekende Gr98 V1.0 referentiewaarden."""
    if "Alleskunner" not in ship_objects:
        raise AssertionError("Regressiecheck kan niet: Alleskunner load case ontbreekt.")

    expected_tank1 = float(template["Lading_locaties"].get("Transition_piece_1", {}).get("LCG #[m]", 0.0))
    _ = expected_tank1  # Alleen om key-bestaan te forceren in template-structuur.

    expected_tank1_pct = 59.322
    expected_tank2_pct = 85.1747
    expected_gm = 1.0585

    alles = ship_objects["Alleskunner"].to_dict()
    delta_t1 = abs(alles["tank1_percentage"] - expected_tank1_pct)
    delta_t2 = abs(alles["tank2_percentage"] - expected_tank2_pct)
    delta_gm = abs(alles["GM"] - expected_gm)

    tol_tank = 1.5
    tol_gm = 0.15
    if delta_t1 > tol_tank or delta_t2 > tol_tank or delta_gm > tol_gm:
        raise AssertionError(
            "Regressiecheck Gr98 V1.0 faalt: "
            f"tank1 delta={delta_t1:.4f}, tank2 delta={delta_t2:.4f}, GM delta={delta_gm:.4f}."
        )

    print(
        "Regressiecheck geslaagd: "
        f"delta tank1={delta_t1:.4f}, delta tank2={delta_t2:.4f}, delta GM={delta_gm:.4f}"
    )


def parse_args():
    """Parse commandoregel-argumenten."""
    parser = argparse.ArgumentParser(description="Reken drie scheepstypen door.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Map met antwoordenblad.json en InputData_*.json.",
    )
    parser.add_argument(
        "--fallback-data-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps",
        help="Fallback map met hydrostatische en tank-CSV/JSON data.",
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="Sta expliciet fallback naar fallback-data-dir toe bij ongeldige lokale data.",
    )
    parser.add_argument(
        "--skip-regression-check",
        action="store_true",
        help="Sla regressiecheck tegen referentiewaarden over.",
    )
    parser.add_argument(
        "--tank2-movable",
        action="store_true",
        help="Modelleer tank2 als verplaatsbaar in langsscheepse richting.",
    )
    parser.add_argument(
        "--strict-residuen",
        action="store_true",
        help="Maak residuchecks hard-failing in plaats van waarschuwingen.",
    )
    return parser.parse_args()


def main():
    """Run alle load cases, schrijf outputbestanden en voer regressiecheck uit."""
    args = parse_args()
    output_dir = Path(__file__).resolve().parent / "output"

    basis = bouw_basis_scenario_config(
        data_dir=args.data_dir,
        fallback_data_dir=args.fallback_data_dir,
        allow_fallback=args.allow_fallback,
        tank2_is_movable=args.tank2_movable,
        strict_residuen=args.strict_residuen,
    )
    template = lees_antwoordenblad_template(args.data_dir)
    loadcases = bouw_loadcases(basis)

    ship_objects = {}
    fouten = {}
    for naam, loadcase in loadcases.items():
        try:
            ship_objects[naam] = maak_ship_object(loadcase, basis)
            print_result(naam, ship_objects[naam])
        except (InfeasibleLoadCaseError, DataValidatieFout) as exc:
            fouten[naam] = str(exc)
            print(f"\n{naam}")
            print(f"  Infeasible load case: {exc}")

    if not ship_objects:
        raise DataValidatieFout("Geen enkele load case kon succesvol worden doorgerekend.")

    ship_results = {naam: ship.to_dict() for naam, ship in ship_objects.items()}
    payload = build_result_payload(basis, ship_results)
    payload["errors"] = fouten
    json_path = write_results_json(output_dir, payload)
    graph_path = write_results_graph(output_dir, ship_results)
    antwoordenblad_paden = schrijf_antwoordenbladen(
        output_dir=output_dir,
        template=template,
        ship_objects=ship_objects,
        basis=basis,
        loadcases=loadcases,
    )

    if not args.skip_regression_check:
        voer_regressiecheck_uit(ship_objects, template)

    print(f"\nJSON-resultaten opgeslagen in: {json_path}")
    print(f"PNG-grafiek opgeslagen in:    {graph_path}")
    if "default" in antwoordenblad_paden:
        print(f"Antwoordenblad opgeslagen in: {antwoordenblad_paden['default']}")
        return json_path, graph_path, antwoordenblad_paden["default"]
    return json_path, graph_path, None


if __name__ == "__main__":
    try:
        main()
    except (DataValidatieFout, InfeasibleLoadCaseError, AssertionError) as exc:
        raise SystemExit(f"FOUT: {exc}")
