from django.contrib import admin
from django.urls import path
from messapp.views import root_redirect, uhome,ulogin,ulogout,usignup,ucp,adminlogin,admindashboard,adminlogout,admincp,delete_order,auto_admin_logout,manage_menu,aboutus
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", root_redirect),
    path("uhome",uhome,name="uhome"),
    path("ulogin",ulogin,name="ulogin"),
    path("ulogout",ulogout,name="ulogout"),
    path("usignup",usignup,name="usignup"),
    path("ucp",ucp,name="ucp"),
    path("adminlogin",adminlogin,name="adminlogin"),
    path("admindashboard",admindashboard,name="admindashboard"),
    path("adminlogout",adminlogout,name="adminlogout"),
    path("admincp",admincp,name="admincp"),
    path("delete_order/<int:order_id>", delete_order, name="delete_order"),
    path("auto_admin_logout", auto_admin_logout, name="auto_admin_logout"),
    path("manage_menu", manage_menu, name="manage_menu"),
    path("aboutus", aboutus, name="aboutus"),



]
