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
from .views import AuditLogView
from .views import RequestMagicLinkView, MagicLoginView, MagicLinkStatsView, LiveLoginsView, TenantStatsView

from .views import DashboardStatsView
from .views import DemoLoginView, DemoSharingAdminLoginView, DemoSharingUserLoginView
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
    # Invites (both new and legacy URLs)
    path("use-invite/", UseInviteView.as_view()),
    path("invite/use/", UseInviteView.as_view()),
    path("create-invite/", CreateInviteView.as_view()),
    path("invite/create/", CreateInviteView.as_view()),
    path("deactivate-invite/", DeactivateInviteView.as_view()),
    path("invite/deactivate/", DeactivateInviteView.as_view()),
]

urlpatterns += [
    # Tenant / Community (both legacy and new URLs)
    path("my-tenant/", MyTenantView.as_view()),
    path("tenant/me/", MyTenantView.as_view()),
    path("stats/tenants/", TenantStatsView.as_view()),
    path("tenant/stats/", TenantStatsView.as_view()),
]

urlpatterns += [
    # Members
    path("update-role/", UpdateMemberRoleView.as_view()),
    path("tenant/members/role/", UpdateMemberRoleView.as_view()),
    path("remove-member/", RemoveMemberView.as_view()),
    path("tenant/members/remove/", RemoveMemberView.as_view()),
]

urlpatterns += [
    path("audit-log/", AuditLogView.as_view()),
]

urlpatterns += [
    path("request-magic-link/", RequestMagicLinkView.as_view()),
    path("magic-link/request/", RequestMagicLinkView.as_view()),
    path("stats/magic-links/", MagicLinkStatsView.as_view()),
    path("magic-link/stats/", MagicLinkStatsView.as_view()),
    path("magic-login/", MagicLoginView.as_view()),
]

urlpatterns += [
    path("stats/dashboard/", DashboardStatsView.as_view()),
    path("dashboard-stats/", DashboardStatsView.as_view()),
]

urlpatterns += [
    path("stats/live-logins/", LiveLoginsView.as_view()),
    path("admin/live-logins/", LiveLoginsView.as_view()),
]

urlpatterns += [
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    # Current user
    path("auth/me/", MeView.as_view()),
]

urlpatterns += [
    path("timezone/", UserTimezoneView.as_view()),
    path("timezones/", TimezoneListView.as_view()),
]

urlpatterns += [
    path("demo/", DemoLoginView.as_view(), name="demo-login"),
    path("demo/sharing-admin/", DemoSharingAdminLoginView.as_view(), name="demo-sharing-admin"),
    path("demo/sharing-user/", DemoSharingUserLoginView.as_view(), name="demo-sharing-user"),
    path("demo/admin/", DemoSharingAdminLoginView.as_view(), name="demo-admin"),
    path("demo/community/", DemoSharingUserLoginView.as_view(), name="demo-community"),
    path("gdpr/export/", GDPRExportView.as_view(), name="gdpr-export"),
    path("gdpr/delete-account/", GDPRDeleteAccountView.as_view(), name="gdpr-delete-account"),
]
