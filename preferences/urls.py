from django.urls import path
from preferences.views import CreatePreferences, ListPreferences, RemovePreferences, UpdatePreferences, ListAllPreferences, AssignPreferenceToUser, UnnassignPreferenceFromUser, ListUsersPerPreference, AssignPreferenceToUserNoCookie


urlpatterns = [
    path('create', CreatePreferences.as_view(), name='create_preferences'),
    path('list/<int:users>', ListPreferences.as_view(), name='list_preferences'),
    path('list', ListAllPreferences.as_view(), name='list_all_preferences'),
    path('list/users/<int:preference_id>', ListUsersPerPreference.as_view(), name='list_users_per_preference'),
    path('remove/<int:id>', RemovePreferences.as_view(), name='remove_preferences'),
    path('update/<int:id>', UpdatePreferences.as_view(), name='update_preferences'),
    path('assign/cookie/<int:preference_id>', AssignPreferenceToUser.as_view(), name='assign_preferences_to_user'),
    path('assign/<int:preference_id>', AssignPreferenceToUserNoCookie.as_view(), name='assign_preferences_to_user_no_cookie'),
    path('unassign/<int:preference_id>', UnnassignPreferenceFromUser.as_view(), name='unassign_preferences_from_user'),
]
