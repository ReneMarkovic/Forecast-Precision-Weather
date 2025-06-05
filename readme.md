# Weather Forecast Accuracy Tracker

## Opis projekta
Projekt Weather Forecast Accuracy Tracker je namenjen spremljanju vremenskih napovedi in njihovi primerjavi z dejanskimi meritvami za tri slovenske lokacije: Koper, Ljubljana in Maribor.

**Za vsako lokacijo:**
- zajemamo vremensko napoved za naslednjih 1–14 dni (dnevna ločljivost),
- zajemamo vremensko napoved za naslednjih 1–24 ur (urno),
- spremljamo dejansko izmerjene podatke v realnem času,
- izvajamo analizo natančnosti vremenskih napovedi.

## Spremljani parametri
Na dnevni in urni ravni se analizirajo naslednji meteorološki parametri:

- Temperatura (najnižja, najvišja, povprečna)
- Relativna vlažnost
- Oblačnost
- Hitrost vetra
- Količina padavin

## Cilji

Zbrati in strukturirati vremenske napovedi ter meritve. Oceniti točnost napovedi glede na izmerjene vrednosti. Razviti metrike in vizualizacije za analizo točnosti (MAE, RMSE, vizualne primerjave). Pripraviti poročila in povzetke natančnosti po lokaciji, parametru in časovnem oknu napovedi.

## Uporabljene tehnologije
- Python: zbiranje in obdelava podatkov
- Pandas, NumPy: analiza
- Matplotlib, Plotly: vizualizacije
- APIs: vremenski podatki (npr. Open-Meteo, ARSO, Meteostat, ipd.)

## Navodila za zagon

1. Namesti odvisnosti:
   ```bash
   pip install -r requirements.txt
   ```
2. Zaženi skripto:
   ```bash
   python run_analysis.py
   ```

Skripta pridobi napovedi in trenutne podatke za Koper, Ljubljano in Maribor,
shrani rezultate v mapo `data/`, izračuna osnovne metrike (MAE, RMSE) ter
ustvari graf napovedi in dejanskih meritev v mapi `plots/`.

