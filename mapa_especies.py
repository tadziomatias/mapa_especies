import pandas as pd
import zipfile
import os
import folium
from folium.plugins import MarkerCluster
import xml.etree.ElementTree as ET

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
df = pd.read_excel('/Users/matias/Documents/Programação/mapa_especies/Quadrantes.xlsx')

# Exibir as primeiras linhas do DataFrame para garantir que os dados foram lidos corretamente
print(df.head())

# Converter as coordenadas para graus decimais
df['Lat'] = df['Lat'].apply(dms_to_dd)
df['Long'] = df['Long'].apply(dms_to_dd)

# Função para extrair KMZ e converter para KML
def kmz_to_kml(kmz_file, output_dir):
    with zipfile.ZipFile(kmz_file, 'r') as z:
        z.extractall(output_dir)
    for file in os.listdir(output_dir):
        if file.endswith('.kml'):
            return os.path.join(output_dir, file)
    return None

# Diretório temporário para salvar o arquivo KML extraído
output_dir = '/Users/matias/Documents/Programação/mapa_especies/kmz'

# Caminhos dos arquivos KMZ
kmz_files = [
    '/Users/matias/Documents/Programação/mapa_especies/kmz/quadrantes.kmz',
    '/Users/matias/Documents/Programação/mapa_especies/kmz/operacional.kmz',
    '/Users/matias/Documents/Programação/mapa_especies/kmz/patrimonial.kmz',
    '/Users/matias/Documents/Programação/mapa_especies/kmz/patio.kmz',
    '/Users/matias/Documents/Programação/mapa_especies/kmz/ppd.kmz'
]

# Função para adicionar o conteúdo do arquivo KML ao mapa
def add_kml_to_map(kml_file, mapa, line_color='red'):
    tree = ET.parse(kml_file)
    root = tree.getroot()
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    for placemark in root.findall('.//kml:Placemark', namespace):
        name = placemark.find('kml:name', namespace).text if placemark.find('kml:name', namespace) is not None else 'No Name'
        description = placemark.find('kml:description', namespace).text if placemark.find('kml:description', namespace) is not None else 'No Description'
        coordinates = placemark.find('.//kml:coordinates', namespace).text.strip()
        coords = [tuple(map(float, coord.split(','))) for coord in coordinates.split()]
        if len(coords) == 1:  # ponto
            folium.Marker(location=[coords[0][1], coords[0][0]], popup=f'{name}: {description}').add_to(mapa)
        else:  # linha ou polígono
            folium.PolyLine(locations=[(coord[1], coord[0]) for coord in coords], popup=f'{name}: {description}', color=line_color, weight=1, opacity=1.0).add_to(mapa)

# Criar um mapa centrado em uma localização específica
mapa = folium.Map(location=[-7.146954, -34.952295], zoom_start=16)

# Adicionar uma camada de azulejos personalizada com opacidade ajustável
folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='OpenStreetMap',
    opacity=0.0,  # Ajuste a opacidade aqui
).add_to(mapa)
folium.LayerControl().add_to(mapa)

# Adiciona o conteúdo de cada arquivo KML ao mapa
for kmz_file in kmz_files:
    kml_file = kmz_to_kml(kmz_file, output_dir)
    if kml_file:
        add_kml_to_map(kml_file, mapa, line_color='black')

# Caminho para o marcador personalizado
marcadores = {
    'carcara': '/Users/matias/Documents/Programação/mapa_especies/png/carcara.png',
    'quero': '/Users/matias/Documents/Programação/mapa_especies/png/quero.png',
    'garça': '/Users/matias/Documents/Programação/mapa_especies/png/garça.png',
    'urubu': '/Users/matias/Documents/Programação/mapa_especies/png/urubu.png',
    'tatu': '/Users/matias/Documents/Programação/mapa_especies/png/tatu.png',
    'raposa': '/Users/matias/Documents/Programação/mapa_especies/png/raposa.png'
}

# Adicionar marcadores para cada ponto geográfico na planilha
for index, row in df.iterrows():
    especie = row['Especie'].lower()
    if especie in marcadores:
        icon = folium.CustomIcon(icon_image=marcadores[especie], icon_size=(20, 20))
        folium.Marker([row['Lat'], row['Long']], popup=row['Quadrante'], icon=icon).add_to(mapa)
        print(f"Adicionando marcador: {row['Lat']}, {row['Long']} - Espécie: {row['Especie']}")
    else:
        print(f"Espécie não reconhecida: {row['Especie']}")

# Salvar o mapa como um arquivo HTML
mapa.save('/Users/matias/Documents/Programação/mapa_especies/mapa.html')
