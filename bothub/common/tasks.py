import re

from multi_rake import Rake
import nltk
import re
import string
from bothub.celery import app
from bothub.common.models import Repository, RepositoryExample

RE_PUNC = re.compile('[%s]' % re.escape(string.punctuation))

@app.task()
def test_task():
    for repository in Repository.objects.all():
        content = ""
        content += f'{repository.name}\n'
        content += f'{repository.description}\n'
        content += '\n'.join(repository.intents())
        content += '\n'.join([key for key in repository.entities_list])

        examples = RepositoryExample.objects.filter(repository_version_language__repository_version__repository=repository)
        content += '\n'.join([key.text for key in examples])

        text = ""
        for line in content:
            print(line)
            phrase = RE_PUNC.sub('', line)
            phrase = phrase.lower()
            text += phrase

        stopwords = nltk.corpus.stopwords.words('portuguese')

        rake = Rake(
            min_chars=2,
            max_words=1,
            min_freq=1,
            language_code='pt',
            stopwords=stopwords,  # {'and', 'of'}
            lang_detect_threshold=50,
            max_words_unknown_lang=2,
            generated_stopwords_percentile=80,
            generated_stopwords_max_len=3,
            generated_stopwords_min_freq=2,
        )
        keywords_tuple = rake.apply(text)
        keywords = [keyword[0] for keyword in keywords_tuple]

        print(keywords)

        break
    return True
