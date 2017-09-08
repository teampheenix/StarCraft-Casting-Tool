{% capture my_include %}{% include_relative README.md %}{% endcapture %}
{{ my_include | markdownify }}
