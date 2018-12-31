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
            friends = None
            try:
                friends = request.user.profile.get_friends()
            except ObjectDoesNotExist:
                Profile.objects.get_or_create(user_id=request.user.id)
            if friends:
                from chat.serializers import FriendSerializer
                publish_socket(
                    'friends_%s' % request.user.profile.id,
                    FriendSerializer(friends, many=True, context={
                        'profile_id': request.user.profile.id}).data
                )
        return get_response(request)

    return middleware
