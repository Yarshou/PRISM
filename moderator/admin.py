from django.contrib import admin
from django.utils.html import format_html

from analyze.models import Photo
from moderator.models import UserRequest


class UserRequestAdmin(admin.ModelAdmin):
    fields = (
        'get_username',
        'get_avatar',
        'get_requested_image',
        'status',
    )
    readonly_fields = (
        'get_username',
        'get_avatar',
        'get_requested_image'
    )

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

    def get_avatar(self, obj):
        photo = Photo.objects.get(related_photos__user=obj.user, is_avatar=True)
        return format_html('<img src="{}" width="300" height="300" />'.format(photo.img.url))

    get_avatar.short_description = 'Avatar'


    def get_requested_image(self, obj):
        return format_html('<img src="{}" width="300" height="300" />'.format(obj.rected_image.url))

    get_requested_image.short_description = 'Requested image'

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if obj and change:
            if obj.status:
                encoding = obj.vector
                encoding.user = obj.user
                encoding.save()
        super(UserRequestAdmin, self).save_model(request, obj, form, change)



admin.site.register(UserRequest, UserRequestAdmin)
