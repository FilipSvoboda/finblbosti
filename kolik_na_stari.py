
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd


# Formátování osy Y
def millions_formatter(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.0f}M'
    elif x >= 1e3:
        return f'{x/1e3:.0f}K'
    else:
        return f'{x:.0f}'

# Funkce pro čitelné zadávání peněz
def input_money(label, default):
    raw = st.text_input(label, value=f"{default:,}".replace(",", " "), 
            help="Zadej částku s oddělovači (např. 1 000 000)"
          )
    cleaned = raw.replace(" ", "").replace(",", "")
    try:
        return int(cleaned)
    except ValueError:
        st.warning(f"Zadaná částka v poli '{label}' není číslo!")
        return 0


def vypocet():




    df = pd.DataFrame(columns=[
        "rok",                      # kolik ti je v danem roce
        "kapital_zacatek_roku",     # majetek na zacatku roku
        "kapital_vybery",           # kolik jsi v danem roce odsal
        "kapital_vklady",           # kolik jsi v danem roce vlozil
        "kapital_uroky",            # kolik v danem roce prislo na urocich
        "naklady",                  # rocni naklady (bez ohledu jestli sajes)
        "naklady_mesicni_prumer",   # mesicni naklady (bez ohledu jestli sajes)
        "rok_svorc",                # True pro rok kdy jsi prisel svorc
    ])
    df = df.set_index("rok")

    kapital = vstupni_kapital
    naklady_mesicne = naklady_na_zivot_mesicne
    jsi_svorc = False

    roky = list(range(kolik_ti_je, do_kolika_let_vypocitat + 1))
    for rok in roky:
        
        # inicializace hodnot v danem roku na 0
        df.loc[rok, "kapital_zacatek_roku"] = kapital
        df.loc[rok, "kapital_vybery"] = 0.0
        df.loc[rok, "kapital_vklady"] = 0.0
        df.loc[rok, "kapital_uroky"] = 0.0
        df.loc[rok, "naklady"] = 0.0
        df.loc[rok, "naklady_mesicni_prumer"] = 0.0
        df.loc[rok, "rok_svorc"] = False

        pracujes = (rok < v_kolika_prestanes_pracovat)
        df.loc[rok, "kapital_zacatek_roku"] = kapital


        naklady_tento_rok = 0
        uroky_kapitalu_tento_rok = 0
        for mesic in range(12):

            # naklady na zivot mesicne se zvysuji kazdy mesic o 1/12 rocni
            # inflace
            zvyseni_nakladu_mesic = naklady_mesicne * mesicni_inflace
            naklady_mesicne += zvyseni_nakladu_mesic
            naklady_tento_rok += naklady_mesicne


            if pracujes:
                # pokud pracujes, nic neberes a naopak vladas do investic
                kapital += mesicni_prispevek
                df.loc[rok, "kapital_vklady"] += mesicni_prispevek

            else:
                # uz nepracujes a zacal jsi brat z majetku
                kapital -= naklady_mesicne
                df.loc[rok, "kapital_vybery"] += naklady_mesicne


            # nechceme kreslit graf do minusu, kdyz jsi svorc vykresli se ti cara
            if kapital > 0:
                # zhodnoceni kapitalu
                uroky = kapital * mesicni_sazba_uroceni_kapitalu
                uroky_kapitalu_tento_rok += uroky
                kapital += uroky
            elif kapital <= 0:
                kapital = 0

            if kapital <= 0 and not jsi_svorc:
                jsi_svorc = True
                df.loc[rok, "rok_svorc"] = True

        df.loc[rok, "kapital_uroky"] += uroky_kapitalu_tento_rok
        df.loc[rok, "naklady"] += naklady_tento_rok
        df.loc[rok, "naklady_mesicni_prumer"] += (naklady_tento_rok / 12)

    return df


