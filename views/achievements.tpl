<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Achievements
</div>

% for a in achievement_list:
<br/>
<a href="/achievements/${a}/tcohen">${a}</a>
% endfor

