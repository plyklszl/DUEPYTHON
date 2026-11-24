CSV-adatfeltáró

Hallgató Polyák László  
Monogram: PL  
Tantárgy: Szkript nyelvek / Python

A feladat leírása

Tkinter ablakban működő, CSV-fájlokat elemző alkalmazás. A felhasználó kiválasztja az elemezni kívánt számoszlopokat, majd gombnyomással leíró statisztikát, eloszlásvizsgálatot,  Pearson-korrelációt vagy K-means csoportosítást indít. A Matplotlib grafikonjai az alkalmazás ablakán belül jelennek meg.

Indítás Windows alatt

Python 3.11 vagy újabb, Tkinterrel együtt telepítve szükséges. A standard Windows Python-telepítőben a Tcl/Tk összetevő legyen kiválasztva.


!!!! Az inditas.bat létrehozza a virtuális környezetet, és automatikusan telepíti a szükséges csomagokat az első indításkor, illetve ha a .venv/ mappa nem található. 

Indítás: dupla kattintás az inditas.bat filera, vagy PowerShellben:

powershell
.\.venv\Scripts\python.exe main.py

Másik gépen vagy új környezetben, a projekt mappájában:

powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py

A virtuális környezet aktiválása nem szükséges, az új gépen a requirements.txt alapján hozható létre. 

Használat

1. Kattints a **Mintaadatok** gombra, vagy nyiss meg saját CSV-fájlt.
2. Saját fájlnál megnyitás előtt válaszd ki az elválasztót és a tizedesjelet. Az automatikus elválasztó-felismerés a vesszőt, pontosvesszőt, tabulátort és függőleges vonalat vizsgálja. Magyar CSV-nél gyakori a pontosvessző és a tizedesvessző párosa. Az elválasztó és a tizedesjel legyen különböző.
3. Válassz X és szükség esetén Y számoszlopot.
4. Kattints valamelyik elemzési gombra.
5. Az "Adatok előnézete" fülön az első 100 sor látható.
6. Az "Eredmény CSV mentése" az aktuális eredményt menti. A grafikon alatti Matplotlib eszköztár nagyításra, mozgatásra és az ábra mentésére használható.

Elemzések

Funkció 		Bemenet 				Eredmény

Leíró statisztika 	X oszlop 				Darabszám, átlag, medián, mintaszórás, minimum, maximum; hisztogram
Eloszlás 		X oszlop 				Hisztogram és dobozdiagram; azonos leíró statisztika
Korreláció 		Két különböző számoszlop 		Pearson-féle r és pontdiagram
K-means 		Két különböző számoszlop, K = 2–10 	Színezett csoportok és középpontok

K-means esetén a skálázás alapértelmezetten be van kapcsolva:a StandardScaler az oszlopokat nulla átlagú, egységnyi populációs szórású skálára hozza (állandó oszlopot nullára alakít). Így az eltérő mértékegységek kevésbé torzítják a távolságokat. A középpontokat az ábrázoláshoz visszaalakítjuk, ezért a grafikonon mindig az eredeti mértékegységek szerepelnek. A K-means nem találja ki a helyes csoportszámot: a K értékét a felhasználó adja meg. A random_state=42 és n_init=10 azonos adatok és beállítások esetén reprodukálható futást tesz lehetővé. A csoportok sorszáma nem jelent sorrendet.

CSV és adattisztítás

- Az első sor az oszlopneveket tartalmazza; nincs fejléc nélküli mód.
- UTF-8 (BOM-mal is) és Windows-1250 kódolás támogatott.
- Legfeljebb 10 MB és 20 000 adatsor tölthető be, hogy a kis asztali program kezelhető maradjon.
- A számmá alakítható értéket tartalmazó oszlopok kerülnek a választólistákba.
- A hibás szöveges értékek, hiányok és végtelenek nem kerülnek a számításba.
- Két oszlopnál csak a mindkettőben érvényes sorok számítanak.
- A felület minden eredménynél jelzi a felhasznált és kihagyott sorok számát.
- Az eredeti adatokat a program nem módosítja.
- Ezreselválasztó, százalékjel és mértékegységgel írt szám automatikus tisztítása nem támogatott.
- A statisztikában mintaszórás szerepel: nevezője n−1; egyetlen értéknél nincs eredmény.
- A Pearson-korreláció állandó oszlopra nem értelmezhető; a program ezt jelzi.
- A korreláció lineáris együttjárást mér, és önmagában nem bizonyít okságot.

