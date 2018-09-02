<link rel="stylesheet" type="text/css" href="/css/achievements/badges/badges.css"/>
<table class="badges_desc_achievement achievements">
  <thead>
    <tr>
      <th class="badges_title" colspan="10">
        Badges
      </th>
    </tr>
  </thead>
  <tbody>
    % for i, t in enumerate(badge_list):
      <% badge, limits = t %>
      % if i % 3 == 0:
        <tr>
      % endif
        <td class="badge_image">
            <img class="badge" src="/images/achievements/badges/${badge}_3.png" >
        </td>
      % if i % 3 == 2:
        <td class="last descr">
      % else:
        <td class="descr">
      % endif
          <br/>
          <span class="badge_name">${badge.capitalize()}</span>
          <ul>
          % for i, metal in enumerate(['bronze', 'silver', 'gold']):
            <li>${metal}: ${limits[i]}</li>
          % endfor
          </ul>
        </td>
      % if i % 3 == 1:
        </tr>
      % endif

    % endfor
  </tbody>
</table>
