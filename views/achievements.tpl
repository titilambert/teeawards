<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Achievements
</div>

<ul>
% for name, data in achievement_desc_list.items():
<li>
  ${data}
</li>
% endfor
</ul>
