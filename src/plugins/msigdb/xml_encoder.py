import re

class xmlEncoder():

    def encode_xml(xml_text: str):
        # Dictionary for replacements
        replacements = {
            '&': '&amp;',
            '<sup>': '&lt;sup&gt;',
            '</sup>': '&lt;/sup&gt;',
            '<sub>': '&lt;sub&gt;',
            '</sub>': '&lt;/sub&gt;',
            '<i>': '&lt;i&gt;',
            '</i>': '&lt;/i&gt;',
            '<b>': '&lt;b&gt;',
            '</b>': '&lt;/b&gt;',
            '<BR/>': '&lt;BR/&gt;',
            '<br/>': '&lt;br/&gt;',
            ' "TRP-EGL" ': ' &quot;TRP-EGL&quot; ',
            ' "Treg" ': ' &quot;Treg&quot; ',
            '</=': '&lt;/=',
            '>/=': '&gt;/=',
            '< ': '&lt; ',
            '> ': '&gt; ',
            '<or': '&lt;or',
            '>or': '&gt;or',
            ' > ': ' &gt; ',
            ' < ': ' &lt; ',
            ' =< ': ' =&lt; ',
            ' => ': ' =&gt; ',
            '(': '&#40;',
            ')': '&#41;'
        }

        # Apply replacements
        for pattern, replacement in replacements.items():
            xml_text = re.sub(re.escape(pattern), replacement, xml_text)

        # Handle remaining cases
        xml_text = re.sub(r'<([\d_.=-])', r'&lt;\1', xml_text)
        xml_text = re.sub(r'>([\d_.=-])', r'&gt;\1', xml_text)

        return xml_text


    def decode_xml(xml_text: str):
        # Dictionary for replacements
        replacements = {
            '&amp;': '&',
            '&lt;sup&gt;': '<sup>',
            '&lt;/sup&gt;': '</sup>',
            '&lt;sub&gt;': '<sub>',
            '&lt;/sub&gt;': '</sub>',
            '&lt;i&gt;': '<i>',
            '&lt;/i&gt;': '</i>',
            '&lt;b&gt;': '<b>',
            '&lt;/b&gt;': '</b>',
            '&lt;BR/&gt;': '<BR/>',
            '&lt;br/&gt;': '<br/>',
            '&quot;TRP-EGL&quot;': ' "TRP-EGL" ',
            '&quot;Treg&quot;': ' "Treg" ',
            '&lt;=': '</=',
            '&gt;=': '>/=',
            '&lt; ': '< ',
            '&gt; ': '> ',
            '&lt;or': '<or',
            '&gt;or': '>or',
            ' &gt; ': ' > ',
            ' &lt; ': ' < ',
            ' =&lt; ': ' =< ',
            ' =&gt; ': ' => ',
            '&#40;': '(',
            '&#41;': ')'
        }

        # Apply replacements
        for pattern, replacement in replacements.items():
            xml_text = xml_text.replace(pattern, replacement)

        # Handle remaining cases
        xml_text = re.sub(r'&lt;([\d_.=-])', r'<\1', xml_text)
        xml_text = re.sub(r'&gt;([\d_.=-])', r'>\1', xml_text)

        return xml_text