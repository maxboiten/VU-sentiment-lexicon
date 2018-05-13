from distutils.core import setup

setup(name='VUSentimentLexiconLight',
      version='0.1',
      description = 'Small version of VU Sentiment Lexicon. Code covers VU-sentiment-aggregator and' + 
      'VU-polarity-tagger package functionalities, but allows outside pos-tagger such as spaCy.',
      author = 'Max Boiten',
      packages = ['VUSentimentLexiconLight'],
      package_data = {'VUSentimentLexiconLight':['*-lexicon/*']}
      )
      
