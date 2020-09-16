import warnings

import simplejson as json

from app.process import process_text


def get_text_and_parsing_results():
    with open('tests/parsed_text_sample.json', 'r', encoding='utf8') as f:
        sample = json.load(f)

    return sample['text'], sample['parsed_text']


def test_text_parsing():
    warnings.warn('This is only a simple test to be used in a CD workflow verification.')
    text, parsing = get_text_and_parsing_results()
    assert process_text(text=text, spacy_model_name='en_core_web_sm') == parsing
