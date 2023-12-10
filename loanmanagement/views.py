import base64
import io
import json
import os
from io import BytesIO
import mimetypes
from wsgiref.util import FileWrapper

from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.http import FileResponse
from django.shortcuts import render, HttpResponse, redirect

from django.conf import settings
from .forms import PersonForm, UserRegistration
from .models import Person
from qrcode import *


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


def generateQR(request, id):
    person = Person.objects.get(id=id)
    img = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    img.make(person.id)
    qr = img.make_image(fill_color="black", back_color="white").convert("RGB")

    img_url = 'qr-' + str(person.name) + '.png'
    # buffer = io.BytesIO()
    qr.save(img_url)
    # qrcode = base64.b64encode(buffer.getvalue()).decode("utf-8")
    wrapper = FileWrapper(open(settings.MEDIA_ROOT + "/qr/" + img_url, 'rb'))
    content_type = mimetypes.guess_type(img_url)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Disposition'] = "attachment; filename=%s" % img_url
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
