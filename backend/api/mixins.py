from rest_framework import mixins, viewsets


class GetListViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet,
):
    """ViewSet для методов Get, List"""
