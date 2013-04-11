<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<table class="maps">
  <thead>
    <tr>
      <th colspan="5">
        Maps
        <form method="post" action="/maps">
        <label>Game type : </label>
        <select onchange="submit();" name="gametype">
            <option value="">All</option>
          % for mod in mods:
            <option ${'selected=selected' if selected_mod == mod else ''} value="${mod}">${mod}</option>
          % endfor
        </select>
        </form>
      </th>
  </thead>
  <tbody>
    %for map_ in map_list:
      <tr id="${map_['name']}">
        <td class="info">
          <div class="title">${map_['name']}</div>
          <br/>
          Best mod: ${map_['map']['prefered_mod']}
          <br/>
          Min players: ${map_['map']['min_players']}
          <br/>
          Max players: ${map_['map']['max_players']}
          <br/>
        </td>
        <td class="map_screenshot">
          % if 'screenshot' in map_['map']:
             <img src="/map_screenshots/${map_['map']['screenshot']}" >
          % endif
        </td>
      </tr>
    %endfor
  </tbody>
</table>
