from rest_framework.pagination import PageNumberPagination

"""Pagination for planetarium api"""


class PlanetariumPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
