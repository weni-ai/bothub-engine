from django.utils import translation


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            return self.get_response(request)

        user_language = getattr(user, "language", None)
        if not user_language:
            return self.get_response(request)

        translation.activate(user_language)

        response = self.get_response(request)

        return response
