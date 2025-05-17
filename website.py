import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import re
import gdown

@st.cache_data
def carregar_dados():
    # IDs dos arquivos no Google Drive
    id_fundos = "1VmQ3aCa0IHVO_2KAaOlPeWqwP0W8vPDu"
    id_info = "1BnHQTZ-SzNdouH6reoas6QW9nhZ5lpfk"

    # URLs de download direto
    url_fundos = f"https://drive.google.com/uc?id={id_fundos}"
    url_info = f"https://drive.google.com/uc?id={id_info}"

    # Nomes dos arquivos locais
    output_fundos = "fundos_unificados.csv"
    output_info = "fundos_info.csv"

    # Baixa os arquivos do Google Drive
    gdown.download(url_fundos, output_fundos, quiet=False)
    gdown.download(url_info, output_info, quiet=False)

    # Lê os CSVs
    df_fundos = pd.read_csv(output_fundos, parse_dates=["DT_COMPTC"])
    df_info = pd.read_csv(output_info)

    return df_fundos, df_info

with st.spinner("Carregando o aplicativo..."):
    df, df_info = carregar_dados()

# Criar lista de opções: Nome Comercial + CNPJ formatado
opcoes = df_info[["Nome Comercial", "CNPJ da Classe"]].dropna()
opcoes = opcoes.drop_duplicates(subset=["Nome Comercial"])
opcoes["input_opcao"] = opcoes["Nome Comercial"]
lista_opcoes = [""] + sorted(opcoes["input_opcao"].tolist())  # Adiciona uma opção vazia no topo

def extrair_cnpj(valor):
    cnpj_regex = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
    encontrado = cnpj_regex.findall(valor)
    return encontrado[0] if encontrado else None

def processar_entrada(input_text):
    cnpj_direto = extrair_cnpj(input_text)
    if cnpj_direto:
        return cnpj_direto
    nome = input_text.split(" | ")[0].strip()
    match = df_info[df_info["Nome Comercial"] == nome]
    if not match.empty:
        return match["CNPJ da Classe"].values[0]
    return None

def truncar_nome(nome, limite=50):
    return nome if len(nome) <= limite else nome[:limite-3] + "..."

