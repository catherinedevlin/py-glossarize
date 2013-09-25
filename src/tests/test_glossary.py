import io
from glossarize.glossarize import Glossary, DctFromTxtFile

class TestDctFromTxtFile(object):
    _txt = u"""
        cat
            a domestic feline
            of questionable intent
            
        turtle
            a lovely little reptile
            
        %robot:
            your plastic pal
            who's fun to be with
            
    """
    def test_read(self):
        dct = DctFromTxtFile(io.StringIO(self._txt))
        assert dct['%robot:'] == "your plastic pal\nwho's fun to be with"
        
    
class TestGlossary(object):
    _template = r'\1 means {defn}; \1 is always {defn}'
    _translator = r'\1 ({defn})'
    _glossary = {'no': 'NO!'}
    _glossary_yaml = u"""
    hajimemashite: Nice to meet you
    neko: cat
    nekobaasu: cat bus
    """
    def test_str(self):
        glossary = Glossary(glossary = self._glossary, template = self._template)
        result = glossary.annotate('just say no!')
        assert result == 'just say no means NO!; no is always NO!!'
    def test_buried_str(self):
        glossary = Glossary(glossary = self._glossary, template = self._template)
        result = glossary.annotate('Arnold knows no nose')
        assert result == 'Arnold knows no means NO!; no is always NO! nose'
    def test_yml(self):
        glossary_file = io.StringIO(self._glossary_yaml)
        glossary = Glossary(glossary = glossary_file, template = self._translator)
        result = glossary.annotate('Hajimemashite!  Yoroshiko onegai nekobaasu!')
        assert result == 'Hajimemashite (Nice to meet you)!  Yoroshiko onegai nekobaasu (cat bus)!'
        
        