from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def me_stub(request):
    """Заглушка: текущий пользователь (после авторизации — реальные данные)."""
    if request.user.is_authenticated:
        return Response({'username': request.user.username})
    return Response({'detail': 'Не авторизован'}, status=401)
