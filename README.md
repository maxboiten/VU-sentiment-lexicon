VU-sentiment-lexicon
====================

This fork of the VU-sentiment-lexicon is a light-weight package that has all functionalities of the 
[VU-sentiment-aggregator](https://github.com/opener-project/VU-sentiment-aggregator-lite_NL_kernel) and 
[VU-polarity-tagger](https://github.com/opener-project/polarity-tagger). It skips the 
[OpeNER project](https://github.com/opener-project)'s core and allows for the use of spaCy for lemmatisation
and POS-tagging.

Installation
-------------
Simply download from GitHub and install using either

```shell
pip install git+https://github.com/maxboiten/VU-sentiment-lexicon
```

or 

```shell
pip install https://github.com/maxboiten/VU-sentiment-lexicon/archive/master.zip
```

Use
----------
```python
from VUSentimentLexiconLight import LexiconSent
lexicon = LexiconSent('nl')
lexicon.getPolarity('mooi', 'ADJ', spacyPos = True)
```

Lexicons
----------
For more information on lexicons and on how to add lexicons, see the original GitHub readme: 
[VU-sentiment-lexicon](https://github.com/opener-project/VU-sentiment-lexicon)

Reference
----------
Maks I, Izquierdo R, Frontini F, Agerri R, Vossen P (2014) Generating polarity
lexicons with wordnet propagation in five languages. In: Proceedings of the Ninth
International Conference on Language Resources and Evaluation (LREC'14)
