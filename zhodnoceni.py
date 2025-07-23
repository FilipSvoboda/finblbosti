import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import tools

import dotmap


def uvod():
    st.title("Jaká bude finální hodnota mojí investice?")

    st.markdown("""
        
        Tato kalkulačka ti pomůže odhadnout, jakou hodnotu bude mít Tvoje investovaná částka při zvolené výši procentuálního zhodnocení a po uplynutí Tvého investičního horizontu. 

        ### do kalkulačky zadáš:
        - Jednorázovou částku, kterou máš v plánu investovat (Počáteční investice)
        - Roční procentuální zhodnocení (Roční úroková sazba = o kolik % p.a. se úročí Tvoje investice)
        - Délku investice (Počet let, během kterých plánuješ nechat svoji investici zhodnocovat, tzn. Tvůj investiční horizont.)


        
        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.investice = tools.input_money(
        "Jednorázově vložená částka Kč", 50000
    )

    v.rocni_zhodnoceni = st.number_input(
        "Roční procentuální zhodnocení %", value=8) / 100

    v.delka_investice = st.number_input(
        "Délka investice let", min_value=1, value=10
    )

    return v


def vypocet(vstupy):

    df = pd.DataFrame(columns=[
        # kolik ti je v danem roce
        "rok",
        "hodnota_investice",
    ])
    df = df.set_index("rok")

    roky = list(
        range(1, vstupy.delka_investice + 1)
    )

    hodnota_investice = vstupy.investice
    df.loc[0, "hodnota_investice"] = hodnota_investice

    for rok in roky:
        hodnota_investice += (hodnota_investice * vstupy.rocni_zhodnoceni)
        df.loc[rok, "hodnota_investice"] = hodnota_investice
        
    return df, hodnota_investice


def popis_vysledku(hodnota):
    st.markdown(f"""

### Výsledek
**Finální hodnota Tvé investice je {tools.vypis_kc(hodnota)}**

**TIP:**

Pokud je Tvým cílem vyšší částka, potřebuješ se k ní proinvestovat jinak a podniknout jiné kroky. To je možné tak, že navýšíš jeden nebo více ze zadaných parametrů. Můžeš vložit vyšší jednorázovou částku, a/nebo zvolit jiný investiční nástroj s vyšším ročním procentuálním zhodnocením, a/nebo prodloužit svůj investiční horizont. Zkus si do kalkulačky zadat různé varianty, které pro Tebe přicházejí v úvahu a určitě najdeš nějaké řešení, které bude vyhovovat Tvým individuálním potřebám.
"""
    )

def vykreslit_graf(vstupy, df):
    st.write("Graf vývoje hodnoty investice")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["hodnota_investice"], 'k-', 
        label='Hodnota investice'
    )

    ax.set_title('Graf vývoje hodnoty investice')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(tools.millions_formatter))
    ax.set_xticks(df.index)
    if len(df) > 30:
        ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)


def vypsat_tabulku(vstupy, df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "hodnota_investice",
    ]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)


def main():
    uvod()
    vstupy = nacist_vstupy()
    df, vysledna_hodnota = vypocet(vstupy)
    popis_vysledku(vysledna_hodnota)
    vykreslit_graf(vstupy, df)
    vypsat_tabulku(vstupy, df)

