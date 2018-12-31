from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def active_user_middleware(get_response):

    def middleware(request):
        """ Update user online status. """
        if request.user.is_authenticated:
            from django.utils.timezone import now
            cache.set('seen_{}'.format(request.user.username), now(),
                      settings.USER_ONLINE_TIMEOUT)
            from chat.models import publish_socket, Profile
            try:
                from chat.serializers import FriendSerializer
                friends = FriendSerializer(
                    request.user.profile.get_friends(), many=True).data
                if friends:
                    publish_socket(
                        'friends_%s' % request.user.profile.id,
                        friends
                    )
            except ObjectDoesNotExist:
                Profile.objects.get_or_create(user_id=request.user.id)

        return get_response(request)

    return middleware
