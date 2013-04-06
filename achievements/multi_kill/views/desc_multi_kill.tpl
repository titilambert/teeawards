<link rel="stylesheet" type="text/css" href="/css/achievements/multi_kill/multi_kill.css"/>
<table class="multikill_achievement achievements">
  <thead>
    <tr>
      <th rowspan="2" colspan="2">
        <img class="multikill_icon" src="/images/achievements/multi_kill/multikill_image.png" />
      </th>
      <th colspan="6" class="multikill_title">
        Multi Kill
      </th>
    </tr>
    <tr>

      <th colspan="6" class="multikill_description last">
        Number of kills with dead in a round
      </th>
    </tr>
  </thead>
  <tbody>
    % for i, item in enumerate(multikill_list.items()):
      <% k, v = item %>
      % if i % 8 == 0:
        <tr>
      % endif
      % if i % 8 == 7:
        <td class="last">
      % else:
        <td>
      % endif
      <span class="multikill_subtitle">${v[0]}</span>
      <br/>
      ${k} kills
      </td>
      % if i % 8 == 7:
        </tr>
      % endif
    % endfor
  </tbody>
</table>

