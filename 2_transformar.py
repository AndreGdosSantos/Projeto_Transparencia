import pandas as pd
from io import StringIO
from banco import conectar

def transformar():
    print("A ligar à base de dados...")
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # ==========================================
        # 1. SILVER VIAGEM
        # ==========================================
        print("A transformar tabela raw_viagem -> silver_viagem...")
        cursor.execute("SELECT * FROM raw_viagem;")
        linhas = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(linhas, columns=colunas)
        
        # Tratamento de valores monetários
        colunas_valores = ['valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos']
        for col in colunas_valores:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            else:
                df[col] = 0.0

        df['valor_total'] = df['valor_diarias'] + df['valor_passagens'] + df['valor_outros_gastos'] - df['valor_devolucao']

        df['data_inicio'] = pd.to_datetime(df['data_inicio'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
        df['data_fim'] = pd.to_datetime(df['data_fim'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

        dt_inicio_s = pd.to_datetime(df['data_inicio'], errors='coerce')
        dt_fim_s = pd.to_datetime(df['data_fim'], errors='coerce')
        df['duracao_dias'] = (dt_fim_s - dt_inicio_s).dt.days + 1
        df['duracao_dias'] = df['duracao_dias'].fillna(1).astype(int)

        cols_silver_viagem = [
            'id_viagem', 'num_proposta', 'situacao', 'viagem_urgente', 
            'cod_orgao_superior', 'nome_orgao_superior', 'nome_viajante', 'cargo', 
            'data_inicio', 'data_fim', 'destinos', 'motivo', 
            'valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos', 
            'valor_total', 'duracao_dias'
        ]
        
        df_silver = df[cols_silver_viagem].copy()
        df_silver['nome_orgao_superior'] = df_silver['nome_orgao_superior'].fillna("Não Informado")
        df_silver = df_silver.where(pd.notnull(df_silver), None)

        cursor.execute("TRUNCATE TABLE silver_viagem CASCADE;")
        conexao.commit()

        output = StringIO()
        df_silver.to_csv(output, sep='\t', index=False, header=False, na_rep='\\N')
        output.seek(0)
        cursor.copy_expert("COPY silver_viagem FROM STDIN WITH CSV DELIMITER E'\\t' NULL '\\N'", output)
        conexao.commit()
        print("Silver Viagem concluída com sucesso!")

        # ==========================================
        # 2. SILVER PAGAMENTO
        # ==========================================
        print("A transformar tabela raw_pagamento -> silver_pagamento...")
        cursor.execute("SELECT * FROM raw_pagamento;")
        df_pag = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        
        if 'valor' in df_pag.columns:
            df_pag['valor'] = df_pag['valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_pag['valor'] = pd.to_numeric(df_pag['valor'], errors='coerce').fillna(0.0)
        else:
            df_pag['valor'] = 0.0

        cols_silver_pag = ['id_viagem', 'num_proposta', 'nome_orgao_pagador', 'nome_ug_pagadora', 'tipo_pagamento', 'valor']
        df_pag_silver = df_pag[[c for c in cols_silver_pag if c in df_pag.columns]].copy()
        if 'tipo_pagamento' in df_pag_silver.columns:
            df_pag_silver['tipo_pagamento'] = df_pag_silver['tipo_pagamento'].fillna("Não Informado")
        df_pag_silver = df_pag_silver.where(pd.notnull(df_pag_silver), None)

        cursor.execute("TRUNCATE TABLE silver_pagamento CASCADE;")
        conexao.commit()

        output = StringIO()
        df_pag_silver.to_csv(output, sep='\t', index=False, header=False, na_rep='\\N')
        output.seek(0)
        cursor.copy_expert("COPY silver_pagamento (id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora, tipo_pagamento, valor) FROM STDIN WITH CSV DELIMITER E'\\t' NULL '\\N'", output)
        conexao.commit()
        print("Silver Pagamento concluída com sucesso!")

        # ==========================================
        # 3. SILVER PASSAGEM
        # ==========================================
        print("A transformar tabela raw_passagem -> silver_passagem...")
        cursor.execute("SELECT * FROM raw_passagem;")
        df_pas = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        
        for col in ['valor_passagem', 'taxa_servico']:
            if col in df_pas.columns:
                df_pas[col] = df_pas[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_pas[col] = pd.to_numeric(df_pas[col], errors='coerce').fillna(0.0)
            else:
                df_pas[col] = 0.0

        df_pas['data_emissao'] = pd.to_datetime(df_pas['data_emissao'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

        cols_silver_pas = [
            'id_viagem', 'meio_transporte', 'pais_origem_ida', 'uf_origem_ida', 'cidade_origem_ida',
            'pais_destino_ida', 'uf_destino_ida', 'cidade_destino_ida', 'valor_passagem', 'taxa_servico', 'data_emissao'
        ]
        df_pas_silver = df_pas[[c for c in cols_silver_pas if c in df_pas.columns]].copy()
        df_pas_silver = df_pas_silver.where(pd.notnull(df_pas_silver), None)

        cursor.execute("TRUNCATE TABLE silver_passagem CASCADE;")
        conexao.commit()

        output = StringIO()
        df_pas_silver.to_csv(output, sep='\t', index=False, header=False, na_rep='\\N')
        output.seek(0)
        cursor.copy_expert(f"COPY silver_passagem ({','.join(df_pas_silver.columns)}) FROM STDIN WITH CSV DELIMITER E'\\t' NULL '\\N'", output)
        conexao.commit()
        print("Silver Passagem concluída com sucesso!")

        # ==========================================
        # 4. SILVER TRECHO
        # ==========================================
        print("A transformar tabela raw_trecho -> silver_trecho...")
        cursor.execute("SELECT * FROM raw_trecho;")
        df_tre = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        df_tre['origem_data'] = pd.to_datetime(df_tre['origem_data'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
        df_tre['destino_data'] = pd.to_datetime(df_tre['destino_data'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
        
        if 'numero_diarias' in df_tre.columns:
            df_tre['numero_diarias'] = df_tre['numero_diarias'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_tre['numero_diarias'] = pd.to_numeric(df_tre['numero_diarias'], errors='coerce').fillna(0.0)
        else:
            df_tre['numero_diarias'] = 0.0

        if 'sequencia_trecho' in df_tre.columns:
            df_tre['sequencia_trecho'] = pd.to_numeric(df_tre['sequencia_trecho'], errors='coerce').fillna(1).astype(int)
        else:
            df_tre['sequencia_trecho'] = 1

        if 'cidade_origem_ida' in df_tre.columns and 'origem_cidade' not in df_tre.columns:
            df_tre['origem_cidade'] = df_tre['cidade_origem_ida']
        if 'cidade_destino_ida' in df_tre.columns and 'destino_cidade' not in df_tre.columns:
            df_tre['destino_cidade'] = df_tre['cidade_destino_ida']

        cols_silver_tre = [
            'id_viagem', 'sequencia_trecho', 'origem_data', 'origem_uf', 'origem_cidade',
            'destino_data', 'destino_uf', 'destino_cidade', 'meio_transporte', 'numero_diarias'
        ]
        
        df_tre_silver = df_tre[[c for c in cols_silver_tre if c in df_tre.columns]].copy()
        df_tre_silver = df_tre_silver.where(pd.notnull(df_tre_silver), None)

        cursor.execute("TRUNCATE TABLE silver_trecho CASCADE;")
        conexao.commit()

        output = StringIO()
        df_tre_silver.to_csv(output, sep='\t', index=False, header=False, na_rep='\\N')
        output.seek(0)
        cursor.copy_expert(f"COPY silver_trecho ({','.join(df_tre_silver.columns)}) FROM STDIN WITH CSV DELIMITER E'\\t' NULL '\\N'", output)
        conexao.commit()
        print("Silver Trecho concluída com sucesso!")

        print("Processo da camada Silver finalizado com sucesso!")

    except Exception as e:
        print(f"Erro na transformação: {e}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    transformar()