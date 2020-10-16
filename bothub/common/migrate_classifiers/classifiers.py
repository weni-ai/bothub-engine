import logging
from abc import ABCMeta

logger = logging.getLogger(__name__)


class ClassifierType(metaclass=ABCMeta):
    """
    ClassifierType is our abstract base type for custom NLU providers. Each provider will
    provides a way to export phrases, intentions and entities,
    """

    # the verbose name for this classifier type
    name = None

    # the short code for this classifier type (< 16 chars, lowercase)
    slug = None

    repository_version = None
    auth_token = None
    language = None

    def migrate(self):
        """
        Must implement every classifier rule to receive phrases, intentions and consequently entities
        """
        raise NotImplementedError("classifier types must implement migrate")
