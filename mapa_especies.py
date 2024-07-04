import pandas as pd

# Função para converter coordenadas de graus, minutos e segundos para graus decimais
def dms_to_dd(coord):
    # Verifica se a coordenada está no formato esperado
    if '°' not in coord or '\'' not in coord or '\"' not in coord:
        raise ValueError("Formato de coordenadas inválido")

    # Divide a string de coordenadas
    degrees, rest = coord.split('°')
    minutes, rest = rest.split('\'')
    seconds, direction = rest.split('"')

    # Converte as partes em números inteiros
    degrees = int(degrees)
    minutes = int(minutes)
    seconds = float(seconds)

    # Calcula os graus decimais
    dd = degrees + minutes / 60 + seconds / 3600

    # Verifica a direção (N, S, E, W) e ajusta o sinal, se necessário
    if direction in ('S', 'W'):
        dd *= -1

    return dd

# Ler os dados da planilha Excel
df = pd.read_excel('C:\\Users\\Igor Matias\\OneDrive - ProHabitat\\Documentos\\MapaPy\\Quadrantes.xlsx')

# Exibir as primeiras linhas do DataFrame para garantir que os dados foram lidos corretamente
print(df.head())

# Converter as coordenadas para graus decimais
df['Lat'] = df['Lat'].apply(dms_to_dd)
df['Long'] = df['Long'].apply(dms_to_dd)

import folium

# Criar um mapa centrado em uma localização específica
mapa = folium.Map(location=[-7.1403808495986745, -34.958862093743384], zoom_start=10)

# Adicionar marcadores para cada ponto geográfico na planilha
for index, row in df.iterrows():
    folium.Marker([row['Lat'], row['Long']], popup=row['Quadrante']).add_to(mapa)

# Salvar o mapa como um arquivo HTML
print("Salvando o mapa como um arquivo HTML...")
mapa.save('C:\\Users\\Igor Matias\\OneDrive - ProHabitat\\Documentos\\MapaPy\\mapa.html')
print("Mapa salvo com sucesso como mapa.html")

