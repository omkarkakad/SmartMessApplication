from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from .forms import OrderForm
from .models import OrderModel, ActiveMenu
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

def uhome(request):
    if not request.user.is_authenticated:
        return redirect("ulogin")

    if request.user.is_staff:
        return redirect("admindashboard")

    previous_order = OrderModel.objects.filter(user=request.user).first()
    existing_user = bool(previous_order)

    if request.method == "POST":
        allow_edit = request.POST.get('edit_mode') == 'true'
        form = OrderForm(request.POST, existing_user=existing_user, 
                         name_value=previous_order.name if existing_user else '',
                         surname_value=previous_order.surname if existing_user else '',
                         allow_edit=allow_edit)

        if form.is_valid():
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            order_place = form.cleaned_data['order_place']
            is_paid = form.cleaned_data['is_paid']

            menu_data = {}
            for item in OrderModel.MENU_CHOICES:
                qty = form.cleaned_data.get(item[0], 0)
                if qty and qty > 0:
                    menu_data[item[0]] = qty

            if menu_data:
                order_menu_json = json.dumps(menu_data)

                existing_ids = set(OrderModel.objects.values_list('order_id', flat=True))
                new_order_id = 1
                while new_order_id in existing_ids:
                    new_order_id += 1

                OrderModel.objects.create(
                    order_id=new_order_id,
                    user=request.user,
                    name=name,
                    surname=surname,
                    order_menu=order_menu_json,
                    order_place=order_place,
                    is_paid=is_paid
                )

                # Refill form with updated name/surname
                form = OrderForm(
                    existing_user=True,
                    name_value=name,
                    surname_value=surname,
                    allow_edit=False,
                    initial={'name': name, 'surname': surname}
                )

                return render(request, "home.html", {
                    'form': form,
                    'msg': 'Order placed!'
                })
            else:
                return render(request, "home.html", {
                    'form': form,
                    'msg': 'Please select at least one item.'
                })

    else:
        # GET request – show form with readonly name/surname if existing user
        initial_data = {}
        if existing_user:
            initial_data = {
                'name': previous_order.name,
                'surname': previous_order.surname
            }

        form = OrderForm(
            existing_user=existing_user,
            name_value=previous_order.name if existing_user else '',
            surname_value=previous_order.surname if existing_user else '',
            allow_edit=False,
            initial=initial_data
        )

    return render(request, "home.html", {'form': form})





