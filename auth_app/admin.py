from django.contrib import admin

from auth_app.models import Account


class AccountAdmin(admin.ModelAdmin):
    list_display = ["fullname", "user_username", "user_email"]

    def user_username(self, obj):
        return obj.user.username

    user_username.short_description = "Username"

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"


# Register your models here.
admin.site.register(Account, AccountAdmin)
