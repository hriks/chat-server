from rest_framework import serializers

from chat.models import (
    Thread, Message, Friend, Profile,
    FriendRequest
)

import pytz


class ThreadSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        return MessageSerializer(obj.messages.all(), many=True).data

    class Meta:
        model = Thread
        fields = ('name', 'last_message', 'messages')


class MessageSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    def get_time(self, obj):
        return obj.time.astimezone(
            pytz.timezone('Asia/Kolkata')).strftime("%d %B, %Y %I: %M %p")

    class Meta:
        model = Message
        fields = ('text', 'time')


class FriendSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(
        source="to_user.is_online", read_only=True)
    username = serializers.SerializerMethodField()
    last_active = serializers.SerializerMethodField()
    thread_id = serializers.SerializerMethodField()
    last_thread_message = serializers.SerializerMethodField()
    last_message_read = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.to_user.user.username.title()

    def get_last_active(self, obj):
        if obj.to_user.last_active is None:
            return ' - '
        return obj.to_user.last_active.astimezone(
            pytz.timezone('Asia/Kolkata')).strftime("%d %m, %Y %I: %M %p")

    def get_thread_id(self, obj):
        return obj.from_user.threads.get(
            profiles__in=[obj.to_user.id, self.context.get('profile_id')]).id

    def get_last_thread_message(self, obj):
        thread = obj.from_user.threads.get(
            profiles__in=[obj.to_user.id, self.context.get('profile_id')])
        messages = Message.objects.filter(thread=thread)
        if messages.exists():
            return messages.latest('time').text
        return ' Send a Message '

    def get_last_message_read(self, obj):
        return obj.from_user.threads.get(
            profiles__in=[obj.to_user.id, self.context.get('profile_id')]
        ).last_message_read

    class Meta:
        model = Friend
        fields = (
            'username', 'is_online', 'last_active', 'thread_id',
            'last_message_read', 'last_thread_message'
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    friend_request_send = serializers.SerializerMethodField()
    friend_request_recieved = serializers.SerializerMethodField()
    request_id = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username.title()

    def get_is_friend(self, obj):
        return Friend.objects.filter(
            to_user_id=obj.id, from_user_id=self.context.get("profile_id")
        ).exists()

    def get_friend_request_send(self, obj):
        return FriendRequest.objects.filter(
            from_user_id=self.context.get("profile_id"), to_user_id=obj.id
        ).exists()

    def get_friend_request_recieved(self, obj):
        return FriendRequest.objects.filter(
            to_user_id=self.context.get("profile_id"), from_user_id=obj.id
        ).exists()

    def get_request_id(self, obj):
        if self.get_friend_request_send(obj):
            return FriendRequest.objects.get(
                from_user_id=self.context.get("profile_id"), to_user_id=obj.id
            ).id
        elif self.get_friend_request_recieved(obj):
            return FriendRequest.objects.get(
                to_user_id=self.context.get("profile_id"), from_user_id=obj.id
            ).id
        return None

    class Meta:
        model = Profile
        fields = (
            'username', 'id', 'is_friend', 'friend_request_send',
            'friend_request_recieved', 'request_id'
        )


class CreateUpdateFriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ('to_user',)


class MessaageSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_time(self, obj):
        return obj.time.astimezone(
            pytz.timezone('Asia/Kolkata')).strftime("%d %B, %Y %I: %M %p")

    def get_username(self, obj):
        return obj.profile.user.username

    class Meta:
        model = Message
        fields = ('text', 'time', 'username')


class CreateMessageSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_time(self, obj):
        return obj.time.astimezone(
            pytz.timezone('Asia/Kolkata')).strftime("%d %B, %Y %I: %M %p")

    def get_username(self, obj):
        return obj.profile.user.username

    class Meta:
        model = Message
        fields = ('text', 'thread', 'time', 'username')
