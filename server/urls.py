"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from chat.views import (
    Friends, Login, Signup, Dashboard, Profiles,
    CreateFriendRequest, UpdateFriendRequest,
    CreateMessage, Messages, Logout
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/login/$', Login.as_view(), name='login'),
    url(r'^user/logout/$', Logout.as_view(), name='userlogout'),
    url(r'^user/signup/$', Signup.as_view(), name='signup'),
    url(r'^user/friends$', Friends.as_view(), name='friends'),
    url(r'^user/friendsrequest/$', CreateFriendRequest.as_view()),
    url(r'^user/friendsrequest/(?P<pk>[A-Za-z_0-9\-]+)/$',
        UpdateFriendRequest.as_view()),
    url(r'^user/message/send/$', CreateMessage.as_view()),
    url(r'^user/messages$', Messages.as_view()),
    url(r'^profiles$', Profiles.as_view(), name='profiles'),
    url(r'^', Dashboard.as_view(), name='dashboard')
]
