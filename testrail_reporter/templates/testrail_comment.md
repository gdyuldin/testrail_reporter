{{ xunit_case.message|default('Passed') }}

Env: **{{ env_description }}**

[Jenkins Job Result]({{ jenkins_url }})

{% if paste_url %}
[Trace, logs]({{ paste_url }})
{% endif %}

---
{% if xunit_case.trace %}
**Trace:**
{% for line in xunit_case.trace.splitlines() %}
    {{ line }}
{% endfor %}
{% endif %}
