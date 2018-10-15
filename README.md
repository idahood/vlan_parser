# This became https://github.com/ansible/ansible/pull/40555

# vlan_parser
Ansible filter for declaratively defining vlan trunks

# Example Jinja usage
```jinja
{% set parsed_vlans = item.vlans | vlan_parser %}
switchport trunk allowed vlan {{ parsed_vlans[0] }}
{% for i in range (1, parsed_vlans | count) %}
switchport trunk allowed vlan add {{ parsed_vlans[i] }}
```