def ulogin(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admindashboard")
        return redirect("uhome")

    if request.method == "POST":
        un = request.POST.get("un")
        pw = request.POST.get("pw")
        usr = authenticate(username=un, password=pw)

        if usr is None:
            return render(request, "login.html", {"msg": "Invalid login"})
        elif usr.is_staff:
            return render(request, "login.html", {"msg": "Admin must login from Admin Login page"})
        else:
            login(request, usr)
            return redirect("uhome")

    return render(request, "login.html")

def usignup(request):
	if request.user.is_authenticated:
		return redirect("uhome")
	elif request.method=="POST":
		un=request.POST.get("un")
		ph = request.POST.get("phone_number")
		email = request.POST.get("email")
		pw1=request.POST.get("pw1")
		pw2=request.POST.get("pw2")


		if not re.match(r'^\d{10}$', ph):
			return render(request, "signup.html", {"msg": "Enter a valid 10-digit phone number"})

        
		try:
			validate_email(email)
		except ValidationError:
			return render(request, "signup.html", {"msg": "Enter a valid email address"})

		if pw1 == pw2:
			try:
				usr=User.objects.get(username=un)
				return render(request,"signup.html",{"msg":"User already exists"})
			except User.DoesNotExist:
				usr = User.objects.create_user(username=un, password=pw1)
				usr.email = email
				usr.save()

				# Save phone number to linked Profile
				usr.profile.phone_number = ph
				usr.profile.save()

				return redirect("ulogin")

		else:
			return render(request,"signup.html",{"msg":"Password did not match"})
	else:
		return render(request,"signup.html")
def ucp(request):
	if not request.user.is_authenticated:
		return redirect("ulogin")
	elif request.method =="POST":
		pw1=request.POST.get("pw1")
		pw2=request.POST.get("pw2")
		if pw1 == pw2:
			usr=User.objects.get(username=request.user.username)
			usr.set_password(pw1)
			usr.save()
			return redirect("ulogin")

			
		else:
			return render(request,"cp.html",{"msg":"password does not match"})
	else:
		return render(request,"cp.html")


def ulogout(request):
	logout(request)
	return redirect("ulogin")

def adminlogin(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admindashboard")

    if request.method == "POST":
        un = request.POST.get("un")
        pw = request.POST.get("pw")
        usr = authenticate(username=un, password=pw)

        if usr is None or not usr.is_staff:
            return render(request, "adminlogin.html", {"msg": "Invalid Admin login"})
        else:
            login(request, usr)
            return redirect("admindashboard")
    else:
        return render(request, "adminlogin.html")

def adminlogout(request):
	logout(request)
	return redirect("adminlogin")
  

def admindashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('adminlogin')

    # Menu price dictionary
    MENU_PRICES = {
        'Poha': 35,
        'Sabudana': 40,
        'Appe': 40,
        'Dosa': 40,
        'Yellow Dhokla': 40,
        'White Dhokla': 40,
        'Methi Thepla': 45,
        'Idli': 40,
        'kothambir wadi': 40,
        'Chana Masala': 40,
        'Jalebi': 40,
	'Egg':15,
    }

    # Get filter values from URL
    query = request.GET.get("q", "")
    payment_filter = request.GET.get("payment", "")
    place_filter = request.GET.get("place", "")
    date_filter = request.GET.get("date", "")

    # Start with all orders
    orders = OrderModel.objects.all()

    # Search by name or surname
    if query:
        orders = orders.filter(
            Q(name__icontains=query) |
            Q(surname__icontains=query)
        )

    if payment_filter:
        orders = orders.filter(is_paid=payment_filter)

    if place_filter:
        orders = orders.filter(order_place__icontains=place_filter)

    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            orders = orders.filter(order_time__date=parsed_date)
        except ValueError:
            pass

    # Sort by time
    orders = orders.order_by('order_time')

    # Calculate total cost per order
    for order in orders:
        try:
            menu_dict = json.loads(order.order_menu)
        except:
            menu_dict = {}

        total = 0
        for item, qty in menu_dict.items():
            total += MENU_PRICES.get(item, 0) * qty

        order.total_price = total

    return render(request, "admindashboard.html", {
        'orders': orders,
        'q': query,
        'payment': payment_filter,
        'place': place_filter,
        'date': date_filter
    })




def admincp(request):
	if not request.user.is_authenticated:
		return redirect("adminlogin")
	elif request.method =="POST":
		pw1=request.POST.get("pw1")
		pw2=request.POST.get("pw2")
		if pw1 == pw2:
			usr=User.objects.get(username=request.user.username)
			usr.set_password(pw1)
			usr.save()
			return redirect("adminlogin")

			
		else:
			return render(request,"admincp.html",{"msg":"password does not match"})
	else:
		return render(request,"admincp.html")



def delete_order(request, order_id):
    order = get_object_or_404(OrderModel, order_id=order_id)
    deleted_order_id = order.order_id
    order.delete()

    # Reorder remaining orders
    orders = OrderModel.objects.filter(order_id__gt=deleted_order_id).order_by('order_id')
    for o in orders:
        o.order_id -= 1
        o.save()

    return redirect("admindashboard")


def root_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admindashboard")
        else:
            return redirect("uhome")
    return redirect("ulogin")





@csrf_exempt
def auto_admin_logout(request):
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_staff:
            logout(request)
            return JsonResponse({'status': 'admin_logged_out'})
    return JsonResponse({'status': 'no_action'})


def manage_menu(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('adminlogin')

    menu_choices = [item[0] for item in OrderModel.MENU_CHOICES]
    try:
        active_menu = ActiveMenu.objects.latest('updated_at')
        current_menu = active_menu.menu_items
    except ActiveMenu.DoesNotExist:
        current_menu = menu_choices

    if request.method == "POST":
        selected_items = request.POST.getlist('menu_items')
        if selected_items:
            ActiveMenu.objects.create(menu_items=selected_items)
            current_menu = selected_items
        return render(request, "manage_menu.html", {
            "menu_choices": menu_choices,
            "current_menu": current_menu,
            "msg": "Menu updated successfully!"
        })

    return render(request, "manage_menu.html", {
        "menu_choices": menu_choices,
        "current_menu": current_menu
    })


def aboutus(request):
    return render(request, "aboutus.html")












