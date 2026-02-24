from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import AgendamentoConsultaViewSet, ConsultaViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"consultas", ConsultaViewSet, basename="consultas")
router.register(r"agendamentos", AgendamentoConsultaViewSet, basename="agendamentos")


urlpatterns = router.urls

urlpatterns += [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
