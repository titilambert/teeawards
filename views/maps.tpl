<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<table class="maps">
  <thead>
    <tr>
      <th colspan="5">
        Maps
      </th>
  </thead>
  <tbody>
    %for map_ in map_list:
      <tr>
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