Export: UTF-8 BOM kódolás, pontosvessző elválasztó, tizedespont.
A statisztikai export mutató–érték táblázat, a korrelációs export egy összesítő sor.
A K-means export az elemzésben használt eredeti sorokat és egy "PL_csoport" oszlopot tartalmaz, 1-től számozott csoportokkal. Ha ilyen oszlop már létezik, az új név további alulvonást kap; az eredeti oszlop nem vész el.

Fileok

- main.py: az ablak, a vezérlők, eseménykezelés, ábrázolás és export.
- pl_elemzes.py: saját modul; CSV-betöltés, tisztítás és elemzések.
- minta_adatok.csv: saját, szintetikus mérési adatok három elkülönülő csoporttal; nem valós mérés. Néhány szándékosan hiányos/hibás értékkel szemlélteti az adattisztítást.
- requirements.txt: a telepítendő külső csomagok verziótartományai.
- inditas.bat: indítás az előkészített Windows-környezetben.
- .gitignore: a környezet, gyorsítótárak, és egyéb fileok kihagyása a Gitből.

Modulok és a használt függvények / metódusok

Bemutatandó modul: statistics

Mindhárom függvény tényleges használata a pl_statisztika() függvényben látható.

- statistics.mean(adatok): számtani átlag.
- statistics.median(adatok): rendezett adatok középső értéke; páros elemszámnál a két középső érték átlaga.
- statistics.stdev(adatok): mintaszórás, legalább két adatból.

Grafikus és további modulok

- tkinter: Tk(), StringVar(), BooleanVar(), Text(), mainloop(); ttk.Frame, Label, LabelFrame, Button, Combobox, Spinbox, Checkbutton, Notebook, Treeview, Scrollbar, Style
- tkinter.filedialog: askopenfilename(), asksaveasfilename()
- tkinter.messagebox: showerror()
- matplotlib.figure: Figure(); ábra/tengely metódusok: clear(), subplots(), add_subplot(), hist(), boxplot(), scatter(), axvline(), legend(), text(), grid(), set_title(), set_xlabel(), set_ylabel(), set_xticks(), set_axis_off(), set_axisbelow()
- matplotlib.backends.backend_tkagg: FigureCanvasTkAgg(), NavigationToolbar2Tk(); get_tk_widget(), draw_idle(), update()
- pandas: read_csv(), DataFrame(), to_numeric(), isna(), api.types.is_numeric_dtype(); DataFrame/Series metódusok: dropna(), drop_duplicates(), corr(), nunique(), head(), itertuples(), to_numpy(), to_csv(), astype(), replace(), notna(), any(), copy(), .str.strip() és .str.replace()
- numpy: flatnonzero(), inf, nan
- sklearn.cluster: KMeans(), fit_predict()
- sklearn.preprocessing: StandardScaler(), fit_transform(), inverse_transform()
- csv: Sniffer().sniff()
- pathlib: Path(), open(), stat()

Saját osztályok és függvények

PLAdathalmaz (pl_elemzes.py)

- __init__(): az üres adathalmaz létrehozása
- pl_betolt(): CSV-beolvasás és a numerikus oszlopok előállítása
- pl_tiszta(): az adott elemzéshez szükséges érvényes sorok kiválasztása
- pl_leiro(): a leíró statisztika és a tisztított adatok visszaadása
- pl_korrelacio(): Pearson-korreláció számítása, bemenetellenőrzéssel
- pl_klaszterez(): skálázás, K-means, eredmények és középpontok visszaadása

Önálló saját függvény: pl_statisztika(); a statistics modul három bemutatott függvényét használja.

PLAlkalmazas (main.py)

- __init__(): az ablak állapota és vezérlőváltozók
- pl_felulet(): a vezérlők és a Matplotlib-vászon létrehozása
- pl_szoveg(): eredményszöveg frissítése
- pl_ures_abra(): kezdő vagy tájékoztató ábra
- pl_megnyit(): fájlválasztó eseménykezelője
- pl_minta(): a mellékelt minta megnyitása
- pl_betolt(): az adatmodell és a felület összekapcsolása betöltéskor
- pl_valasztas(): oszlopváltáskor a korábbi eredmény törlése
- pl_tengely(): ábracímek, tengelyfeliratok, rácsozás
- pl_elemez(): a kért elemzés elindítása és megrajzolása
- pl_ment(): az aktuális eredmény exportálása

Az eseménykezelést a gombok command paraméterei, valamint a ComboboxSelected eseményhez rendelt pl_valasztas() valósítja meg.