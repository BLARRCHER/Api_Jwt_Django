from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(UUIDMixin, AbstractBaseUser, PermissionsMixin, TimeStampedMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class Article(UUIDMixin, TimeStampedMixin):

    class Type(models.TextChoices):
        IT = "IT", _("Information_technologies")
        IS = "IS", _("Information_security")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateTimeField(_("creation_date"))
    rating = models.FloatField(_("rating"), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.TextField(_("type"), choices=Type.choices)
    is_active = models.BooleanField(default=True)
    author_id = models.ForeignKey("User", on_delete=SET_NULL, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"article"
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        indexes = [models.Index(fields=["creation_date", "rating"])]


class Comment(UUIDMixin, TimeStampedMixin):
    content = models.TextField(_("description"), blank=True)
    is_active = models.BooleanField(default=True)
    article_id = models.ForeignKey("Article", on_delete=models.CASCADE, related_name='comments')
    author_id = models.ForeignKey("User", on_delete=SET_NULL, null=True)

    @property
    def represent_content(self):
        return f'Комментарий от {self.author_id.username}'

    def __str__(self):
        return self.represent_content

    class Meta:
        db_table = "content\".\"comment"
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
