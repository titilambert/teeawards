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
      <tr id="${map_['map_name']}">
        <td class="info">
          <div class="title">${map_['map_name']}</div>
          <br/>
          Best mod: ${map_['prefered_mod']}
          <br/>
          Min players: ${map_['min_players']}
          <br/>
          Max players: ${map_['max_players']}
          <br/>
        </td>
        <td class="map_screenshot">
          <img src="/map/${map_['map_name']}/screenshot" >
        </td>
      </tr>
    %endfor
  </tbody>
</table>
