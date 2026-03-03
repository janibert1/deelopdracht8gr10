# 12 Bijdragen en Onderhoud

## 1. Doel

Richtlijnen voor teamleden die code of documentatie aanpassen, met focus op stabiliteit, traceerbaarheid en voorspelbare output.

## 2. Basisprincipes voor wijzigingen

1. Verander geen antwoordenblad-keys zonder expliciete impactanalyse.
2. Houd interne units op `kg`, `m`, `kgm`.
3. Voeg geen impliciete fallbacklogica toe zonder expliciete flag.
4. Laat alle loadcases altijd terugkomen in outputstructuur.
5. Behoud duidelijke foutmeldingen; vermijd stille defaultgedragingen.

## 3. Verplichte documentatie-updates bij codewijzigingen

Werk minimaal deze pagina's bij wanneer relevant:

- `docs/02_cli_referentie.md` bij CLI-verandering;
- `docs/03_data_contracten.md` bij inputcontractwijziging;
- `docs/08_output_referentie.md` bij outputstructuurwijziging;
- `docs/09_foutcatalogus_en_debug.md` bij foutgedragwijziging;
- `docs/11_assignment_traceability_mt1466.md` bij functionele dekkingwijziging.

## 4. Aanbevolen ontwikkelworkflow

1. Maak wijziging klein en gericht.
2. Run minimaal smoke test.
3. Run regressiecheck bij modelwijziging.
4. Controleer output op backwards compatibility.
5. Update documentatie in dezelfde commitreeks.

## 5. Code review checklist

1. Zijn nieuwe parameters volledig gedocumenteerd?
2. Zijn units en conversies consequent toegepast?
3. Is foutafhandeling expliciet en nuttig voor eindgebruiker?
4. Zijn regressie/smoke checks uitgevoerd en gerapporteerd?
5. Blijft outputstructuur stabiel voor bestaande tooling?

## 6. Commit- en wijzigingsstijl

Aanbevolen commitprefixen:

- `feat: ...`
- `fix: ...`
- `docs: ...`
- `refactor: ...`

Houd commitboodschappen kort maar technisch concreet.

## 7. Onderhoud van documentatiekwaliteit

Schrijfregels:

- gebruik helder Nederlands zonder impliciete aannames;
- benoem units bij alle numerieke velden;
- geef concrete commandovoorbeelden;
- maak foutscenario's oplosbaar met stap-voor-stap acties.

## 8. Releasevoorbereiding

Voor een teamrelease:

1. run smoke + regressie;
2. controleer outputartefacten;
3. update relevante docs;
4. laat een tweede teamlid output en docs reviewen.

## 9. Versiebeheer van docs

Behandel docs als onderdeel van het product, niet als bijlage. Als codegedrag verandert zonder docupdate, is de wijziging incompleet.
