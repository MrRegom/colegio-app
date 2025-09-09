from django.shortcuts import render
from django.http import JsonResponse
from .models import SolicitudPerfil

def crear_solicitud(request):
    print("Vista crear_solicitud llamada. Método:", request.method)
    if request.method == 'POST':
        print("POST data:", request.POST)
        sistemas = list(request.POST.getlist('sistemas'))
        print("Sistemas recibidos:", sistemas)
        solicitud = SolicitudPerfil.objects.create(
            nombre=request.POST['firstnamefloatingInput'],
            apellidos=request.POST['lastnamefloatingInput'],
            rut=request.POST['rutfloatingInput'],
            email=request.POST['emailfloatingInput'],
            unidad=request.POST['unidadfloatingInput1'],
            estamento=request.POST['estamentofloatingInput'],
            cargo=request.POST['cargofloatingInput'],
            nombre_jefatura=request.POST['firstnameleadershipfloatingInput'],
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
    return render(request, 'apps/forms/form-perfil.html')

def lista_solicitudes(request):
    solicitudes = SolicitudPerfil.objects.all().order_by('-fecha_creacion')
    return render(request, 'apps/solicitudes_perfil/lista.html', {'solicitudes': solicitudes})
