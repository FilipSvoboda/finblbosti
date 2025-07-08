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

def vypocet(start_month, initial_capital, monthly_contribution, ema_power):
    df = pd.read_csv('S&P 500 Historical Data.csv', thousands=',')
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df['Change %'] = df['Change %'].str.replace('%', '').astype(float)
    df = df.sort_values('Date').reset_index(drop=True)
    df['Close'] = df['Price']

    df['EMA'] = df['Close'].ewm(span=5, adjust=False).mean()

    start_date = pd.to_datetime(start_month)
    df = df[df['Date'] >= start_date].copy()
    df.reset_index(drop=True, inplace=True)

    #dca_units = 0
    #dca_adj_units = 0
    #lump_sum_units = 0
    result = []

    jednorazove_sharu = 0
    jednorazove_hodnota = 0

    dca_sharu = 0
    dca_hodnota = 0

    dca_ex_sharu = 0
    dca_ex_hodnota = 0


    if not df.empty:
        initial_price = df.loc[0, 'Close']
        jednorazove_sharu = initial_capital / initial_price

    for i, row in df.iterrows():
        price = row['Close']
        ema = row['EMA']
        date = row['Date']

        # jednorazova investice na zacatku
        jednorazova_hodota = jednorazove_sharu * price


        # cista DCA
        dca_sharu += monthly_contribution / price
        dca_hodnota = dca_sharu * price

        # DCA s promenlivym vkladem

        factor = (ema / price) ** ema_power
        adj_contrib = monthly_contribution * factor

        dca_ex_sharu += adj_contrib / price
        dca_ex_hodnota = dca_ex_sharu * price

        result.append({
            'Date': date,
            'S&P 500': price,
            'DCA': dca_hodnota,
            'DCA EMA': dca_ex_hodnota,
            'Lump sum': jednorazove_hodnota,
            'Vklad DCA': monthly_contribution,
            'Vklad DCA EMA': adj_contrib,
            'EMA factor': factor,
            'EMA': ema,
        })

    return pd.DataFrame(result)

def vykreslit_graf(df):
    st.write("Graf vývoje majetku:")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df['Date'], df['DCA'], label='DCA')
    ax1.plot(df['Date'], df['DCA EMA'], label='DCA podle EMA', linestyle='--')
    ax1.plot(df['Date'], df['Lump sum'], label='Jednorázová investice')

    ax1.set_ylabel('Hodnota investice [USD]')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))

    ax2 = ax1.twinx()
    ax2.plot(df['Date'], df['S&P 500'], label='S&P 500 index', color='black')
    ax2.plot(df['Date'], df['EMA'], label='EMA', color="gray")
    ax2.set_ylabel('Hodnota S&P 500')

    fig.suptitle('Vývoj hodnoty investic a indexu')
    ax1.set_xlabel('Datum')
    ax1.grid(True, linestyle='--', alpha=0.5)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    fig.tight_layout()
    st.pyplot(fig)

def vykreslit_tabulku(df):
    st.write("\nTabulka vývoje hodnot a vkladů:")
    df_formatted = df[['Date', 'Vklad DCA', 'Vklad DCA EMA', 'DCA', 'DCA EMA', 'Lump sum']].copy()
    df_formatted['Date'] = df_formatted['Date'].dt.strftime('%Y-%m')
    df_formatted = df_formatted.rename(columns={
        'Date': 'Datum',
        'Vklad DCA': 'Vklad DCA',
        'Vklad DCA EMA': 'Vklad DCA EMA',
        'DCA': 'Hodnota DCA',
        'DCA EMA': 'Hodnota DCA EMA',
        'Lump sum': 'Hodnota jednorázově'
    })
    st.dataframe(df_formatted, use_container_width=True)

def vypis_vliv_na_prispevek(df):
    min_factor = df['EMA factor'].min()
    max_factor = df['EMA factor'].max()
    st.markdown(f"""
    ### Vliv zesílení EMA
    - Nejvyšší navýšení měsíčního vkladu: **{max_factor:.2f}×**
    - Největší snížení měsíčního vkladu: **{min_factor:.2f}×**
    - Znamená to, že pokud je index výrazně **pod EMA**, vkládáš až o **{(max_factor - 1)*100:.0f}% více**.
    - A pokud je vysoko nad EMA, můžeš vkládat i o **{(1 - min_factor)*100:.0f}% méně**.
    """)


# Aplikace
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.title("Kolik budu mít na stáří")
    st.markdown("""
    Tato kalkulačka simuluje tři přístupy k investování do indexu S&P 500:
    - 📈 **DCA** – pravidelné měsíční vklady
    - ⚖️ **DCA upravené o EMA** – přispíváš více, když je index levný
    - 💰 **Jednorázová investice** – vše vloženo na začátku
    """)

    start_month = st.date_input("Od kterého měsíce začít investovat", pd.to_datetime("2000-01-01"))
    initial_capital = input_money("Počáteční kapitál (jednorázová investice)", 1_000_000)
    monthly_contribution = input_money("Měsíční příspěvek (DCA)", 10000)
    ema_power = st.slider("Zesílení EMA vlivu (exponent)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

    df = vypocet(start_month, initial_capital, monthly_contribution, ema_power)
    vykreslit_graf(df)
    vypis_vliv_na_prispevek(df)
    vykreslit_tabulku(df)

