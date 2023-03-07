from rest_framework import mixins, viewsets


class CLDViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    pass


class OnlyCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    pass
