<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Achievements
</div>

<ul>
% for a in achievement_list:
<li>${a}</li>
% endfor
</ul>
