from django.urls import path
from .views import get_user_profile_data, CustomTokenObtainPairView, CustomTokenRefreshView, register, authenticated, toggle_follow, get_user_posts, toggle_like, create_post, get_posts, search_users, update_user_details, logout, delete_post, get_friends, post_comment, google_auth, check_username, set_username, get_user_photos



urlpatterns = [
    path('user_data/<str:pk>/', get_user_profile_data),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('authenticated/', authenticated),
    path('register/', register),
    path('auth/google/', google_auth),
    path('toggle_follow/', toggle_follow), 
    path('toggle_like/', toggle_like), 
    path('posts/<str:pk>/', get_user_posts), 
    path('create_post/', create_post), 
    path('get_posts/', get_posts), 
    path('search/', search_users), 
    path('update_user/', update_user_details), 
    path('logout/', logout), 
    path('delete_post/', delete_post), 
    path('get_friends/<str:pk>/', get_friends), 
    path('post_comment/', post_comment), 
    path('set_username/', set_username), 
    path('check_username/', check_username), 
    path('get_photos/', get_user_photos), 

]