st.title("Comparador de Fundos de Investimento")
st.markdown(
    """
    <p style='color:red; font-size: 0.85rem;'>
    ⚠️ Este projeto tem finalidade educacional, alguns erros e inconsistências podem ser encontrados.<br>
    ⚠️ Os dados são estáticos (de 2015 até 05/2025), e podem parar de ser atualizados a qualquer momento.
    </p>                        
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    entrada1 = st.selectbox("Fundo 1", options=lista_opcoes, index=0, placeholder="Digite nome ou CNPJ...")
    cnpj1 = processar_entrada(entrada1)
    dados1 = df[df["CNPJ_FUNDO"] == cnpj1].copy() if cnpj1 else pd.DataFrame()

with col2:
    entrada2 = st.selectbox("Fundo 2", options=lista_opcoes, index=0, placeholder="Digite nome ou CNPJ...")
    cnpj2 = processar_entrada(entrada2)
    dados2 = df[df["CNPJ_FUNDO"] == cnpj2].copy() if cnpj2 else pd.DataFrame()

# 1 - Exibição de informações dos fundos
if not dados1.empty and not dados2.empty:
    dados1.sort_values("DT_COMPTC", inplace=True)
    dados2.sort_values("DT_COMPTC", inplace=True)

    ultima1 = dados1.iloc[-1]
    ultima2 = dados2.iloc[-1]

    st.markdown("### Informações dos Fundos")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Número de Cotistas", int(ultima1["NR_COTST"]))
        st.metric("Valor Atual da Cota", f"R$ {ultima1['VL_QUOTA']:.2f}")
        st.metric("Patrimônio Líquido", f"R$ {ultima1['VL_PATRIM_LIQ']}")
    with col2:
        st.metric("Número de Cotistas", int(ultima2["NR_COTST"]))
        st.metric("Valor Atual da Cota", f"R$ {ultima2['VL_QUOTA']:.2f}")
        st.metric("Patrimônio Líquido", f"R$ {ultima2['VL_PATRIM_LIQ']}")

# 2 - Seletor de intervalo de datas
st.markdown("##### Selecione o intervalo de datas para a análise do gráfico")
data_min = pd.to_datetime("2015-01-01")
data_max = pd.to_datetime("2025-05-14")

data_inicio = st.date_input("Data Início", value=data_min, min_value=data_min, max_value=data_max)
data_fim = st.date_input("Data Fim", value=data_max, min_value=data_min, max_value=data_max)

# 3 - Gráfico
if data_inicio > data_fim:
    st.error("A data de início não pode ser maior que a data de fim.")
elif not dados1.empty and not dados2.empty:
    dados1 = dados1[(dados1["DT_COMPTC"] >= pd.Timestamp(data_inicio)) & (dados1["DT_COMPTC"] <= pd.Timestamp(data_fim))]
    dados2 = dados2[(dados2["DT_COMPTC"] >= pd.Timestamp(data_inicio)) & (dados2["DT_COMPTC"] <= pd.Timestamp(data_fim))]

    if dados1.empty or dados2.empty:
        st.warning("Não há dados suficientes no intervalo de datas selecionado para um ou ambos os fundos.")
    else:
        dados1["retorno"] = dados1["VL_QUOTA"] / dados1["VL_QUOTA"].iloc[0] - 1
        dados2["retorno"] = dados2["VL_QUOTA"] / dados2["VL_QUOTA"].iloc[0] - 1

        st.markdown("### Retorno Acumulado")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dados1["DT_COMPTC"], dados1["retorno"], label=truncar_nome(entrada1))
        ax.plot(dados2["DT_COMPTC"], dados2["retorno"], label=truncar_nome(entrada2))
        ax.set_title("Comparação de Retorno Acumulado")
        ax.set_xlabel("Data")
        ax.set_ylabel("Retorno")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=2)
        st.pyplot(fig)

if not dados1.empty and not dados2.empty:
    st.markdown("### Simulador de Aplicação")

    montante = st.number_input("Montante a ser investido (R$)", min_value=100.0, value=1000.0, step=100.0)

    data_inicio_comum = max(dados1["DT_COMPTC"].min(), dados2["DT_COMPTC"].min()).date()
    data_fim_comum = min(dados1["DT_COMPTC"].max(), dados2["DT_COMPTC"].max()).date()

    if data_inicio_comum > data_fim_comum:
        st.error("Não há intervalo comum de datas entre os fundos selecionados para simular a aplicação.")
    else:
        data_aplicacao = st.date_input(
            "Data da aplicação",
            value=data_inicio_comum,
            min_value=data_inicio_comum,
            max_value=data_fim_comum
        )

        if data_aplicacao < data_inicio_comum or data_aplicacao > data_fim_comum:
            st.warning("A data de aplicação está fora do intervalo disponível dos fundos.")
        else:
            try:
                cota_inicio1 = dados1[dados1["DT_COMPTC"] >= pd.Timestamp(data_aplicacao)].iloc[0]["VL_QUOTA"]
                cota_fim1 = dados1.iloc[-1]["VL_QUOTA"]
                valor_final1 = montante * (cota_fim1 / cota_inicio1)
                retorno1 = ((valor_final1 / montante - 1) * 100)

                cota_inicio2 = dados2[dados2["DT_COMPTC"] >= pd.Timestamp(data_aplicacao)].iloc[0]["VL_QUOTA"]
                cota_fim2 = dados2.iloc[-1]["VL_QUOTA"]
                valor_final2 = montante * (cota_fim2 / cota_inicio2)
                retorno2 = ((valor_final2 / montante - 1) * 100)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(label=f"{truncar_nome(entrada1)} - Valor Final", value=f"R$ {valor_final1:,.2f}")
                    cor1 = "green" if retorno1 > retorno2 else ""
                    st.markdown(f"<span style='color:{cor1 if cor1 else 'inherit'}; font-size:1.5em;'>Retorno: {retorno1:.2f}%</span>", unsafe_allow_html=True)

                with col2:
                    st.metric(label=f"{truncar_nome(entrada2)} - Valor Final", value=f"R$ {valor_final2:,.2f}")
                    cor2 = "green" if retorno2 > retorno1 else ""
                    st.markdown(f"<span style='color:{cor2 if cor2 else 'inherit'}; font-size:1.5em;'>Retorno: {retorno2:.2f}%</span>", unsafe_allow_html=True)

            except IndexError:
                st.error("Não foi possível encontrar cotas para a data de aplicação selecionada.")


st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
        text-align: center;
        padding: 10px 0;
        font-size: 0.85rem;
    }
    </style>
    <div class="footer">
        Created by Thierno Dia<br>
        Linkedin: <a href='https://www.linkedin.com/in/thierno-dia-256374207/' target='_blank'>https://www.linkedin.com/in/thierno-dia-256374207/</a> |
        Github: <a href='https://github.com/Thierno88' target='_blank'>https://github.com/Thierno88</a>
    </div>
    """,
    unsafe_allow_html=True
)

