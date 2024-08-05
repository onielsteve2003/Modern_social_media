from django.urls import path
from ..views.block import ToggleBlockView

urlpatterns = [
    path('<int:user_id>', ToggleBlockView.as_view(), name='toggle-block'),
]
