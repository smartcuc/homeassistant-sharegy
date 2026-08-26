######################
# accounts/api/urls.py
######################

from django.urls import path
from .views import UserSettingsView, UpdateOnboardingStepView
from .views import UserProfileView
from .views import UserUsageModeView
from .views import UserLanguageView, UserTimezoneView, TimezoneListView
from .views import UseInviteView
from .views import CreateInviteView
from .views import MyTenantView
from .views import UpdateMemberRoleView
from .views import RemoveMemberView
from .views import DeactivateInviteView
from .views import RequestMagicLinkView, MagicLoginView, MagicLinkStatsView, LiveLoginsView, TenantStatsView
from .views import DashboardStatsView
from .views import DemoLoginView
##from .views import TrackEventView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, LogoutView
from .views import GDPRExportView, GDPRDeleteAccountView


urlpatterns = [
    path("settings/", UserSettingsView.as_view()),
    path("onboarding-step/", UpdateOnboardingStepView.as_view()),
]

urlpatterns += [
    path("profile/", UserProfileView.as_view()),
]

urlpatterns += [
    path("usage-mode/", UserUsageModeView.as_view()),
]

urlpatterns += [
    path("language/", UserLanguageView.as_view()),
]

urlpatterns += [
   path("use-invite/", UseInviteView.as_view()),
]

urlpatterns += [
    path("create-invite/", CreateInviteView.as_view()),
]

urlpatterns += [
    path("my-tenant/", MyTenantView.as_view()),
]

urlpatterns += [
path("update-role/", UpdateMemberRoleView.as_view()),
]

urlpatterns += [
path("remove-member/", RemoveMemberView.as_view()),
]

urlpatterns += [
path("deactivate-invite/", DeactivateInviteView.as_view()),
]

urlpatterns += [
    path("request-magic-link/", RequestMagicLinkView.as_view()),
    path("magic-login/", MagicLoginView.as_view()),
    path("stats/magic-links/", MagicLinkStatsView.as_view()),
    path("stats/live-logins/", LiveLoginsView.as_view()),
    path("stats/tenants/", TenantStatsView.as_view()),
    path("stats/dashboard/", DashboardStatsView.as_view()),
##    path("track/", TrackEventView.as_view()),
]

urlpatterns += [
    # Refresh
    path("auth/refresh/", TokenRefreshView.as_view()),
    # Logout
    path("auth/logout/", LogoutView.as_view()),
    # Current user
    path("auth/me/", MeView.as_view()),
]

urlpatterns += [
    path("timezone/", UserTimezoneView.as_view()),
    path("timezones/", TimezoneListView.as_view()),
]

urlpatterns += [
    path("demo/", DemoLoginView.as_view(), name="demo-login",),
    path("gdpr/export/", GDPRExportView.as_view(), name="gdpr-export"),
    path("gdpr/delete-account/", GDPRDeleteAccountView.as_view(), name="gdpr-delete-account"),
]
