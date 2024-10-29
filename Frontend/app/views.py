from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileForm
import requests
import xml.etree.ElementTree as ET
import graphviz

api = 'http://localhost:5000'
API_RESET_DB_URL = f"{api}/reset_db"


# Create your views here.
def index(request):
    return render(request, 'homepage.html')

def cardsPizza(request):
    context = {
        'pizzas': None
    }

    response = requests.get(api + '/config/obtenerPizzas')
    if response.status_code == 200:
        context['pizzas'] = response.json().get('pizzas', [])
    else:
        context['pizzas'] = []

    return render(request, 'cardsPizza.html', context)

def verPizzaDetalle(request, id):
    context = {
        'pizza': None
    }

    response = requests.get(api + '/config/obtenerPizza/' + id)
    if response.status_code == 200:
        context['pizza'] = response.json()
    else:
        context['pizza'] = {}

    return render(request, 'detailPizza.html', context)

def configurar(request):
    return render(request, 'configurar.html', {'xml_content': None})

def visualizarXML(request):
    xml_content = ""
    graph_image_path = None

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            xml_content = file.read().decode('utf-8')

            try:
                # Parsear el contenido XML
                root = ET.fromstring(xml_content)

                # Crear un gráfico basado en el XML cargado (opcional)
                dot = graphviz.Digraph(comment="Representación del XML")
                for idx, venta in enumerate(root.findall(".//Venta")):
                    node_id = f"venta_{idx}"
                    dot.node(node_id, f"{venta.find('Fecha').text}")

                # Guardar el gráfico en un archivo temporal
                graph_image_path = "static/graph_xml"
                dot.render(graph_image_path, format="png")
                graph_image_path += ".png"

                # Convertir el contenido del XML a string para la interfaz
                xml_content = ET.tostring(root, encoding='utf8').decode('utf8')

            except ET.ParseError as e:
                messages.error(request, f"Error al parsear el XML: {e}")

    return render(request, 'configurar.html', {
        'xml_content': xml_content,
        'graph_image_path': graph_image_path
    })

def subirXML(request):
    xml_content = ""
    response_message = ""
    
    if request.method == 'POST':
        xml_content = request.POST.get('xml', '')

        try:
            # Parsear el XML de entrada
            root = ET.fromstring(xml_content)
            
            # Leer el diccionario de sentimientos
            sentimientos_positivos = [palabra.text.strip() for palabra in root.findall(".//sentimientos_positivos/palabra")]
            sentimientos_negativos = [palabra.text.strip() for palabra in root.findall(".//sentimientos_negativos/palabra")]
            
            # Leer empresas y sus servicios
            empresas = {}
            for empresa in root.findall(".//empresa"):
                nombre = empresa.find("nombre").text.strip()
                servicios = {}
                for servicio in empresa.findall(".//servicio"):
                    nombre_servicio = servicio.get("nombre").strip()
                    alias = [a.text.strip() for a in servicio.findall("alias")]
                    servicios[nombre_servicio] = alias
                empresas[nombre] = servicios

            # Crear la estructura del nuevo XML de salida
            resumen = ET.Element('Resumen')
            listado_respuestas = ET.SubElement(resumen, 'lista_respuestas')

            # Recorrer cada mensaje y clasificar palabras
            for mensaje in root.findall(".//mensaje"):
                texto_mensaje = mensaje.text.strip() if mensaje.text is not None else ""
                positivos, negativos, neutros = 0, 0, 0

                # Clasificar las palabras en el mensaje
                palabras = texto_mensaje.split()
                for palabra in palabras:
                    if palabra in sentimientos_positivos:
                        positivos += 1
                    elif palabra in sentimientos_negativos:
                        negativos += 1
                    else:
                        neutros += 1

                # Estructura XML para cada mensaje
                mensaje_element = ET.SubElement(listado_respuestas, 'mensaje')
                ET.SubElement(mensaje_element, 'texto').text = texto_mensaje
                ET.SubElement(mensaje_element, 'positivos').text = str(positivos)
                ET.SubElement(mensaje_element, 'negativos').text = str(negativos)
                ET.SubElement(mensaje_element, 'neutros').text = str(neutros)

            # Convertir el XML a string y formatearlo
            xml_string = ET.tostring(resumen, encoding='utf-8').decode('utf-8')
            response_message = "XML procesado correctamente con conteo de sentimientos."
            xml_content = xml_string

        except ET.ParseError as e:
            response_message = f"Error al parsear el XML: {e}"

    return render(request, 'configurar.html', {
        'xml_content': xml_content,
        'response_message': response_message
    })


def ayuda(request):
    return render(request, 'ayuda.html')

def datos_estudiante(request):
    return render(request, 'datos_estudiante.html')

def doc(request):
    return render(request, 'doc.html')

def reset_db(request):
    if request.method == "POST":
        try:
            # Enviar una solicitud POST a la API para restablecer la base de datos
            response = requests.post(API_RESET_DB_URL)
            
            if response.status_code == 200:
                messages.success(request, "La base de datos ha sido restablecida al estado inicial.")
            else:
                messages.error(request, "Error al restablecer la base de datos en la API.")
        
        except requests.RequestException as e:
            messages.error(request, f"Error de conexión con la API: {e}")
        
        return redirect('configurar')


