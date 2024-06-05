import os
import xmlrpc.client
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from .tools import check_connexion, format_time_render

load_dotenv()


def index(request):
    """Method for home page"""
    url, db = os.getenv('ODOO_URL'), os.getenv('ODOO_DB')
    if not check_connexion():
        request.session.flush()
        request.session['url'], request.session['db'], request.session['check_connexion'] = url, db, False

        return render(request, 'index.html', {'connected': request.session.get('uid')})

    request.session['check_connexion'] = True

    if request.session.get('url') != url:
        request.session.flush()
        request.session['url'], request.session['db'] = url, db

        return redirect('login')

    if request.session.get('uid'):
        models = xmlrpc.client.ServerProxy("{0}/xmlrpc/2/object".format(request.session['url']))
        attendance = models.execute_kw(request.session.get('db'), request.session.get('uid'),
                                       request.session.get('password'), 'hr.attendance', 'search_read',
                                       [[['employee_id', '=', request.session.get('employee_id')]]],
                                       {'fields': ['check_in', 'check_out', 'user_id'], 'limit': 1, 'order': 'id desc'})

        if any(attendance):
            request.session['check_in'] = format_time_render(attendance[0].get('check_in')) if attendance[0].get(
                'check_in') else False
            request.session['check_out'] = format_time_render(attendance[0].get('check_out')) if attendance[0].get(
                'check_out') else False

    else:
        return redirect('login')

    return render(request, 'index.html', {'connected': request.session.get('uid'), 'check_connexion': True})


def login(request):
    """Method for login page"""
    if not check_connexion():
        return redirect('home')

    if request.session.get('uid'):
        return redirect('home')
    connected = request.session.get('uid')

    request.session.flush()
    request.session['check_connexion'] = True
    request.session['url'], request.session['db'] = os.getenv('ODOO_URL'), os.getenv('ODOO_DB')
    return render(request, 'login.html', {'connected': connected})


def login_request(request):
    """Method for login post request"""
    if not check_connexion():
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        request.session['uid'] = False

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(request.session.get('url')))
        uid = common.authenticate(request.session.get('db'), username, password, {})

        if uid:
            request.session['username'] = request.POST.get('login')
            request.session['password'] = request.POST.get('password')
            request.session['uid'] = uid
            models = xmlrpc.client.ServerProxy("{0}/xmlrpc/2/object".format(request.session['url']))
            employee = models.execute_kw(request.session.get('db'), request.session.get('uid'),
                                         request.session.get('password'), 'hr.employee', 'search_read',
                                         [[['user_id', '=', request.session.get('uid')]]],
                                         {'fields': ['name', 'barcode', 'user_id'], 'limit': 1})
            request.session['employee'] = employee[0].get('name')
            request.session['employee_id'] = employee[0].get('id')
            request.session['barcode'] = employee[0].get('barcode')
            attendance = models.execute_kw(request.session.get('db'), request.session.get('uid'),
                                           request.session.get('password'), 'hr.attendance', 'search_read',
                                           [[['employee_id', '=', employee[0].get('id')]]],
                                           {'fields': ['check_in', 'check_out', 'user_id'], 'limit': 1,
                                            'order': 'id desc'})
            if any(attendance):
                request.session['check_in'] = attendance[0].get('check_in')
                request.session['check_out'] = attendance[0].get('check_out')

            return redirect('home')
        else:
            request.session['employee'] = False

            return redirect('login')


def attendance_check(request):
    """Method to check employee"""
    if not check_connexion():
        return redirect('home')

    models = xmlrpc.client.ServerProxy("{0}/xmlrpc/2/object".format(request.session['url']))
    barcode = request.session.get('barcode')
    models.execute_kw(request.session.get('db'), request.session.get('uid'), request.session.get('password'),
                      'hr.employee', 'attendance_scan',
                      [[barcode]])

    return redirect('home')


def logout(request):
    """Method for lgout"""
    if not check_connexion():
        return redirect('home')

    request.session.flush()

    return redirect('login')