def vykreslit_graf(df):
    st.write("Graf vývoje majetku:")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["naklady_mesicni_prumer"], 'c--', 
        label='Naklady na zivot mesicne(prumer roku)'
    )

    ax.plot(df.index, df["naklady"], 'c', 
        label=f'Naklady na zivot rocne, inflace {(rocni_inflace * 100):.2f}% p.a.'
    )

    ax.plot(df.index, df["kapital_zacatek_roku"], 'b', 
        label=f'Hodnota kapitalu (start {millions_formatter(vstupni_kapital, None)})', 
        linewidth=1
    )

    ax.plot(df.index, df["kapital_uroky"], 'b--', 
        label=f'Uroky na kapitalu {(rocni_sazba_uroceni_kapitalu * 100):.2f}% p.a.', 
        linewidth=1
    )

    ax.axvline(x=v_kolika_prestanes_pracovat, color='black', linestyle='--', 
        linewidth=2, label="Konec prace"
    )

    if df["rok_svorc"].any():
        rok_svorc = df[df["rok_svorc"]].index[0]
        ax.axvline(x=rok_svorc, color='red', linestyle='--', linewidth=2, 
            label="Kapital vyčerpán"
        )

    ax.set_title('Vypocet vlastniho duchodu')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)


    ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
    #ax.set_xticks(roky)
    ax.set_xticks(df.index)
    ax.xaxis.set_major_locator(MultipleLocator(2))

    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)


def vypsat_tabulku(df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "kapital_zacatek_roku",
        "kapital_vybery",
        "kapital_vklady",
        "kapital_uroky",
        "naklady",
        "naklady_mesicni_prumer"]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)



# Aplikace

st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([1, 3, 1])  # prostřední sloupec 3× širší

with col2:
    st.title("Kolik budu mít na stáří")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, jak se bude vyvíjet hodnota tvého majetku v průběhu života na základě několika základních údajů, které zadáš.

        ### Jak to funguje

        Zadáš:
        - **kolik ti je teď let**
        - **kolik máš aktuálně investováno**
        - **kolik přidáváš do investic každý měsíc (dokud pracuješ)**
        - **v jakém věku plánuješ přestat pracovat a začít čerpat úspory**
        - **měsíční náklady na život v dnešních cenách**
        - **očekávané roční zhodnocení investic (v %)**
        - **očekávanou průměrnou roční inflaci (v %)**

        Dokud **pracuješ**, kalkulace předpokládá, že se živíš sám a z investic pouze investuješ a zhodnocuješ je. Jakmile přestaneš pracovat, začneš **čerpat peníze z investic na život**. Náklady na život rostou každý rok podle zadané inflace.

        """)




# vstupy:

    kolik_ti_je = st.number_input(
        "Aktuální věk - kolik ti ted je", min_value=1, value=30
    )

    do_kolika_let_vypocitat = st.number_input(
        "do kolika let vyhodnocovat graf", min_value=1, value=95
    )

    v_kolika_prestanes_pracovat = st.number_input(
        "V kolika letech planujes prestat pracovat a zacnes zit z majetku", 
        min_value=1, value=60
    )

    naklady_na_zivot_mesicne = input_money(
        "Naklady na mesic tveho zivota v aktualnich cenach", 50000
    )

    vstupni_kapital = input_money(
        "Tvuj aktualni kapital v investicich", 1_000_000
    )

    mesicni_prispevek = input_money(
        "Kolik mesicne prispivas do investic (dokud pracujes)", 0
    )

    rocni_inflace = st.number_input(
        "Prumerna rocni inflace (% p.a.)", value=3.5) / 100

    rocni_sazba_uroceni_kapitalu = st.number_input(
        "Rocni urok na kapitalu (% p.a.)", value=7.0) / 100


# konstanty:


    mesicni_inflace = rocni_inflace / 12
    mesicni_sazba_uroceni_kapitalu = rocni_sazba_uroceni_kapitalu / 12



    df = vypocet()

    vykreslit_graf(df)

    vypsat_tabulku(df)


