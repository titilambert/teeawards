<link rel="stylesheet" type="text/css" href="/css/achievements/medals/medals.css"/>
<table class="medals_achievement achievements">
  <thead>
    <tr>
      <th class="medals_title" colspan="10">
        Medals
      </th>
    </tr>
  </thead>
  <tbody>
    % for medal, desc in medals_list:
      <% stat = results.get(medal, 0) %>
      <tr>
        <td class="medal_title">
          <span class="title" >${medal.capitalize()}</span>
          <br/>
          <span class="nb_medals">${stat} medals</span>
          <br/>
          <span class="desc" >${desc}</span>
        </td>
        <td class="last" >
          % if stat > 0 :
            <img class="medal" src="/images/achievements/medals/${medal}.jpg" >
          % else:
            <img class="medal medal_notok" src="/images/achievements/medals/${medal}.jpg" >
          % endif
        </td>
      </tr>
    % endfor
  </tbody>
</table>

