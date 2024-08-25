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
df = pd.read_excel('/Users/matias/Documents/Programação/mapa_especies/Quadrantes.xlsx')

# Exibir as primeiras linhas do DataFrame para garantir que os dados foram lidos corretamente
print(df.head())

# Converter as coordenadas para graus decimais
df['Lat'] = df['Lat'].apply(dms_to_dd)
df['Long'] = df['Long'].apply(dms_to_dd)

import zipfile
import os

def kmz_to_kml(kmz_file, output_dir):
    with zipfile.ZipFile(kmz_file, 'r') as z:
        z.extractall(output_dir)
    # Procura o arquivo KML extraído
    for file in os.listdir(output_dir):
        if file.endswith('.kml'):
            return os.path.join(output_dir, file)
    return None

# Diretório temporário para salvar o arquivo KML extraído
output_dir = '/Users/matias/Documents/Programação/mapa_especies'

# Caminho do arquivo KMZ
kmz_file = '/Users/matias/Documents/Programação/mapa_especies/GE_SBJP_Quadrantes.kmz'

# Converte KMZ para KML
kml_file = kmz_to_kml(kmz_file, output_dir)

import folium
from folium.plugins import MarkerCluster

# Criar um mapa centrado em uma localização específica
mapa = folium.Map(location=[-7.146954, -34.952295], zoom_start=16)

folium.TileLayer('openstreetmap').add_to(mapa)

folium.LayerControl().add_to(mapa)

# Função para adicionar o conteúdo do arquivo KML ao mapa
def add_kml_to_map(kml_file, mapa):
    import xml.etree.ElementTree as ET
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
            folium.PolyLine(locations=[(coord[1], coord[0]) for coord in coords], popup=f'{name}: {description}').add_to(mapa)

# Adiciona o conteúdo do KML ao mapa
if kml_file:
    add_kml_to_map(kml_file, mapa)

# Caminho para o marcador personalizado
marcadores = {
    'carcara': '/Users/matias/Documents/Programação/mapa_especies/carcara.png',
    'quero': '/Users/matias/Documents/Programação/mapa_especies/quero.png',
    'urubu': '/Users/matias/Documents/Programação/mapa_especies/urubu.png',
    'garça': '/Users/matias/Documents/Programação/mapa_especies/garça.png',
    'raposa': '/Users/matias/Documents/Programação/mapa_especies/raposa.png',
    'tatu': '/Users/matias/Documents/Programação/mapa_especies/tatu.png'
}


# Adicionar marcadores para cada ponto geográfico na planilha
for index, row in df.iterrows():
    especie = row['Especie'].lower()  # Converter a espécie para minúsculas para evitar problemas de case-sensitive
    
    if especie in marcadores:
        # Criar um ícone personalizado para cada ponto
        icon = folium.CustomIcon(icon_image=marcadores[especie], icon_size=(20, 20))
        
        # Adicionar o marcador ao mapa
        folium.Marker([row['Lat'], row['Long']], popup=row['Quadrante'], icon=icon).add_to(mapa)

        # Debugging: Verificar as coordenadas e a espécie
        print(f"Adicionando marcador: {row['Lat']}, {row['Long']} - Espécie: {row['Especie']}")
    else:
        print(f"Espécie não reconhecida: {row['Especie']}")


# Salvar o mapa como um arquivo HTML
mapa.save('/Users/matias/Documents/Programação/mapa_especies/mapa.html')
