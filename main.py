import tkinter as tk
import numpy as np
import pandas as pd
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from pl_elemzes import PLAdathalmaz


class PLAlkalmazas:
    def __init__(self, root):
        self.root = root
        self.adathalmaz = PLAdathalmaz()
        self.eredmeny = None
        self.root.title("CSV-adatfeltáró | Polyák László")
        self.root.geometry("1180x820")
        self.root.minsize(960, 700)
        self.root.configure(background="#eef2f6")
        self.x = tk.StringVar()
        self.y = tk.StringVar()
        self.k = tk.StringVar(value="3")
        self.skalazas = tk.BooleanVar(value=True)
        self.elvalaszto = tk.StringVar(value="Automatikus")
        self.tizedesjel = tk.StringVar(value=".")
        self.statusz = tk.StringVar(value="Tölts be egy CSV-t, vagy nyisd meg a mintaadatokat.")
        self.pl_felulet()

    def pl_felulet(self):
        stilus = ttk.Style()
        stilus.theme_use("clam")
        stilus.configure("TFrame", background="#eef2f6")
        stilus.configure("TLabel", background="#eef2f6", font=("Segoe UI", 10))
        stilus.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))
        stilus.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#17324d")
        stilus.configure("TLabelframe", background="#eef2f6")
        stilus.configure("TLabelframe.Label", background="#eef2f6", font=("Segoe UI", 10, "bold"))

        keret = ttk.Frame(self.root, padding=16)
        keret.pack(fill="both", expand=True)
        ttk.Label(keret, text="CSV-adatfeltáró", style="Title.TLabel").pack(anchor="w")
        ttk.Label(keret, text="Leíró statisztika · Eloszlások · Korreláció · K-means").pack(anchor="w", pady=(0, 12))

        betoltes = ttk.Frame(keret)
        betoltes.pack(fill="x")
        ttk.Button(betoltes, text="CSV megnyitása", command=self.pl_megnyit).pack(side="left")
        ttk.Button(betoltes, text="Mintaadatok", command=self.pl_minta).pack(side="left", padx=6)
        ttk.Label(betoltes, text="Elválasztó:").pack(side="left", padx=(12, 4))
        ttk.Combobox(betoltes, textvariable=self.elvalaszto, state="readonly", width=13,
                     values=["Automatikus", "Pontosvessző", "Vessző", "Tabulátor", "Függőleges vonal"]).pack(side="left")
        ttk.Label(betoltes, text="Tizedesjel:").pack(side="left", padx=(12, 4))
        ttk.Combobox(betoltes, textvariable=self.tizedesjel, state="readonly",
                     values=[".", ","], width=3).pack(side="left")

        beallitas = ttk.LabelFrame(keret, text="Elemzés beállításai", padding=10)
        beallitas.pack(fill="x", pady=10)
        ttk.Label(beallitas, text="X / vizsgált oszlop:").grid(row=0, column=0, sticky="w")
        self.x_valaszto = ttk.Combobox(beallitas, textvariable=self.x, state="readonly", width=22)
        self.x_valaszto.grid(row=0, column=1, padx=(6, 18))
        ttk.Label(beallitas, text="Y oszlop:").grid(row=0, column=2)
        self.y_valaszto = ttk.Combobox(beallitas, textvariable=self.y, state="readonly", width=22)
        self.y_valaszto.grid(row=0, column=3, padx=(6, 18))
        ttk.Label(beallitas, text="K:").grid(row=0, column=4)
        ttk.Spinbox(beallitas, from_=2, to=10, textvariable=self.k, width=4).grid(row=0, column=5, padx=6)
        ttk.Checkbutton(beallitas, text="Skálázás", variable=self.skalazas).grid(row=0, column=6)
        for valaszto in (self.x_valaszto, self.y_valaszto):
            valaszto.bind("<<ComboboxSelected>>", self.pl_valasztas)

        gombok = ttk.Frame(keret)
        gombok.pack(fill="x", pady=(0, 10))
        self.elemzo_gombok = []
        for felirat, muvelet in [
            ("Leíró statisztika", "statisztika"), ("Eloszlás", "eloszlas"),
            ("Korreláció", "korrelacio"), ("K-means", "kmeans"),
        ]:
            gomb = ttk.Button(gombok, text=felirat, state="disabled",
                              command=lambda nev=muvelet: self.pl_elemez(nev))
            gomb.pack(side="left", padx=(0, 6))
            self.elemzo_gombok.append(gomb)
        self.mentes_gomb = ttk.Button(gombok, text="Eredmény CSV mentése",
                                      state="disabled", command=self.pl_ment)
        self.mentes_gomb.pack(side="right")

        notebook = ttk.Notebook(keret)
        notebook.pack(fill="both", expand=True)
        grafikon_lap = ttk.Frame(notebook)
        adat_lap = ttk.Frame(notebook, padding=8)
        notebook.add(grafikon_lap, text="  Grafikon és eredmények  ")
        notebook.add(adat_lap, text="  Adatok előnézete  ")
        self.figure = Figure(figsize=(8, 4), dpi=100, layout="constrained", facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.figure, master=grafikon_lap)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, grafikon_lap, pack_toolbar=False)
        self.toolbar.pack(fill="x")
        self.szoveg = tk.Text(grafikon_lap, height=6, wrap="word", font=("Consolas", 10),
                              background="#f8fafc", foreground="#17324d", relief="flat", padx=12, pady=8)
        self.szoveg.pack(fill="x")
        self.szoveg.configure(state="disabled")

        ttk.Label(adat_lap, text="Az első 100 sor látható. Az elemzés a teljes betöltött adathalmazon fut.").pack(anchor="w", pady=(0, 8))
        tabla_keret = ttk.Frame(adat_lap)
        tabla_keret.pack(fill="both", expand=True)
        tabla_keret.rowconfigure(0, weight=1)
        tabla_keret.columnconfigure(0, weight=1)
        self.tabla = ttk.Treeview(tabla_keret, show="headings")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(tabla_keret, orient="vertical", command=self.tabla.yview)
        x_scroll = ttk.Scrollbar(tabla_keret, orient="horizontal", command=self.tabla.xview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.tabla.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        ttk.Label(keret, textvariable=self.statusz, wraplength=1100).pack(fill="x", pady=(8, 0))
        self.pl_ures_abra("Tölts be egy CSV-fájlt az elemzéshez")
        self.pl_szoveg("A kezdéshez kattints a Mintaadatok gombra.\nA statisztika és az eloszlás az X oszlopot; a korreláció és a K-means az X és Y oszlopot használja.")

    def pl_szoveg(self, szoveg):
        self.szoveg.configure(state="normal")
        self.szoveg.delete("1.0", "end")
        self.szoveg.insert("1.0", szoveg)
        self.szoveg.configure(state="disabled")

    def pl_ures_abra(self, felirat):
        self.figure.clear()
        ax = self.figure.add_subplot()
        ax.text(0.5, 0.5, felirat, ha="center", va="center", fontsize=16, color="#52677d", wrap=True)
        ax.set_axis_off()
        self.toolbar.update()
        self.canvas.draw_idle()

    def pl_megnyit(self):
        filenev = filedialog.askopenfilename(parent=self.root, title="CSV kiválasztása",
                                             filetypes=[("CSV-fájlok", "*.csv"), ("Minden fájl", "*.*")])
        if filenev:
            jelek = {"Automatikus": None, "Pontosvessző": ";", "Vessző": ",", "Tabulátor": "\t", "Függőleges vonal": "|"}
            self.pl_betolt(filenev, jelek[self.elvalaszto.get()], self.tizedesjel.get())

    def pl_minta(self):
        self.pl_betolt(Path(__file__).parent / "minta_adatok.csv", ";", ".")

    def pl_betolt(self, filenev, elvalaszto, tizedesjel):
        try:
            self.adathalmaz.pl_betolt(filenev, elvalaszto, tizedesjel)
        except (OSError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as hiba:
            messagebox.showerror("Betöltési hiba", str(hiba), parent=self.root)
            return
        oszlopok = list(self.adathalmaz.szamok.columns)
        self.x_valaszto["values"] = oszlopok
        self.y_valaszto["values"] = oszlopok
        self.x.set(oszlopok[0])
        self.y.set(oszlopok[1] if len(oszlopok) > 1 else oszlopok[0])
        for gomb in self.elemzo_gombok:
            gomb.configure(state="normal")
        for gomb in self.elemzo_gombok[2:]:
            gomb.configure(state="normal" if len(oszlopok) > 1 else "disabled")
        self.tabla.delete(*self.tabla.get_children())
        azonosito = [str(i) for i in range(len(self.adathalmaz.adatok.columns))]
        self.tabla["columns"] = azonosito
        for az, nev in zip(azonosito, self.adathalmaz.adatok.columns):
            self.tabla.heading(az, text=nev)
            self.tabla.column(az, width=140, minwidth=90, stretch=False)
        for sor in self.adathalmaz.adatok.head(100).itertuples(index=False, name=None):
            self.tabla.insert("", "end", values=["" if pd.isna(v) else str(v) for v in sor])
        self.pl_elemez("statisztika")

    def pl_valasztas(self, event=None):
        self.eredmeny = None
        self.mentes_gomb.configure(state="disabled")
        self.pl_ures_abra("Válassz elemzést a fenti gombokkal")
        self.pl_szoveg(f"Kiválasztva: X = {self.x.get()}, Y = {self.y.get()}")
        self.statusz.set("Az új oszlopok elemzéséhez kattints egy funkciógombra.")

    def pl_tengely(self, ax, cim, x, y="Gyakoriság"):
        ax.set_title(cim, fontsize=13, pad=12)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(alpha=0.18)
        ax.set_axisbelow(True)

    def pl_elemez(self, muvelet):
        x, y = self.x.get(), self.y.get()
        self.eredmeny = None
        self.mentes_gomb.configure(state="disabled")
        try:
            if muvelet in ("statisztika", "eloszlas"):
                stat, tiszta, kihagyott = self.adathalmaz.pl_leiro(x)
                eredmeny = pd.DataFrame(list(stat.items()), columns=["Mutató", "Érték"])
            elif muvelet == "korrelacio":
                korrelacio, tiszta, kihagyott = self.adathalmaz.pl_korrelacio(x, y)
                eredmeny = pd.DataFrame({"X": [x], "Y": [y], "Pearson_r": [korrelacio], "Darabszám": [len(tiszta)], "Kihagyott": [kihagyott]})
            else:
                try:
                    k = int(self.k.get())
                except ValueError:
                    raise ValueError("A K mezőbe 2 és 10 közötti egész számot írj.")
                tiszta, cimkek, kozeppontok, kihagyott = self.adathalmaz.pl_klaszterez(x, y, k, self.skalazas.get())
                eredmeny = self.adathalmaz.adatok.loc[tiszta.index].copy()
                uj_oszlop = "PL_csoport"
                while uj_oszlop in eredmeny.columns:
                    uj_oszlop += "_"
                eredmeny[uj_oszlop] = cimkek + 1

            self.figure.clear()
            if muvelet == "eloszlas":
                ax, box = self.figure.subplots(1, 2)
            else:
                ax = self.figure.add_subplot()
            if muvelet in ("statisztika", "eloszlas"):
                ax.hist(tiszta[x], bins="auto", color="#327bba", edgecolor="white", alpha=0.9)
                ax.axvline(stat["Átlag"], color="#d97706", linewidth=2, label="Átlag")
                ax.axvline(stat["Medián"], color="#15803d", linestyle="--", linewidth=2, label="Medián")
                ax.legend()
                self.pl_tengely(ax, "Értékek eloszlása", x)
                if muvelet == "eloszlas":
                    box.boxplot(tiszta[x].to_numpy(), patch_artist=True, boxprops={"facecolor": "#93c5fd"})
                    box.set_xticks([1], [x])
                    box.set_title("Dobozdiagram")
                    box.set_ylabel(x)
                    box.grid(axis="y", alpha=0.18)
                szoveg = "   |   ".join(f"{nev}: {'nem értelmezhető' if ertek is None else f'{ertek:.6g}'}" for nev, ertek in stat.items())
                szoveg += "\nA mintaszórás n−1 nevezővel készül; egyetlen adatnál nem értelmezhető."
                if muvelet == "eloszlas":
                    szoveg += "\nA dobozon kívüli jelölések lehetséges kiugró értékek, nem automatikusan hibás adatok."
            elif muvelet == "korrelacio":
                ax.scatter(tiszta[x], tiszta[y], color="#327bba", alpha=0.7, s=28)
                self.pl_tengely(ax, f"Pearson-korreláció: r = {korrelacio:.4f}", x, y)
                szoveg = f"Pearson r = {korrelacio:.6f}\nAz r a lineáris együttjárás irányát és erősségét mutatja (−1 és +1 között).\nA korreláció önmagában nem bizonyít ok-okozati kapcsolatot."
            else:
                szinek = ["#327bba", "#e58b2a", "#22a080", "#a166b7", "#d95b6b", "#8b6f47", "#d667a7", "#6b7280", "#969c25", "#27a2b7"]
                csoportok = []
                for i in range(k):
                    csoport = tiszta.iloc[np.flatnonzero(cimkek == i)]
                    ax.scatter(csoport[x], csoport[y], color=szinek[i], alpha=0.75, s=28, label=f"{i + 1}. csoport ({len(csoport)})")
                    csoportok.append(f"{i + 1}. csoport: {len(csoport)} pont")
                ax.scatter(kozeppontok[:, 0], kozeppontok[:, 1], marker="X", s=160, color="#172b44", edgecolors="white", label="Középpontok")
                ax.legend(fontsize=8)
                self.pl_tengely(ax, f"K-means · {k} csoport", x, y)
                szoveg = "   |   ".join(csoportok)
                szoveg += f"\nSkálázás: {'bekapcsolva' if self.skalazas.get() else 'kikapcsolva'}. Az ábra az eredeti mértékegységeket mutatja."
                szoveg += "\nA csoportszámot te adod meg; a csoportszámok címkék, nem minősítések."
            self.eredmeny = eredmeny
            self.mentes_gomb.configure(state="normal")
            self.pl_szoveg(szoveg + f"\nFelhasznált sorok: {len(tiszta)}. Kihagyott (hiányzó, nem számszerű vagy végtelen adat): {kihagyott}.")
            self.toolbar.update()
            self.canvas.draw_idle()
            self.statusz.set(f"{self.adathalmaz.filenev} | {len(self.adathalmaz.adatok)} sor | {len(self.adathalmaz.szamok.columns)} számoszlop | Kódolás: {self.adathalmaz.kodolas}")
        except ValueError as hiba:
            self.pl_ures_abra("Az elemzés nem végezhető el ezekkel a beállításokkal")
            self.pl_szoveg(str(hiba))
            self.statusz.set("Módosítsd a beállításokat, és indítsd újra az elemzést.")
            messagebox.showerror("Elemzési hiba", str(hiba), parent=self.root)

    def pl_ment(self):
        if self.eredmeny is None:
            return
        filenev = filedialog.asksaveasfilename(parent=self.root, title="Elemzési eredmény mentése",
                                              defaultextension=".csv", initialfile="elemzes_eredmeny.csv",
                                              filetypes=[("CSV-fájl", "*.csv")])
        if filenev:
            try:
                self.eredmeny.to_csv(filenev, sep=";", index=False, encoding="utf-8-sig")
                self.statusz.set(f"Eredmény elmentve: {filenev}")
            except OSError as hiba:
                messagebox.showerror("Mentési hiba", str(hiba), parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = PLAlkalmazas(root)
    root.mainloop()
