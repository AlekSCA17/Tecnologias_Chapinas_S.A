from django.shortcuts import render
from .forms import FileForm
import requests
import xml.etree.ElementTree as ET
import graphviz

api = 'http://localhost:5000'

# Create your views here.
def index(request):
    return render(request, 'homepage.html')

def cardsPizza(request):
    context = {
        'pizzas': None
    }

    response = requests.get(api+'/config/obtenerPizzas')

    if response.status_code == 200:
        context['pizzas'] = response.json()['pizzas']
        return render(request, 'cardsPizza.html', context)
    else:
        context['pizzas'] = []
        return render(request, 'cardsPizza.html')

def verPizzaDetalle(request, id):
    context = {
        'pizzas': None
    }

    response = requests.get(api+'/config/obtenerPizza/'+id)
    if response.status_code == 200:
        context['pizza'] = response.json()
        return render(request, 'detailPizza.html', context)
    else:
        context['pizzas'] = []
        return render(request, 'detailPizza.html')

def configurar(request):
    xmlContent = None
    return render(request, 'configurar.html', {'xmlContent': xmlContent})

def visualizarXML(request):
    xml_content = ""
    graph_image_path = None  # Para guardar la ruta del gráfico generado

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            xml_content = file.read().decode('utf-8')

            try:
                # Parsear el contenido XML
                root = ET.fromstring(xml_content)

                # Crear un gráfico dirigido (puede ajustarse a las necesidades)
                dot = graphviz.Digraph(comment="XML Visualization")

                # Recorrer los elementos del XML y añadir nodos/arcos al gráfico
                def parse_element(element, parent=None):
                    node_id = element.tag
                    dot.node(node_id, element.tag)
                    if parent:
                        dot.edge(parent, node_id)
                    
                    # Recorrer los hijos
                    for child in element:
                        parse_element(child, node_id)

                # Iniciar el proceso desde la raíz
                parse_element(root)

                # Guardar el gráfico en un archivo temporal
                graph_image_path = "static/graph_xml"
                dot.render(graph_image_path, format="png")
                graph_image_path += ".png"  # Asegurar que termina en .png
            except ET.ParseError as e:
                print(f"Error al parsear el XML: {e}")

    return render(request, 'configurar.html', {'xml_content': xml_content, 'graph_image_path': graph_image_path})

def subirXML(request):
    xml_content = ""

    if request.method == 'POST':
        xml_content = request.POST.get('xml', '')

        cleaned_xml_content = xml_content.encode('utf-8')
        response = requests.post(api+'/config/postXML', data=cleaned_xml_content)

        if response.status_code == 200:
            print(response.json())

    return render(request, 'configurar.html', {'xml_content': xml_content, 'response': response.json().get('message', '')})

def ayuda(request):
    return render(request, 'ayuda.html')

def datos_estudiante(request):
    return render(request, 'datos_estudiante.html')

def doc(request):
    return render(request, 'doc.html')

