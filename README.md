# Comparador de Fundos de Investimento 📊
Este projeto é uma plataforma web de comparação de fundos de investimento e um simulador de retornos, com base em dados públicos disponibilizados pela CVM e pela ANBIMA. Ele permite ao usuário:

- Comparar a performance de fundos de investimento ao longo dos últimos 10 anos (2015–2025)

- Simular quanto teria rendido um investimento em cada fundo nesse período

- Visualizar comparações de forma prática e interativa

### Preview💻
<img src="info.png">
<img src="grafico.png">
<img src="simulador.png">
<br>

### Processamento de Dados ⚙️: <br>
Os dados brutos dos fundos foram coletados a partir do portal oficial da CVM:
🔗 https://dados.cvm.gov.br/dataset/fi-doc-inf_diario <br>

Esses dados foram organizados por ano, em pastas nomeadas como: <br>
data2015/<br>
data2016/<br>
...<br>
data2025/<br>

### O notebook pre-processing.ipynb realiza as seguintes etapas:<br>
1 - Pré-processamento por ano: <br>
- Cada pasta anual é processada individualmente, gerando pastas equivalentes com dados limpos e prontos para análise:<br>
data_processed2015/  <br>
data_processed2016/ <br>
... <br>
data_processed2025/ <br>
<br>

2 - Unificação do dataset:<br>
Após o pré-processamento, todas as pastas data_processedXXXX são mescladas em um único dataset consolidado df_geral. <br>
<br>
3 - Enriquecimento com dados da ANBIMA:<br>
Os dados da ANBIMA foram utilizados para extrair e associar os nomes dos fundos aos respectivos registros.
Fonte:<br>
🔗 https://data.anbima.com.br/datasets/fundos-175-caracteristicas-publico/detalhes



