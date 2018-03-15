class BotHubException(Exception):
    pass

class RepositoryUpdateAlreadyStartedTraining(BotHubException):
    pass


class RepositoryUpdateAlreadyTrained(BotHubException):
    pass


class TrainingNotAllowed(BotHubException):
    pass


class DoesNotHaveTranslation(BotHubException):
    pass
