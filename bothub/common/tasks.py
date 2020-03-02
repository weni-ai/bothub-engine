import re

from multi_rake import Rake
import nltk
import re
import string
import ssl
from bothub.celery import app
from bothub.common.models import Repository, RepositoryExample

RE_PUNC = re.compile('[%s]' % re.escape(string.punctuation))

@app.task()
def test_task():
    try:
        createunverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = createunverified_https_context

    nltk.download('stopwords')

    for repository in Repository.objects.all():
        content = f'{repository.name}\n'
        content += f'{repository.description}\n'
        content += '\n'.join(repository.intents()) + "\n"
        content += '\n'.join([key for key in repository.entities_list]) + "\n"

        examples = RepositoryExample.objects.filter(repository_version_language__repository_version__repository=repository)
        content += '\n'.join([key.text for key in examples]) + "\n"

        text = ""
        for line in content.split('\n'):
            phrase = RE_PUNC.sub('', line)
            phrase = phrase.lower()
            text += phrase + "\n"

        stopwords = nltk.corpus.stopwords.words('english')

        print(text)

        rake = Rake(
            min_chars=2,
            max_words=1,
            min_freq=1,
            language_code='en',
            # stopwords=stopwords,  # {'and', 'of'}
            lang_detect_threshold=50,
            max_words_unknown_lang=2,
            generated_stopwords_percentile=80,
            generated_stopwords_max_len=3,
            generated_stopwords_min_freq=2,
        )
        print(text)
        keywords_tuple = rake.apply(text)
        print(keywords_tuple)
        keywords = [keyword[0] for keyword in keywords_tuple]

        print(keywords)

        break
    return True
