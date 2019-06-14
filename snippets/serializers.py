from django.contrib.auth.models import User
from rest_framework import serializers

from snippets.models import Snippet


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(
        view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner', 'title', 'code',
                  'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')


class BaseActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()


class ActivitySerializer(BaseActivitySerializer):
    def __init__(self, *args, **kwargs):
        object_serializer = kwargs.pop("object_serializer", None)
        actor_serializer = kwargs.pop("actor_serializer", None)
        super().__init__(self, *args, **kwargs)
        if object_serializer:
            self.fields["object"] = object_serializer()
        else:
            self.fields["object"] = serializers.CharField()
        if actor_serializer:
            self.fields["actor"] = actor_serializer()
        else:
            self.fields["actor"] = serializers.CharField()

    foreign_id = serializers.CharField()
    verb = serializers.CharField()
    time = serializers.DateTimeField()


class AggregatedSerializer(BaseActivitySerializer):
    def __init__(self, *args, **kwargs):
        object_serializer = kwargs.pop("object_serializer", None)
        actor_serializer = kwargs.pop("actor_serializer", None)
        super().__init__(self, *args, **kwargs)
        self.fields["activities"] = ActivitySerializer(many=True, object_serializer=object_serializer, actor_serializer=actor_serializer)
    
    group = serializers.CharField()


class NotificationSerializer(AggregatedSerializer):
    is_seen = serializers.BooleanField()
    is_read = serializers.BooleanField()


def get_activity_serializer(data, object_serializer=None, actor_serializer=None, **kwargs):
    kwargs["object_serializer"] = object_serializer
    kwargs["actor_serializer"] = actor_serializer
    serializer = ActivitySerializer
    if not data:
        return serializer(data, **kwargs)
    if "is_seen" in data[0]:
        serializer = NotificationSerializer
    elif "activities" in data[0]:
        serializer = AggregatedSerializer
    return serializer(data, **kwargs)
