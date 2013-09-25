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
                term = block.splitlines()[0].strip()
                defn = "\n".join(line.strip() for line in block.splitlines()[1:])
                self[term] = defn
            
class Glossary(object):
    """
    Annotates text it is passed based on a glossary dictionary.
    
    By default, uses title attributes for visualization as tooltips.
    >>> g = Glossary({'OH': 'Ohio', 'MI': 'Michigan', 'QC': 'Quebec'})
    >>> g.annotate('How far to QC?')
    'How far to <span title="Quebec" style="text-decoration:underline;">QC</span>?'
    """
    _template = r'\1<span title="{defn}" style="text-decoration:underline;">\2</span>\3'
    _searcher = r'(\A|[\s\,]+)({term})(\Z|[\s\,]+)'
    def __init__(self, glossary='glossary.yml', template=None):
        """
        Creates a Glossary, a dictionary of terms that can annotate strings or HTML tables.
        
        Arguments
        ---------
        glossary:  source of term definitions; can be
                     - a Python dictionary
                     - name of a YAML file to read
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
                else:
                    self.glossary = DctFromTxtFile(open(self.glossary_file))
        self.template = template or self._template
    def replace(self, txt):
        for term in self.glossary:
            txt = re.sub(self._searcher.format(term=term), 
                         self.template.format(defn=self.glossary[term]),      
                         txt, flags=re.IGNORECASE)
        return txt
    def annotate(self, resultset):
        if hasattr(resultset, '_repr_html_'):
            annotated_txt = resultset._repr_html_()
        else:
            annotated_txt = '<div style="font-family:monospace">%s</div>' % resultset.n
        resultset.annotated = Annotated(self.replace(annotated_txt))
        return resultset.annotated
            
class Annotated(str):
    def _repr_html_(self):
        spaced = self.replace('  ', '&nbsp; ').replace('  ', '&nbsp; ')
        spaced = spaced.replace('\n', '<br>\n').replace('\t', '&nbsp;&nbsp;&nbsp; ')
        return spaced
               
if __name__ == '__main__':
    doctest.testmod()