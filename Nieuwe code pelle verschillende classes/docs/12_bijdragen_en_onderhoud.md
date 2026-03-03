# 12 Bijdragen en Onderhoud

## 1. Doel

Richtlijnen voor teamleden die code/documentatie wijzigen.

## 2. Wijzigingsregels

1. Wijzig nooit zomaar keynamen in antwoordenblad-output.
2. Houd interne units op `kg`, `m`, `kgm`.
3. Voeg geen stille fallback-logica toe zonder expliciete flag.
4. Laat loadcases altijd in output verschijnen.

## 3. Documentatieregels

Bij elke functionele wijziging update minimaal:

- `docs/02_cli_referentie.md` (als CLI verandert)
- `docs/03_data_contracten.md` (als input verandert)
- `docs/08_output_referentie.md` (als output verandert)
- `docs/09_foutcatalogus_en_debug.md` (als foutgedrag verandert)

## 4. Code-review checklist

1. Zijn alle nieuwe parameters gedocumenteerd?
2. Zijn units consequent?
3. Zijn foutmeldingen expliciet en nuttig?
4. Is regressie/smoke test gedraaid?
5. Zijn outputs backward-compatible waar nodig?

## 5. Versiebeheer

Aanbevolen commitstijl:

- `feat: ...`
- `fix: ...`
- `docs: ...`

## 6. Bijdragen aan docs

- Schrijf in helder Nederlands.
- Vermijd impliciete aannames.
- Voeg altijd concrete voorbeelden toe.
- Houd commandovoorbeelden direct kopieerbaar.
