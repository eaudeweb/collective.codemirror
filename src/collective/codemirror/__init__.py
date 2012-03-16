from App.special_dtml import DTMLFile
try:
    import simplejson as json
except ImportError:
    import json
import re

def initialize(context):
    patch_pythonscripts()
    patch_pagetemplates()

def patch_pythonscripts():
    import Products.PythonScripts
    PythonScript = Products.PythonScripts.PythonScript.PythonScript
    ZPythonScriptHTML_editForm = DTMLFile('pyScriptEdit', globals())
    PythonScript.manage = PythonScript.manage_main = ZPythonScriptHTML_editForm
    PythonScript.ZPythonScriptHTML_editForm =ZPythonScriptHTML_editForm
    original_compile = PythonScript._compile
    def get_codemirror_json(self):
        error_lines = [int(re.sub(r'.*line ([0-9]+)\).*',r'\1',error))
                       for error in self.errors
                       if re.match(r'.*line ([0-9]+)\).*', error)]
        return json.dumps({
            'error_lines': error_lines,
        })
    PythonScript.get_codemirror_json = get_codemirror_json

def patch_pagetemplates():
    from Products.PageTemplates.PageTemplateFile import PageTemplateFile
    from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
    # customize `pt_editForm` of ZopePageTemplate
    tmpl = PageTemplateFile('ptEdit', globals(), __name__='pt_editForm')
    tmpl._owner = None
    ZopePageTemplate.pt_editForm = tmpl
    ZopePageTemplate.manage = tmpl
    ZopePageTemplate.manage_main = tmpl
    def get_codemirror_json(self, request):
        error_lines = [int(re.sub(r'.*line ([0-9]+)\).*',r'\1',error))
                       for error in getattr(self, '_v_errors', [])
                       if re.match(r'.*line ([0-9]+)\).*', error)]
        cursor_position = request.get('codemirror-cursor-position', None)
        data = {
            'error_lines': error_lines,
            'cursor_position': bool(cursor_position),
        }
        if cursor_position:
            data.update({
                'cursor_position': True,
                'line': int(cursor_position.split('-')[0]),
                'ch': int(cursor_position.split('-')[1]),
            })
        else:
            data['cursor_position'] = False
        return json.dumps(data)
    ZopePageTemplate.get_codemirror_json = get_codemirror_json
