from django.shortcuts import render
from django.http import JsonResponse
from .models import SolicitudPerfil
import traceback

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def crear_solicitud(request):
    print("Vista crear_solicitud llamada. Método:", request.method)
    if request.method == 'POST':
        try:
            print("POST data:", request.POST)
            sistemas = list(request.POST.getlist('sistemas'))
            print("Sistemas recibidos:", sistemas)
            solicitud = SolicitudPerfil.objects.create(
                nombre=request.POST.get('firstnamefloatingInput', ''),
                apellidos=request.POST.get('lastnamefloatingInput', ''),
                rut=request.POST.get('rutfloatingInput', ''),
                email=request.POST.get('emailfloatingInput', ''),
                unidad=request.POST.get('unidadfloatingInput1', ''),
                estamento=request.POST.get('estamentofloatingInput', ''),
                cargo=request.POST.get('cargofloatingInput', ''),
                nombre_jefatura=request.POST.get('firstnameleadershipfloatingInput', ''),
                apellidos_jefatura=request.POST.get('lastnameleadershipfloatingInput', ''),
                rut_jefatura=request.POST.get('rutleadershipfloatingInput', ''),
                email_jefatura=request.POST.get('emailleadershipfloatingInput', ''),
                unidad_jefatura=request.POST.get('unidadleadershipfloatingInput1', ''),
                estamento_jefatura=request.POST.get('estamentoleadershipfloatingInput', ''),
                cargo_jefatura=request.POST.get('cargoleadershipfloatingInput', ''),
                sistemas=sistemas,
                permisos=request.POST.get('permisos', ''),
                homologacion=request.POST.get('homologacion', ''),
            )
            print("Solicitud creada:", solicitud)
            return JsonResponse({'success': True, 'message': 'Solicitud creada correctamente'})
        except Exception as e:
            tb = traceback.format_exc()
            print("Error creando solicitud:", str(e))
            print(tb)
            return JsonResponse({'success': False, 'message': str(e), 'traceback': tb}, status=500)
    return render(request, 'apps/forms/form-perfil.html')

def lista_solicitudes(request):
    solicitudes = SolicitudPerfil.objects.all().order_by('-fecha_creacion')
    return render(request, 'apps/solicitudes_perfil/lista.html', {'solicitudes': solicitudes})
