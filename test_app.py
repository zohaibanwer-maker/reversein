import unittest
from engine import edit_text
from streamlit.testing.v1 import AppTest

class EngineTests(unittest.TestCase):
    def test_phrase_and_case(self):
        self.assertEqual(edit_text('In order to test.')['output'],'To test.')

    def test_protected_spans(self):
        original='`in order to` "in order to" $in order to$ https://example.org/in_order_to MQTT 12% [12]'
        self.assertEqual(edit_text(original,synonyms=True)['output'],original)
        original='```python\n# in order to\n```\nIn order to test.'
        self.assertEqual(edit_text(original)['output'],'```python\n# in order to\n```\nTo test.')

    def test_custom_term_and_zero_intensity(self):
        source='In order to test.'
        self.assertEqual(edit_text(source,custom_terms=('In order to',))['output'],source)
        self.assertEqual(edit_text(source,intensity=0)['output'],source)

    def test_determinism_and_offsets(self):
        source='We evaluate the method in order to improve the result.'
        first=edit_text(source,synonyms=True,seed=7)
        self.assertEqual(first,edit_text(source,synonyms=True,seed=7))
        for change in first['changes']:
            self.assertEqual(source[change['start']:change['end']],change['before'])

    def test_limits(self):
        with self.assertRaises(ValueError):edit_text('x'*100001)

class AppTests(unittest.TestCase):
    def test_editor_flow(self):
        from pathlib import Path
        app=AppTest.from_file(str(Path(__file__).with_name('streamlit_app.py'))).run(timeout=20)
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label=='Load example').click().run()
        next(b for b in app.button if b.label=='Edit text').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state['result']['changes'])
        self.assertIn('12%',app.session_state['result']['output'])
        next(b for b in app.button if b.label=='Clear text').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['input_text'],'')

if __name__=='__main__':unittest.main()
