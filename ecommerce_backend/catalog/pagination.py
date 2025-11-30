from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """
    Custom pagination for product listings.
    
    Features:
    - Default page size of 12 products
    - Client can override page size: ?page_size=50
    - Maximum 100 items per page
    - Returns page numbers: ?page=2
    
    Response format:
    {
        "count": 150,
        "next": "http://api.example.com/products/?page=3",
        "previous": "http://api.example.com/products/?page=1",
        "results": [...]
    }
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
