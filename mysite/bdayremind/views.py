
# Create your views here.
import datetime, requests, json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.template.loader import get_template
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

def index(request):
    request.session.flush()
    template = loader.get_template('bdayremind/index.html')
    return HttpResponse(template.render(request))


def auth(request):
    if 'error' in request.GET:
        raise ValueError('Error authorizing application: %s' % request.GET['error'])

    response = requests.post('https://drchrono.com/o/token/', data={
        'code': request.GET['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://django-env.pugpagfzrb.us-west-2.elasticbeanstalk.com/bdayremind/auth/',
        'client_id': 'qeNCkab7IXtkcr1gUrhkLDgFBvn1W4sXgNEu4MoY',
        'client_secret': 'LyRiOShccBKaLInvSJKEqOUMxeTF7bzgWx5Yfw0LdG8IRa5Q30Q2FZQmQ5ijqQuMjSGjrGOHXoBHJpcEpgHsPzCVoucJYigpQ9HQdZsTdSlfe4ZYr1cw43kEIYVCzIkk',
        })
    response.raise_for_status()
    data = response.json()
    request.session['access_token']=data['access_token']
    return HttpResponseRedirect(reverse('home'))


def home(request):
    if 'access_token' in request.session:
        access_token = request.session['access_token']
    else:
        return HttpResponseRedirect(reverse('home'))
    headers = {
        'Authorization' : 'Bearer %s' % access_token
    }
    response = requests.get('https://drchrono.com/api/users/current', headers=headers)
    res = response.json()
    username = res['username']
    patients = []
    patients_url = 'https://drchrono.com/api/patients'
    while patients_url:
        data = requests.get(patients_url,headers=headers).json()
        patients.extend(data['results'])
        patients_url = data['next']
    today = datetime.date.today()
    bday_list = []
    upcoming = []
    previous = []
    for p in patients:
        if p['date_of_birth'] == None:
            continue
        bdate = datetime.datetime.strptime(p['date_of_birth'],"%Y-%m-%d")
        if bdate.month > today.month:
            upcoming.append(p)
        elif bdate.month == today.month:
            if bdate.day > today.day:
                upcoming.append(p)
            if bdate.day == today.day:
                bday_list.append(p)
        else:
            previous.append(p)
    previous = sorted(previous,key=lambda patient: patient['date_of_birth'][5:])
    upcoming = sorted(upcoming,key=lambda patient: patient['date_of_birth'][5:])
    bday_list = sorted(bday_list,key=lambda patient: patient['date_of_birth'][5:])
    return render(request, 'bdayremind/home.html', {'previous':previous,'patients' : upcoming,'username': username, 'today':bday_list})


def send(request):
    if 'access_token' in request.session:
        access_token = request.session['access_token']
    else:
        return HttpResponseRedirect(reverse('home'))
    email = [request.GET['email']]
    url = 'https://drchrono.com/api/doctors'
    headers = {
        'Authorization' : 'Bearer %s' % access_token
    }
    doctors = []
    while url:
        data = requests.get(url,headers=headers).json()
        doctors.extend(data['results'])
        url = data['next']
    doctor = None
    for d in doctors:
        if d['id'] == int(request.GET['doctor']):
            doctor = d['last_name']
    context = {
        'name': request.GET['name'],
        'bday': request.GET['bday'],
        'doctor': doctor
    }
    message = get_template('bdayremind/mail_template.html').render(Context(context))
    msg = EmailMessage('Happy Birthday',message,'drcbdayapp@gmail.com',email)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(json.dumps({'success': True,'email': email}),content_type='application/json')



