from django.contrib.auth import user_logged_in, user_logged_out
from django.core.cache import cache
from django.dispatch import receiver


@receiver(user_logged_in)
def on_user_loggedin(sender, user, request, **kwargs):
    if user.is_authenticated:
        from chat.models import Profile
        Profile.objects.get_or_create(user=user)


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    """ Update user online status. """
    user = kwargs.get('user')
    if user.is_authenticated:
        cache.delete('seen_{}'.format(user.username))
