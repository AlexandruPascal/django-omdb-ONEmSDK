import datetime
import jwt

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import View as _View
from onemsdk.schema.v1 import (
    Response, Menu, MenuItem, MenuItemType, Form, FormItemContent,
    FormItemContentType, FormMeta
)

from .models import History
from .helpers import OmdbMixin


class View(_View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *a, **kw):
        return super(View, self).dispatch(*a, **kw)

    def get_user(self):
        # return User.objects.filter()[0]
        token = self.request.headers.get('Authorization')
        if token is None:
            raise PermissionDenied

        data = jwt.decode(token.replace('Bearer ', ''), key='87654321')
        user, created = User.objects.get_or_create(id=data['sub'],
                                                   username=str(data['sub']))
        return user

    def to_response(self, content):
        response = Response(content=content)
        return HttpResponse(response.json(),
                            content_type='application/json')


class HomeView(View):
    http_method_names = ['get']

    def get(self, request):
        body = [
            MenuItem(type=MenuItemType.option, description='Search',
                     method='GET', path=reverse('search_wizard'))
        ]
        user = self.get_user()
        history_count = user.history_set.count()
        if history_count:
            body.append(MenuItem(
                type=MenuItemType.option,
                description='History ({count})'.format(count=history_count),
                method='GET',
                path=reverse('history')),
            )
        return self.to_response(Menu(body=body, header='menu'))


class SearchWizardView(View, OmdbMixin):
    http_method_names = ['get', 'post']

    def get(self, request):
        body = [FormItemContent(type=FormItemContentType.string,
                                name='keyword',
                                description='Send keywords to search',
                                header='search', footer='send keyword')]
        return self.to_response(
            Form(body=body, method='POST', path=reverse('search_wizard'),
                 meta=FormMeta(confirmation_needed=False,
                               completion_status_in_header=False,
                               completion_status_show=False))
        )

    def post(self, request):
        keyword = request.POST['keyword']
        response = self.get_page_data(keyword)
        if response['Response'] == 'False':
            return self.to_response(Form(
                body=[FormItemContent(
                    type=FormItemContentType.string,
                    name='result',
                    description='No results',
                    header='{keyword} SEARCH'.format(keyword=keyword.title()),
                    footer='send BACK and search again'
                )],
                method='GET',
                path=reverse('home'),
                meta=FormMeta(confirmation_needed=False,
                              completion_status_in_header=False,
                              completion_status_show=False)

            ))

        body = []
        for result in response['Search']:
            body.append(MenuItem(
                type=MenuItemType.option,
                description=u'{title} - {year}'.format(
                    title=result['Title'], year=result['Year']
                ),
                method='GET',
                path=reverse('movie_detail', args=[result['imdbID']])
            ))

        return self.to_response(Menu(
            body=body,
            header='{keyword} SEARCH'.format(keyword=keyword.title()),
            footer='Select result'
        ))


class HistoryView(View, OmdbMixin):
    http_method_names = ['get']

    def get(self, requset):
        user = self.get_user()
        history = user.history_set.order_by('-datetime')
        body = []
        for movie in history:
            body.append(MenuItem(
                type=MenuItemType.option,
                description=u'{title} - {year}'.format(
                    title=movie.title, year=movie.year
                ),
                method='GET',
                path=reverse('movie_detail', args=[movie.omdb_id])
            ))

        return self.to_response(Menu(
            body=body, header='history', footer='Select from history'
        ))


class MovieDetailView(View, OmdbMixin):
    http_method_names = ['get']

    def get(self, request, id):
        history = History.objects.all()
        movie_from_history = [movie for movie in history if movie.omdb_id == id]
        if not movie_from_history:
            response = self.get_page_data(id)
            if response['Response'] == 'False':
                return self.to_response(Form(
                    body=[FormItemContent(
                        type=FormItemContentType.string,
                        name='result',
                        description='Please try again later',
                        header='INFO',
                        footer='send BACK'
                    )],
                    method='GET',
                    path=reverse('home'),
                    meta=FormMeta(confirmation_needed=False,
                                  completion_status_in_header=False,
                                  completion_status_show=False)
                    ))
            omdb_id = response['imdbID']
            title = response['Title']
            year = response['Year']
            rate = response['Ratings'][0]['Value']
            plot = response['Plot']
            history_create = History.objects.create(
                user=self.get_user(), omdb_id=omdb_id, title=title, year=year,
                rate=rate, plot=plot, datetime=datetime.datetime.now()
            )
            history_create.save()
        else:
            movie_from_history = movie_from_history[0]
            omdb_id = movie_from_history.omdb_id
            title = movie_from_history.title
            year = movie_from_history.year
            rate = movie_from_history.rate
            plot = movie_from_history.plot

        user = self.get_user()
        user_history = user.history_set.all()
        movie_from_user = [movie for movie in user_history if movie.omdb_id == id]
        if movie_from_history and not movie_from_user:
            history_create = History.objects.create(
                user=self.get_user(), omdb_id=omdb_id, title=title, year=year,
                rate=rate, plot=plot, datetime=datetime.datetime.now()
            )
            history_create.save()
        elif movie_from_history and movie_from_user:
            movie_from_user = movie_from_user[0]
            movie_from_user.datetime = datetime.datetime.now()
            movie_from_user.save()

        body = [
            FormItemContent(
                type=FormItemContentType.string,
                name='movie',
                description=u'\n'.join([
                    u'Title: {movie_title}'.format(movie_title=title),
                    u'Year: {movie_year}'.format(movie_year=year),
                    u'Rate: {movie_rate}'.format(movie_rate=rate),
                    u'Plot: {movie_plot}'.format(movie_plot=plot),
                ]),
                header='Movie details', footer='send BACK')
        ]
        return self.to_response(Form(
            body=body, method='GET', path=reverse('home'),
            meta=FormMeta(confirmation_needed=False,
                          completion_status_in_header=False,
                          completion_status_show=False)
        ))
