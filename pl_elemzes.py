import csv
import statistics
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

MAX_SOR = 20000

def pl_statisztika(ertekek):
    adatok = [float(ertek) for ertek in ertekek]
    if not adatok:
        raise ValueError("Nincs elemezhető szám a kiválasztott oszlopban.")
    return {
        "Darabszám": len(adatok),
        "Átlag": statistics.mean(adatok),
        "Medián": statistics.median(adatok),
        "Mintaszórás": statistics.stdev(adatok) if len(adatok) > 1 else None,
        "Minimum": min(adatok),
        "Maximum": max(adatok),
    }

class PLAdathalmaz:

    def __init__(self):
        self.adatok = pd.DataFrame()
        self.szamok = pd.DataFrame()
        self.filenev = ""
        self.kodolas = ""
        self.elvalaszto = ""

    def pl_betolt(self, filenev, elvalaszto=None, tizedesjel="."):
        utvonal = Path(filenev)
        if utvonal.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Legfeljebb 10 MB méretű CSV tölthető be.")
        if elvalaszto == tizedesjel:
            raise ValueError("Az elválasztójel és a tizedesjel legyen különböző.")

        for kodolas in ("utf-8-sig", "cp1250"):
            try:
                with utvonal.open(encoding=kodolas, newline="") as file:
                    minta = file.read(8192)
                jel = elvalaszto
                if jel is None:
                    try:
                        jel = csv.Sniffer().sniff(minta, delimiters=",;\t|").delimiter
                    except csv.Error:
                        jel = ";" if tizedesjel == "," else ","
                if jel == tizedesjel:
                    raise ValueError(
                        "Az észlelt elválasztó megegyezik a tizedesjellel. "
                        "Válaszd ki kézzel a helyes elválasztót."
                    )
                adatok = pd.read_csv(
                    utvonal, sep=jel, decimal=tizedesjel,
                    encoding=kodolas, nrows=MAX_SOR + 1,
                )
                break
            except UnicodeDecodeError:
                if kodolas == "cp1250":
                    raise ValueError("A file nem UTF-8 vagy Windows-1250 kódolású.")

        if adatok.empty:
            raise ValueError("A CSV nem tartalmaz adatsorokat.")
        if len(adatok) > MAX_SOR:
            raise ValueError(f"Legfeljebb {MAX_SOR} adatsor tölthető be.")

        szamok = pd.DataFrame(index=adatok.index)
        for oszlop in adatok.columns:
            sorozat = adatok[oszlop]
            if not pd.api.types.is_numeric_dtype(sorozat):
                sorozat = sorozat.astype("string").str.strip()
                if tizedesjel == ",":
                    sorozat = sorozat.str.replace(",", ".", regex=False)
            numerikus = pd.to_numeric(sorozat, errors="coerce").astype(float)
            numerikus = numerikus.replace([np.inf, -np.inf], np.nan)
            if numerikus.notna().any():
                szamok[oszlop] = numerikus

        if szamok.empty:
            raise ValueError(
                "Nem található számmá alakítható adat. "
                "Ellenőrizd az elválasztót és a tizedesjelet."
            )
        self.adatok = adatok
        self.szamok = szamok
        self.filenev = utvonal.name
        self.kodolas = kodolas
        self.elvalaszto = jel

    def pl_tiszta(self, *oszlopok):
        if not oszlopok or any(o not in self.szamok for o in oszlopok):
            raise ValueError("Válassz ki elemezhető számoszlopot.")
        tiszta = self.szamok[list(dict.fromkeys(oszlopok))].dropna()
        if tiszta.empty:
            raise ValueError("A kiválasztott oszlopokban nincs közös érvényes adatsor.")
        return tiszta, len(self.adatok) - len(tiszta)

    def pl_leiro(self, oszlop):
        tiszta, kihagyott = self.pl_tiszta(oszlop)
        return pl_statisztika(tiszta[oszlop]), tiszta, kihagyott

    def pl_korrelacio(self, x, y):
        if x == y:
            raise ValueError("Két különböző oszlopot válassz.")
        tiszta, kihagyott = self.pl_tiszta(x, y)
        if len(tiszta) < 2:
            raise ValueError("A korrelációhoz legalább két közös adatsor kell.")
        if tiszta[x].nunique() < 2 or tiszta[y].nunique() < 2:
            raise ValueError("Állandó értékű oszlopra nem értelmezhető a korreláció.")
        return float(tiszta[x].corr(tiszta[y])), tiszta, kihagyott

    def pl_klaszterez(self, x, y, k, skalazas=True):
        if x == y:
            raise ValueError("Két különböző oszlopot válassz.")
        if not 2 <= k <= 10:
            raise ValueError("A csoportok száma 2 és 10 közötti egész legyen.")
        tiszta, kihagyott = self.pl_tiszta(x, y)
        if len(tiszta.drop_duplicates()) < k:
            raise ValueError("Nincs elegendő különböző adatpont a kért csoportszámhoz.")
        bemenet = tiszta.to_numpy()
        skala = StandardScaler() if skalazas else None
        if skala is not None:
            bemenet = skala.fit_transform(bemenet)
        modell = KMeans(n_clusters=k, random_state=42, n_init=10)
        cimkek = modell.fit_predict(bemenet)
        kozeppontok = modell.cluster_centers_
        if skala is not None:
            kozeppontok = skala.inverse_transform(kozeppontok)
        return tiszta, cimkek, kozeppontok, kihagyott
