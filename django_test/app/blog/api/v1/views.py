from functools import wraps
from typing import Any

from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.views import View
from django.forms.models import model_to_dict
from blog.authenticate import decode_access_token, create_access_token, create_refresh_token, \
    decode_refresh_token
from blog.models import User, Article, Comment


def jwt_required(
    refresh: bool = False,
    verify_type: bool = True,
) -> Any:

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if refresh:
                decode_refresh_token()
            else:
                decode_access_token()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


class ArticlesApiMixin:
    model = Article
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):

        return Article.objects.prefetch_related('comments')

    def render_to_response(self, context, **response_kwargs):

        return JsonResponse(context)


class UserApiMixin:
    model = User
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
    ]

    def get_queryset(self):

        return User.objects.filter(pk=self.user.id)

    def render_to_response(self, context, **response_kwargs):

        return JsonResponse(context)


class ArticlesListApi(ArticlesApiMixin, BaseListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            50
        )
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.number-1 if page.has_previous() else page.number,
            'next': page.number+1 if page.has_next() else page.number,
            'results': [model_to_dict(page_object) for page_object in page.object_list],
        }

        return context


class ArticlesDetailApi(ArticlesApiMixin, BaseDetailView):
    pk_url_kwarg = 'uuid'

    def get_context_data(self, *, object=None, **kwargs):
        if not object.is_active:
            return {'response': 'Article is not existing.'}
        context = {
            **model_to_dict(object),
            'comments': [{**model_to_dict(comment)} for comment in object.comments.all() if comment.is_active]}

        return context


class ArticlesCreateApi(ArticlesApiMixin, View):

    def post(self, request):
        token = request.COOKIES.get('accessToken', None)
        if token is not None:
            user_id, perms = decode_access_token(token)
            user = User.objects.filter(pk=user_id).first()
            try:
                article = Article.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    creation_date=request.POST.get('creation_date'),
                    rating=request.POST.get('rating'),
                    type=request.POST.get('type'),
                    author_id=user,
                )
            except TypeError:
                raise Exception('Error accured while creating article.')

        return JsonResponse(data=model_to_dict(article))


class ArticlesDeleteApi(ArticlesApiMixin, View):
    pk_url_kwarg = 'uuid'

    def delete(self, uuid):
        queryset = Article.objects.prefetch_related('comments').filter(pk=uuid).first()
        queryset.comments.all().update(is_active=False)
        queryset.is_active = False
        queryset.save()
        return JsonResponse(data=model_to_dict(queryset))


class ArticlesEditApi(ArticlesApiMixin, View):
    pk_url_kwarg = 'uuid'

    def patch(self, request, uuid):
        token = request.COOKIES.get('accessToken', None)
        if token is not None:
            user_id, perms = decode_access_token(token)
            user = User.objects.filter(pk=user_id).first()
            article = Article.objects.filter(pk=uuid)
            if user.is_superuser:
                article.update(**request.POST)
                return JsonResponse(model_to_dict(article))
            if 'blog.add_article' in perms and article.author_id == user.id:
                article.update(**request.POST, author_id=user)
                return JsonResponse(model_to_dict(article))

        raise PermissionError('unauthenticated')


class RegisterApi(UserApiMixin, View):

    def post(self, request):
        try:
            user = User.objects.create_user(**request.data)
        except TypeError:
            raise Exception('Error accured while creating user.')

        return JsonResponse(data=model_to_dict(user))


class LoginApi(UserApiMixin, View):

    def post(self, request):
        user = User.objects.filter(email=request.POST.get('email')).first()

        if not user:
            raise Exception('Invalid credentials!')

        if not user.check_password(request.POST.get('password')):
            raise Exception('Invalid credentials!')

        access_token = create_access_token(user.id, user.get_user_permissions())
        refresh_token = create_refresh_token(user.id)

        response = JsonResponse(data={'accessToken': access_token, 'refreshToken': refresh_token})

        response.set_cookie(
            key='accessToken', value=access_token, httponly=True)
        response.set_cookie(
            key='refreshToken', value=refresh_token, httponly=True)

        return response


class UserApi(UserApiMixin, View):

    def get(self, request):
        token = request.COOKIES.get('accessToken', None)
        if token is not None:
            user_id, perms = decode_access_token(token)

            user = User.objects.filter(pk=user_id).first()

            return JsonResponse(data=model_to_dict(user))

        raise PermissionError('unauthenticated')


class RefreshApi(UserApiMixin, View):

    def post(self, request):
        refresh_token = request.COOKIES.get('refreshToken')
        user_id = decode_refresh_token(refresh_token)
        user = User.objects.filter(pk=user_id).first()
        access_token = create_access_token(user_id, user.get_user_permissions())
        refresh_token = create_refresh_token(user_id)

        return JsonResponse(data={
            'accessToken': access_token,
            'refreshToken': refresh_token
        })


class LogoutApi(UserApiMixin, View):

    def post(self, _):
        response = JsonResponse(data={'message': 'success'})
        response.delete_cookie(key="accessToken")
        response.delete_cookie(key="refreshToken")
        return response
