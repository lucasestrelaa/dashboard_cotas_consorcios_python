import pandas as pd

# 1. Carregar planilha
df = pd.read_excel('data_to_set_db_1.xlsx')

# 2. Dicionário de segmentos mapeados
segmentos = {
    1: 'Imóveis',
    2: 'Veículos Pesados',
    3: 'Veículos Leves',
    4: 'Motocicletas',
    5: 'Outros Serviços',
    6: 'Serviços'
}

# 3. Mapear administradoras únicas para IDs numéricos
admin_unicas = sorted(df['Administradora'].dropna().unique())
admin_map = {nome: idx + 1 for idx, nome in enumerate(admin_unicas)}

# 4. Despivotar colunas de datas em linhas (Unpivot / Melt)
colunas_datas = [c for c in df.columns if c not in ['Segmento', 'Administradora']]
df_long = pd.melt(
    df,
    id_vars=['Segmento', 'Administradora'],
    value_vars=colunas_datas,
    var_name='data_referencia',
    value_name='quantidade'
)

df_long['data_referencia'] = pd.to_datetime(df_long['data_referencia']).dt.strftime('%Y-%m-%d')
df_long['admin_id'] = df_long['Administradora'].map(admin_map)

# 5. Exportar comandos SQL para arquivo
with open('insert_script.sql', 'w', encoding='utf-8') as f:
    # Inserts de Segmentos
    for seg_id, seg_nome in segmentos.items():
        f.write(f"INSERT INTO segmentos (id_segmento, nome_segmento) VALUES ({seg_id}, '{seg_nome}');\n")
    
    # Inserts de Administradoras
    for nome_admin, admin_id in admin_map.items():
        nome_escapado = nome_admin.replace("'", "''")
        f.write(f"INSERT INTO administradoras (id_administradora, nome_administradora) VALUES ({admin_id}, '{nome_escapado}');\n")
    
    # Inserts de Vendas/Registros
    for _, row in df_long.iterrows():
        f.write(
            f"INSERT INTO vendas_consorcio (id_segmento, id_administradora, data_referencia, quantidade) "
            f"VALUES ({row['Segmento']}, {row['admin_id']}, '{row['data_referencia']}', {row['quantidade']});\n"
        )

print("Arquivo 'insert_script.sql' gerado com sucesso!")