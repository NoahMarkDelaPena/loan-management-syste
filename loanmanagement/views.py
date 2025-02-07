import json
import mimetypes
import os
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, HttpResponse, redirect
from qrcode import *

from .forms import PersonForm, UserRegistration, CollectorForm
from .models import Person, Collector


# Create your views here.
def home(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('adminLogin')
    return render(request, "dashboard.html")


def addClient(request):
    if request.method == "POST":
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            context = {'form': form}
            return render(request, "addClient.html", context)

    persons = Person.objects.all()
    context = {'form': PersonForm(), 'persons': persons}
    return render(request, "addClient.html", context)


def deleteClient(request, id):
    item = Person.objects.get(id=id)
    item.delete()
    if item.picture.name and item.document.name:
        os.remove(os.path.join(settings.MEDIA_ROOT, item.picture.name))
        os.remove(os.path.join(settings.MEDIA_ROOT, item.document.name))
    return redirect('/adminUser/addClient')


def qrFunc(val, name):
    img = make(val)
    img_url = 'qr-' + str(name) + '.png'
    # buffer = io.BytesIO()
    img.save(settings.MEDIA_ROOT + '/qr/' + img_url)
    return img_url


def generateQR(request, id):
    person = Person.objects.get(id=id)
    img = qrFunc(person.id, person.name)
    # # qrcode = base64.b64encode(buffer.getvalue()).decode("utf-8")
    if img:
        wrapper = FileWrapper(open(settings.MEDIA_ROOT + "/qr/" + img, 'rb'))
        content_type = mimetypes.guess_type(img)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Disposition'] = "attachment; filename=%s" % img
        return response


def loanPortal(request):
    return render(request, "loanPortal.html")


def payments(request):
    return render(request, "payments.html")


def reports(request):
    return render(request, "reports.html")


def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
        # else:
        #     return render(request, 'register.html', {'form': form})
        #     raise Exception(form.errors.get_text())
    else:
        form = UserRegistration()
    return render(request, 'register.html', {'form': form})


def adminLogin(request):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    return render(request, "adminLogin.html")


def loginController(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['user']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            else:
                resp['msg'] = 'Incorrect username or password'
        else:
            resp['msg'] = 'Incorrect username or password'
    return HttpResponse(json.dumps(resp), content_type="application/json")


def logout_page(request):
    auth.logout(request)
    return redirect('/adminUser/adminLogin/')


def client(request):
    id = request.POST.get('id')
    client_data = Person.objects.get(id=id)
    client_json = {
        'name': client_data.name,
        'address': client_data.address,
        'image': '/media/' + client_data.picture.name,
        'document': '/media/' + client_data.document.name
    }
    return HttpResponse(json.dumps(client_json), content_type="application/json")


def addCollector(request):
    if request.method == "POST":
        colForm = CollectorForm(request.POST)
        if colForm.is_valid():
            colForm.save()
        else:
            context = {'form': colForm}
            return render(request, "addClient.html", context)

    collector = Collector.objects.all()
    colForm = CollectorForm(request.POST)
    return render(request, "addCollector.html", {'persons': collector, 'form': colForm})


def generateCollector(request,id):
    col = Collector.objects.get(id=id)
    img = qrFunc(col.id, col.name)
    # # qrcode = base64.b64encode(buffer.getvalue()).decode("utf-8")
    if img:
        wrapper = FileWrapper(open(settings.MEDIA_ROOT + "/qr/" + img, 'rb'))
        content_type = mimetypes.guess_type(img)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Disposition'] = "attachment; filename=%s" % img
        return response


def deleteCollector(request, id):
    itemCol = Collector.objects.get(id=id)
    itemCol.delete()
    return redirect('/adminUser/addCollector')


def singleCollector(request):
    collectorId = request.POST.get('id')
    collector_data = Collector.objects.get(id=collectorId)
    collector_json = {
        'name': collector_data.name,
    }
    return HttpResponse(json.dumps(collector_json), content_type="application/json")


def editClient(request):
    cId = request.POST.get('id')
    name = request.POST.get('name')
    address = request.POST.get('address')

    c = Person.objects.get(id=cId)
    c.name = name
    c.address = address
    c.save()
    return redirect('/adminUser/addClient')


def editCollector(request):
    colId = request.POST.get('id')
    name = request.POST.get('name')
    address = request.POST.get('address')

    col = Collector.objects.get(id=colId)
    col.name = name
    col.address = address
    col.save()
    return redirect('/adminUser/addCollector')