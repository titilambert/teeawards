<link rel="stylesheet" type="text/css" href="/css/achievements/medals/medals.css"/>
<table class="medals_desc_achievement achievements">
  <thead>
    <tr>
      <th class="medals_title" colspan="10">
        Medals
      </th>
    </tr>
  </thead>
  <tbody>
    % for i, t in enumerate(medal_list):
      <% medal, desc = t %>
      % if i % 3 == 0:
        <tr>
      % endif
        <td class="medal_image">
            <img class="badge" src="/images/achievements/medals/${medal}.jpg" >
        </td>
      % if i % 3 == 2:
        <td class="last descr">
      % else:
        <td class="descr">
      % endif
          <br/>
          <span class="medal_name">${medal.capitalize()}</span>
          <ul>
            <li>${desc}</li>
          </ul>
        </td>
      % if i % 3 == 2:
        </tr>
      % endif

    % endfor
  </tbody>
</table>
