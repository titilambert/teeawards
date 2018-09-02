<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
</div>

<form enctype="multipart/form-data" name="new_conf" method="post" action="/admin/map/edit/${id}">
  <button>Add map</button>
    <table>
      <thead>
        <tr>
          <th colspan="20">
            % if map:
              Edit map ${map['name']}
            % else:
              Add map
            % endif
          </th>
        </tr>
      </thead>
      <tr>
        <td>
          Map file
          % if map:
         <br>
          % endif
        </td>
        <td>
        % if map:
         Map filename: <strong>${map['name']}.map</strong>
        % else:
          <input name="map_file" type="file" value="" />
        % endif
        </td>
      </tr>
      <tr>
        <td>
          Minimum players
        </td>
        <td>
          <input name="min_players" type="text" value="${map['map']['min_players'] if map else '0'}" />
        </td>
      </tr>
      <tr>
        <td>
          Maximum players
        </td>
        <td>
          <input name="max_players" type="text" value="${map['map']['max_players'] if map else '32'}" />
        </td>
      </tr>
      <tr>
        <td>
          Best mod for this map
        </td>
        <td>
          <input name="prefered_mod" type="text" value="${map['map']['prefered_mod'] if map else 'dm'}" />
        </td>
      </tr>
      <tr>
        <td>
          Screenshot
        </td>
        <td>
          <input name="screenshot" type="file" value="" />
        </td>
      </tr>
    </table>
  % if map:
  <input name="map_name" type="hidden" value="${map['name']}" />
  % endif
  <button>Add map</button>
</form> 
