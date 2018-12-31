# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


def publish_socket(facility, data):
    from ws4redis.redis_store import RedisMessage
    from ws4redis.publisher import RedisPublisher
    import json
    redis_publisher = RedisPublisher(
        facility=facility, broadcast=True)
    message = RedisMessage(json.dumps(data))
    redis_publisher.publish_message(message)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE
    )
    last_active = models.DateTimeField(null=True, blank=True)

    @property
    def is_online(self):
        from django.core.cache import cache
        return cache.get('seen_%s' % self.user.username) is not None

    def get_friends(self):
        return Friend.objects.select_related(
            'to_user').filter(from_user_id=self.id)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        Profile,
        related_name='friendship_requests_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        Profile,
        related_name='friendship_requests_received',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('from_user', 'to_user'),)

    def accept(self):
        """ Accept this friendship request. """
        Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )
        Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user
        )

        self.delete()

        # Delete any reverse requests
        FriendRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        name = '%s -> %s' % (
            self.to_user.user.username, self.from_user.user.username)
        thread = Thread.objects.create(name=name)
        thread.profiles.add(self.to_user, self.from_user)
        self.update_socket()
        return True

    def reject(self):
        """ Reject this friendship request. """
        self.delete()
        self.update_socket()
        return True

    def cancel(self):
        """ Cancel this friendship request. """
        self.delete()
        self.update_socket()
        return True

    def update_socket(self):
        from chat.serializers import ProfileSerializer
        publish_socket(
            'friendrequestreceive_%s' % self.to_user.id, ProfileSerializer(
                self.from_user,
                context={'profile_id': self.to_user.id}
            ).data)
        publish_socket(
            'update_friend_request_%s' % self.from_user.id, ProfileSerializer(
                self.to_user,
                context={'profile_id': self.from_user.id}
            ).data)


@receiver(
    post_save, sender=FriendRequest,
    dispatch_uid="friendRequest_%s" % str(now()))
def friend_request_post_save(sender, instance, created, **kwargs):
    if created:
        instance.update_socket()


class Friend(models.Model):
    to_user = models.ForeignKey(Profile, related_name='friends',
                                on_delete=models.CASCADE)
    from_user = models.ForeignKey(
        Profile, related_name='unused_friend_relation',
        on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('from_user', 'to_user'),)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves.
        if self.to_user == self.from_user:
            raise ValidationError(
                "User cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)

    def __str__(self):
        return "User #{} is friends with #{}".format(
            self.to_user.id, self.from_user.id)


class Thread(models.Model):
    name = models.CharField(max_length=255)
    profiles = models.ManyToManyField(Profile, related_name='threads')
    last_message = models.DateTimeField(null=True)
    last_message_read = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        related_name='messages',
        on_delete=models.CASCADE
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.thread.last_message = now()
        self.thread.save()
        super(Message, self).save(*args, **kwargs)
        from chat.serializers import MessaageSerializer
        publish_socket(
            'thread_%s' % self.thread.id, MessaageSerializer(self).data)
