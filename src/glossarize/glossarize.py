"""
Given a glossary, edit a string so that the definitions are provided.
By default, inserts definitions as tooltips (HTML ``title`` attributes).

Designed for use in IPython notebook; untried in other environments.

Glossaries can be passed as dictionaries or names of .yml or .txt files.

>>> from glossarize.glossarize import Glossary
>>> g = Glossary({'java': 'old and busted', 'python': 'the new hotness'})
>>> g.annotate('Shall the new project use Java or Python?')

"""
import json
import os
import re
import yaml
import doctest

class DctFromTxtFile(dict):
    splitter = re.compile('\n[ \t]*\n')
    def __init__(self, infile):
        """
        Initialize with an open File object of text.  
        
        Keys *must* be separated by one linefeed from values;
        key:value pairs *must* be separated by two or more linefeeds.
        
        >>> import io
        >>> result = io.StringIO(u'x \n xval \n\n y \n yval')
        >>> result['x']
        'xval'
        >>> result['y']
        'yval'
        """
        txt = infile.read()
        for block in self.splitter.split(txt):
            block = block.strip()
            if block:
                term = block.splitlines()[0].strip().decode('utf8')
                defn = "\n".join(line.strip() for line in block.splitlines()[1:])
                self[term] = defn.decode('utf8')
            
class Glossary(object):
    """
    Annotates text it is passed based on a glossary dictionary.
    
    By default, uses title attributes for visualization as tooltips.
    >>> g = Glossary({'OH': 'Ohio', 'MI': 'Michigan', 'QC': 'Quebec'})
    >>> g.annotate('How far to QC?')
    'How far to <span title="Quebec" style="text-decoration:underline;">QC</span>?'
    """
    _template = ur'\1<span title="{defn}" style="text-decoration:underline;">\2</span>\3'
    _marker = '___TRANSLATE_ME___'
    _marking_template = ur'\1\2%s\3' % _marker
    _searcher = ur'(\A|[\s\,>]+)({term})(\Z|[\s\,<]+|&nbsp;)'
    def _hidden_in_unicode(self, txt):
        """
        Weird maneuver to protect 
        """
    def __init__(self, glossary='glossary.yml', template=None):
        """
        Creates a Glossary, a dictionary of terms that can annotate strings or HTML tables.
        
        Arguments
        ---------
        glossary:  source of term definitions; can be
                     - a Python dictionary
                     - name of a YAML file to read
                     - name of a JSON file to read
                     - name of a plain text file, with one line b/t 
                       a term and its definition, and two lines b/t
                       the definition and the next term
        template:  a Python 3 format string used to replace the term
                   with its annoated term, using \2 for the term and
                   `defn` for the definition
        """
        if hasattr(glossary, 'keys'):
            self.glossary = glossary
        elif hasattr(glossary, 'flush'):
            self.glossary = yaml.load(glossary)
        else:
            self.glossary_file = glossary
            with open(self.glossary_file) as infile:
                if self.glossary_file.endswith('.yml') or self.glossary_file.endswith('yaml'):
                    self.glossary = yaml.load(infile)
                elif self.glossary_file.endswith('.json'):
                    self.glossary = json.load(infile)
                else:
                    self.glossary = DctFromTxtFile(open(self.glossary_file))
        self.template = template or self._template
    def replace(self, txt):
        # First pass - mark translatable terms.
        for term in self.glossary:
            seek = self._searcher.format(term=term)
            txt = re.sub(seek, self._marking_template, txt, flags=re.IGNORECASE)
        # Second pass - we will only replace terms marked as translatable
        # on the first pass.  This protects us from replacing terms that
        # appear within the tooltips, creating nested tooltip syntax messes
        for term in self.glossary:
            seek = self._searcher.format(term=term+self._marker)
            replacement = self.template.format(defn=self.glossary[term]
                                               .replace(u'\\', u'\\\\')
                                               .replace(u'"', u'\"'))
            txt = re.sub(seek, replacement, txt, flags=re.IGNORECASE)
        txt = txt.replace(self._marker, '')
        return txt
    def annotate(self, target):
        if hasattr(target, '_repr_html_'):
            html = target._repr_html_()
        else:
            if hasattr(target, 'n'):
                html = target.n
            else:
                html = str(target)
            html = u'<div style="font-family:monospace">%s</div>' % html
            html = html.replace(u'  ', u'&nbsp; ').replace(u'  ', u'&nbsp; ') \
                       .replace(u'\n', u'<br>\n').replace(u'\t', u'&nbsp;&nbsp;&nbsp; ')            
        target.annotated = Annotated(self.replace(html))
        return target.annotated
            
class Annotated(unicode):
    def _repr_html_(self):
        return self
               
if __name__ == '__main__':
    doctest.testmod()
