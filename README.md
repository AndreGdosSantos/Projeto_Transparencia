# Projeto de Análise de Dados: Viagens a Serviço (2025)

Este projeto é um pipeline de dados desenvolvido como trabalho prático para aplicar conceitos de Engenharia e Análise de Dados utilizando Python, PostgreSQL e Jupyter Notebook, seguindo a Arquitetura Medallion.

---

## 🚀 Sobre o Projeto
O objetivo é processar os dados públicos de viagens oficiais do Portal da Transparência do Governo Federal, transformando dados brutos em informações organizadas e úteis para a tomada de decisão.

---

## 🛠️ Tecnologias Utilizadas
- **Python** (Pandas, Matplotlib, Seaborn)
- **PostgreSQL** (Base de dados relacional)
- **Jupyter Notebook** (Análise de dados e visualizações)
- **Git e GitHub** (Controlo de versão)

---

## 🏗️ Estrutura do Pipeline (Arquitetura Medallion)

1. **Camada Raw (Bruta):** Ingestão fiel dos ficheiros CSV originais, mantendo todas as colunas como texto (`VARCHAR`).
2. **Camada Silver (Limpa e Tipada):** Tratamento de dados, conversão de tipos (datas e valores monetários), criação de chaves primárias (PK), chaves estrangeiras (FK) e restrições (`CHECK`, `NOT NULL`, `UNIQUE`).
3. **Camada Gold (Analítica):** Consultas SQL agregadas e gráficos desenvolvidos no Jupyter Notebook para responder a perguntas de negócio.

---

## 📂 Organização dos Ficheiros

- `0_criar_banco.sql`: Script SQL para criar a base de dados e as tabelas das camadas Raw e Silver.
- `1_extrair.py`: Script Python para extrair os dados e povoar a camada Raw.
- `2_transformar.py`: Script Python para limpar, tipar e povoar a camada Silver.
- `3_analise.ipynb`: Notebook com as consultas, análises e gráficos da camada Gold.
- `banco.py`: Módulo de conexão com o PostgreSQL.
- `config.py`: Configurações gerais e leitura do ficheiro `.env`.
- `requirements.txt`: Lista de dependências do projeto.

---

## ⚙️ Como Executar

1. Certifica-te de que tens o PostgreSQL a correr e cria um ficheiro `.env` com as tuas credenciais (baseado no `.env.example`).
2. Executa o script `0_criar_banco.sql` no teu gestor de PostgreSQL.
3. Executa o script de extração: `python 1_extrair.py`
4. Executa o script de transformação: `python 2_transformar.py`
5. Abre o `3_analise.ipynb` no VS Code para ver os resultados e gráficos.