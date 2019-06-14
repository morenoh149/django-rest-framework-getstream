from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from stream_django.feed_manager import feed_manager
from stream_django.enrich import Enrich

from snippets.models import Snippet
from snippets.permissions import IsOwnerOrReadOnly
from snippets.serializers import NotificationSerializer, SnippetSerializer, UserSerializer, get_activity_serializer

enricher = Enrich()


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly, )

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class NotificationViewSet(viewsets.ViewSet):
    """
    This viewset returns a notifications feed for the logged in user.
    The feed contains events for when a relevant snippet is created.
    """
    serializer_class = NotificationSerializer

    def list(self, request):
        feed = feed_manager.get_notification_feed(self.request.user.id)
        activities = feed.get()['results']
        enriched_activities = enricher.enrich_aggregated_activities(activities)
        serializer = get_activity_serializer(enriched_activities, SnippetSerializer, None, many=True, context={'request': request})
        return Response(serializer.data)
