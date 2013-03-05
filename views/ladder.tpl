<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<table class="ladder">
  <thead>
    <tr>
      <th>
        Ranking
      </th>
      <th ${'class="sorted"' if sort == 'nickname' else ''} >
        <a href="/ladder/nickname">Nick Name</a>
      </th>
      <th ${'class="sorted"' if sort == 'score' else ''} >
        <a href="/ladder/score">Score</a>
      </th>
      <th ${'class="sorted"' if sort == 'ratio' else ''} >
        <a href="/ladder/ratio">Ratio K/D</a>
      </th>
      <th ${'class="sorted"' if sort == 'kills' else ''} >
        <a href="/ladder/kills">Kills</a>
      </th>
      <th ${'class="sorted"' if sort == 'deaths' else ''} >
        <a href="/ladder/deaths">Deaths</a>
      </th>
      <th ${'class="sorted"' if sort == 'suicides' else ''} >
        <a href="/ladder/suicides">Suicides</a>
      </th>
    </tr>
  </thead>
  <tbody>
    %for i, data in enumerate(stats_by_players):
    <% player, stats = data %>
      <tr>
        <td>
          #${i}
        </td>
        <td class="nickname">
          <img src="/images/ranks/rank_${stats['rank']}.gif" />
          <a href="/player_stats/${player}" >${player}</a>
        </td>
        <td>
          ${stats['score']}
        </td>
        <td>
          ${"%0.2f" % stats['ratio']}
        </td>
        <td>
          ${stats['kills']}
        </td>
        <td>
          ${stats['deaths']}
        </td>
        <td class="last">
          ${stats['suicides']}
        </td>
      </tr>
    %endfor
  </tbody>
</table>
