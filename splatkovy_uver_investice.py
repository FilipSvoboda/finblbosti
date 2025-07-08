
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd

import tools

import dotmap


def uvod():
    st.title("Investovani penez pujcenych na splatkovy uver")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, kolik muze vydelat napr. investown kdyz si pujcis splatkovej uver a ten zainvestujes. Vysledky jsou v hrubym (to musis zdanit) a samozrejme neses riziko, kdyz neco selze, platis ze svyho :) Pak je tam i krivka jakej by byl vysledek, pokud si nepujcis a budes stejnou hodnotu splatky posilat primo na investown
        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.vypocitat_na_mesicu = st.number_input(
        "Vypocitat na mesicu", min_value=1, value=60
    )

    v.vychozi_kapital = tools.input_money(
        "Kolik vlozis na zacatku", default=300000
    )

    v.max_investic_mesicne = st.number_input(
        "Kolik dobrych projektu se otevre mesicne (blbe vynechas :)", 
        min_value=1, value=10
    )

    v.prumerny_urok = st.number_input(
        "Prumerny urok rocne %", min_value=1.0, value=9.4
    ) / 100

    v.investovat_do_jednoho_uveru = tools.input_money(
        "Maximalni velikost investice do jednoho uveru", default=20000
    )

    v.moje_splatka = tools.input_money(
        "Moje splatka", default=5000
    )


    return v

def vypocet(vstupy):
    df = pd.DataFrame(columns=[
        "mesic",
        "kapital_zacatek_mesice",
        "investice_nove",
        "vynosy",
        "kapital_konec_mesice",
        "hodnota_portfolia_konec_mesice",
        "celkova_hodnota",
        "splatky_zainvestovano",
        "splatky_volny_kapital"
    ])
    df = df.set_index("mesic")

    volny_kapital = vstupy.vychozi_kapital
    zainvestovano_celkem = 0

    splatky_volny_kapital = 0
    splatky_zainvestovano_celkem = 0

    mesice = range(vstupy.vypocitat_na_mesicu)
    for mesic in mesice:



        # inicializace hodnot v danem mesici na 0
        df.loc[mesic, "kapital_zacatek_mesice"] = 0
        df.loc[mesic, "investice_nove"] = 0.0
        df.loc[mesic, "vynosy"] = 0.0
        df.loc[mesic, "kapital_konec_mesice"] = 0.0
        df.loc[mesic, "hodnota_konec_mesice"] = 0.0
        df.loc[mesic, "celkova_hodnota"] = 0.0

    ## PUJCKA

        df.loc[mesic, "kapital_zacatek_mesice"] = volny_kapital

        # vypocitaji se umesicy z dosavadne bezicich investic
        # ale do kapitalu se pripise az "na konci mesice"
        zisk_tento_mesic = zainvestovano_celkem * (vstupy.prumerny_urok / 12)
        #print(f"zisk tento mesic: {zisk_tento_mesic}")

        # provede se max_investic_mesicne pokud mame vony kapital
        investic_tento_mesic = 0
        zainvestovano_tento_mesic = 0
        while volny_kapital > 500 and investic_tento_mesic < vstupy.max_investic_mesicne:
            # zainvestovat do dalsiho uveru
            castka = min(volny_kapital, vstupy.investovat_do_jednoho_uveru)
            investic_tento_mesic += 1
            zainvestovano_tento_mesic += castka
            zainvestovano_celkem += castka
            volny_kapital -= castka
        df.loc[mesic, "investice_nove"] = zainvestovano_tento_mesic


        df.loc[mesic, "vynosy"] = zisk_tento_mesic

        volny_kapital += zisk_tento_mesic
        df.loc[mesic, "kapital_konec_mesice"] = volny_kapital

        df.loc[mesic, "hodnota_portfolia_konec_mesice"] = zainvestovano_celkem
        df.loc[mesic, "celkova_hodnota"] = volny_kapital + zainvestovano_celkem


    ## VKLADAM "SPLATKY"

        df.loc[mesic, "splatky_celkova_hodnota"] = 0.0
        df.loc[mesic, "splatky_volny_kapital"] = 0.0


        # na zacatku mesice poslu splatku do volneho kapitalu
        splatky_volny_kapital += vstupy.moje_splatka


        df.loc[mesic, "splatky_volny_kapital"] = splatky_volny_kapital

        splatky_zisk_tento_mesic = splatky_zainvestovano_celkem * (vstupy.prumerny_urok / 12)
        print(f"splatky: zisk tento mesic {mesic}: {splatky_zisk_tento_mesic:.0f} z castky: {splatky_zainvestovano_celkem:.0f}")

        # provede se max_investic_mesicne pokud mame vony kapital
        investic_tento_mesic = 0
        zainvestovano_tento_mesic = 0
        while splatky_volny_kapital > 500 and investic_tento_mesic < vstupy.max_investic_mesicne:
            # zainvestovat do dalsiho uveru
            castka = min(splatky_volny_kapital, vstupy.investovat_do_jednoho_uveru)
            investic_tento_mesic += 1
            zainvestovano_tento_mesic += castka
            splatky_zainvestovano_celkem += castka
            splatky_volny_kapital -= castka

        splatky_volny_kapital += splatky_zisk_tento_mesic

        df.loc[mesic, "splatky_celkova_hodnota"] = splatky_zainvestovano_celkem + splatky_volny_kapital
        df.loc[mesic, "splatky_volny_kapital"] = splatky_volny_kapital


    return df




def vykreslit_graf(vstupy, df):
    st.write("Graf")
    fig, ax = plt.subplots(figsize=(12, 6))


    ### PUJCKA

    # První dvě křivky na první ose Y
    ax.plot(df.index, df["kapital_zacatek_mesice"], 'c', label='Volne prostredky zacatek mesice')
    ax.plot(df.index, df["celkova_hodnota"], 'g', label='Celkova hodnota portfolia')

    # Puntík na poslední hodnotu "celkova_hodnota"
    ax.plot(df.index[-1], df["celkova_hodnota"].iloc[-1], 'ro')
    ax.text(
        df.index[-1],
        df["celkova_hodnota"].iloc[-1],
        f'{df["celkova_hodnota"].iloc[-1]:.2f}',
        fontsize=9,
        va='bottom',
        ha='left'
    )


    ### SPLATKY

    ax.plot(df.index, df["splatky_celkova_hodnota"], 'r', label='Celkova hodnota portfolia kdyz investuju co splacim')




    ax.set_title('Hodnota portfolia investown')
    ax.set_xlabel('Mesic')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(tools.millions_formatter))
    ax.set_xticks(df.index)
    ax.xaxis.set_major_locator(MultipleLocator(2))

    # Druhá osa Y pro 'vynosy'
    ax2 = ax.twinx()
    ax2.set_ylim(0, df["vynosy"].max() * 1.5)
    ax2.plot(df.index, df["vynosy"], 'm', label='Vynosy tento mesic', linewidth=1)
    ax2.set_ylabel('Vynosy [Kč]', color='m')
    ax2.tick_params(axis='y', colors='m')

    # Spoj legendy obou os do jedné
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    fig.tight_layout()
    st.pyplot(fig)


def vypsat_tabulku(vstupy, df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "kapital_zacatek_mesice",
        "investice_nove",
        "vynosy",
        "kapital_konec_mesice",
        "hodnota_konec_mesice",
        "celkova_hodnota"]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)


def main():
    uvod()
    vstupy = nacist_vstupy()
    df = vypocet(vstupy)
    vykreslit_graf(vstupy, df)
    vypsat_tabulku(vstupy, df)

