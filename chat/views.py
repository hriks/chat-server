# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from rest_framework import permissions, generics, status, exceptions
from rest_framework.response import Response

from chat.serializers import (
    FriendSerializer, ProfileSerializer, Profile,
    CreateUpdateFriendRequestSerializer, FriendRequest,
    MessaageSerializer, CreateMessageSerializer,
    Message)


from django.views import View


class Login(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('dashboard'))
        return render(request, self.template_name, {'form': form})


class Logout(View):

    @method_decorator(login_required(login_url="/user/login/"))
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login'))


class Signup(View):
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            return redirect(reverse('dashboard'))
        return render(request, 'signup.html', {'form': form})


class Dashboard(View):
    template_name = 'dashboard.html'

    @method_decorator(login_required(login_url="/user/login/"))
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class Friends(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendSerializer

    def get_queryset(self):
        return self.request.user.profile.get_friends()

    def list(self, request):
        return Response(
            FriendSerializer(
                self.get_queryset(), many=True,
                context={'profile_id': request.user.profile.id}
            ).data, status=status.HTTP_200_OK)


class Profiles(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.exclude(
            id=self.request.user.profile.id)

    def list(self, request):
        return Response(
            ProfileSerializer(
                self.get_queryset(), many=True,
                context={'profile_id': request.user.profile.id}
            ).data, status=status.HTTP_200_OK)


class CreateFriendRequest(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateUpdateFriendRequestSerializer

    def perform_create(self, serializer):
        serializer.save(from_user_id=self.request.user.profile.id)


class UpdateFriendRequest(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateUpdateFriendRequestSerializer
    queryset = FriendRequest.objects.all()

    def put(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'action' not in request.data:
            exceptions.NotAcceptable()
        if request.user.profile.id not in [instance.to_user.id, instance.from_user.id]:  # noqa
            exceptions.PermissionDenied()
        return Response({
            'action': getattr(instance, request.data['action'])()
        }, status=status.HTTP_202_ACCEPTED)


class Messages(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessaageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            thread_id=self.request.query_params.get('thread_id')
        ).order_by('-time')


class CreateMessage(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateMessageSerializer

    def perform_create(self, serializer):
        serializer.save(profile_id=self.request.user.profile.id)
