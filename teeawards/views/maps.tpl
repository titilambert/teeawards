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
            <option ${'selected=selected' if selected_mod.encode('utf-8') == mod else ''} value="${mod.decode('utf-8')}">${mod.decode('utf-8')}</option>
          % endfor
        </select>
        </form>
      </th>
  </thead>
  <tbody>
    %for map_ in map_list:
      <tr id="${map_['name'].decode('utf-8')}">
        <td class="info">
          <div class="title">${map_['name'].decode('utf-8')}</div>
          <br/>
          Best mod: ${map_['map']['prefered_mod'].decode('utf-8')}
          <br/>
          Min players: ${map_['map']['min_players'].decode('utf-8')}
          <br/>
          Max players: ${map_['map']['max_players'].decode('utf-8')}
          <br/>
        </td>
        <td class="map_screenshot">
             <img src="/map_screenshots/${map_['_id']}" >
        </td>
      </tr>
    %endfor
  </tbody>
</table>
