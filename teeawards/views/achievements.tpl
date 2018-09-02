<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div class="achievements_title">
    <label>
    Achievements
    </label>
</div>

<div class="achievements_list">
  % for name, data in achievement_desc_list.items():
   ${data}
    <br/>
  % endfor
</div>
