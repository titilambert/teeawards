<link rel="stylesheet" type="text/css" href="/css/achievements/badges/badges.css"/>
<table class="badges_achievement achievements">
  <thead>
    <tr>
      <th class="badges_title" colspan="10">
        Badges
      </th>
    </tr>
  </thead>
  <tbody>
    % for badge, stat in results.items():
      <tr>
        <td class="badge_title">
          ${badge}
        </td>
        % for i in xrange(1, 4): 
        <td ${ 'class="last"' if i == 3 else ''}>
          % if stat >= i :
            <img class="badge" src="/images/achievements/badges/${badge}_${i}.png" >
          % else:
            <img class="badge badge_notok" src="/images/achievements/badges/${badge}_${i}.png" >
          % endif
        </td>
        % endfor
      </tr>
    % endfor
  </tbody>
</table>

