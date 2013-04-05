<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Achievements
</div>

% for name, data in achievement_desc_list.items():
  ${data}
    <br/>
% endfor
