# views.py----ROBOT------------------------
from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://www.salud-animal.com.ar/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")



#-------------------------------------------------------
from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Contacto
from django.shortcuts import render

class HomeView(TemplateView):
    template_name = 'index.html'
def tienda(request):
    return render(request, 'tienda.html')
def nosotros_view(request):
    return render(request, 'nosotros.html')
#def curriculom_view(request):
#    return render(request, 'curriculom.html')
#def contacto_view(request):
#    if request.method == 'POST':
#        nombre = request.POST.get('nombre')
#        email = request.POST.get('email')
#        consulta = request.POST.get('consulta')
#        # Guarda los datos en la base de datos
#        nuevo_contacto = Contacto(nombre=nombre, email=email, consulta=consulta)
#        nuevo_contacto.save()
#        return redirect('gracias')  # Redirige a la página de agradecimiento
#    return render(request, 'formulario.html')

def gracias_view(request):
    return render(request, 'gracias.html')