import io
from glossarize.glossarize import Glossary

class TestGlossary(object):
    _template = r'\1 means {defn}; \1 is always {defn}'
    _translator = r'\1 ({defn})'
    _glossary = {'no': 'NO!'}
    _glossary_yaml = """
    hajimemashite: Nice to meet you
    neko: cat
    nekobaasu: cat bus
    """
    def test_str(self):
        glossary = Glossary(glossary = self._glossary, template = self._template)
        result = glossary.glossarize('just say no!')
        assert result == 'just say no means NO!; no is always NO!!'
    def test_buried_str(self):
        glossary = Glossary(glossary = self._glossary, template = self._template)
        result = glossary.glossarize('Arnold knows no nose')
        assert result == 'Arnold knows no means NO!; no is always NO! nose'
    def test_yml(self):
        glossary_file = io.StringIO(self._glossary_yaml)
        glossary = Glossary(glossary = glossary_file, template = self._translator)
        result = glossary.glossarize('Hajimemashite!  Yoroshiko onegai nekobaasu!')
        assert result == 'Hajimemashite (Nice to meet you)!  Yoroshiko onegai nekobaasu (cat bus)!'
        