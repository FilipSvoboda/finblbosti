
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd


# Formátování osy Y
def millions_formatter(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'{x/1e3:.1f}K'
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
        "rok",
        "ve_firme",
        "osobne",
        "ve_firme_nevybiram",
        "dan_firma", 
        "dan_osoba",
        "dan_kdyz_nevybiram",
    ])
    df = df.set_index("rok")

    kumulovany_kapital = vstupni_kapital

    for rok in range(1, 10):

        fo_dani = rok < fyzicka_osoba_let_bez_dane


        # penize jsou ve firme
        # ==============================================================

        
        # zisk z uroceni celeho kapitalu
        zisk = (vstupni_kapital * ((1+urok_na_kapitalu) ** rok)) - vstupni_kapital

        # dan cca 21% ze zisku (korporatni dan)
        dan_ze_zisku = zisk * dan_firma

        # kolik zisku zbude po zdaneni
        zdaneny_zisk = zisk - dan_ze_zisku

        # to co si vybere jako osba jeste pak cely danis dani pro fo (15%)
        dan_z_fo = (vstupni_kapital + zdaneny_zisk) * dan_fyzicka_osoba


        vysledek = (vstupni_kapital + zdaneny_zisk) - dan_z_fo

        df.loc[rok, "ve_firme"] = vysledek
        df.loc[rok, "dan_firma"] = dan_ze_zisku + dan_z_fo


        # penize ve firme, ktere nevybiram
        # ==============================================================
        zisk = (kumulovany_kapital * (1+urok_na_kapitalu)) - kumulovany_kapital
        dan = zisk * dan_firma
        cisty_zisk = zisk - dan
        kumulovany_kapital += cisty_zisk

        df.loc[rok, "ve_firme_nevybiram"] = kumulovany_kapital
        df.loc[rok, "dan_kdyz_nevybiram"] = dan




        # penize zdanim, vyberu a pak jako soukroma osoba
        # ==============================================================

        # kapital napred danis dani pro fo (15%)
        dan_z_fo = vstupni_kapital * dan_fyzicka_osoba

        # zdaneny kapital ktery zbyde po zdaneni
        zdaneny_kapital = vstupni_kapital  - dan_z_fo

        # kolik to dela zisku kdyz to pak takhle urocis
        zisk = (zdaneny_kapital * ((1+urok_na_kapitalu) ** rok)) - zdaneny_kapital

        # dalsi daneni zisku z uroceni, pouze do 3 let
        if fo_dani:
            zdaneny_zisk = zisk * (1-dan_fyzicka_osoba)
            dan_zisku_fo = zisk * dan_fyzicka_osoba
        else:
            zdaneny_zisk = zisk
            dan_zisku_fo = 0

        df.loc[rok, "osobne"] = zdaneny_kapital + zdaneny_zisk
        df.loc[rok, "dan_osoba"] = dan_z_fo + dan_zisku_fo


    return df


def vykreslit_graf(df):
    st.write("Graf vývoje majetku:")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["ve_firme"], 'c--', 
        label='Zhodnocovani jako firma'
    )

    ax.plot(df.index, df["osobne"], 'b', 
        label=f'Znodnocovani jako FO', 
        linewidth=1
    )

    ax.plot(df.index, df["ve_firme_nevybiram"], 'g', 
        label=f'Znodnocovani jako jako firma, ale nebudu to vybirat', 
        linewidth=1
    )

    ax.set_title('Vypocet vyhodnosti daneni')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)


    ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
    #ax.set_xticks(roky)
    ax.set_xticks(df.index)
    #ax.xaxis.set_major_locator(MultipleLocator(2))

    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)


def vypsat_tabulku(df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "ve_firme",
        "dan_firma",
        "osobne",
        "dan_osoba",
    ]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)



# Aplikace

st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([1, 3, 1])  # prostřední sloupec 3× širší

with col2:
    st.title("Nechat penize ve firme nebo je vybrat a investovat osobne")

    st.markdown("""
        ### Ve firme

        firma uroci celej kapital, pak zdani zisk korporatni dani (21%), penize si pak vyberes a zdanis celou castku dalsi dani pro fyzicke osoby (15%)

        ### Osobne

        vyberes si penize z firmy, zdanis je dani pro fyzicke osoby (15%) a pak je urocis.. pokud je vyberes do 3 letch tak zisk danis 15%, jinak uz nicim


        """)




# vstupy:

    vstupni_kapital = input_money(
        "Tvuj aktualni kapital v investicich", 1_000_000
    )

    urok_na_kapitalu = st.number_input(
        "urok na kapitalu % p.a.", value=8) / 100

    dan_firma = st.number_input(
        "Dan kterou odvadi firma ze zisku", value=21) / 100

    dan_fyzicka_osoba = st.number_input(
        "Dan kterou odvadi fyz osoba (pokud nedrzi vice nez let bez dane)", value=15) / 100

    fyzicka_osoba_let_bez_dane = st.number_input(
        "Kolik lel je treba drzet CP aby byl bez dane pro FO", value=3
    )


# konstanty:

    df = vypocet()

    vykreslit_graf(df)

    vypsat_tabulku(df)


