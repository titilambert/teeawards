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
          Map name
        </td>
        <td>
          <input name="map_name" type="text" value="${map['map']['map_name'].decode('utf-8') if map else ''}" />
        </td>
      </tr>
      <tr>
        <td>
          Map file
        </td>
        <td>
          <input name="map_file" type="file" value="" />
        </td>
      </tr>
      <tr>
        <td>
          Minimum players
        </td>
        <td>
          <input name="min_players" type="text" value="${map['map']['min_players'].decode('utf-8') if map else '0'}" />
        </td>
      </tr>
      <tr>
        <td>
          Maximum players
        </td>
        <td>
          <input name="max_players" type="text" value="${map['map']['max_players'].decode('utf-8') if map else '32'}" />
        </td>
      </tr>
      <tr>
        <td>
          Best mod for this map
        </td>
        <td>
          <input name="prefered_mod" type="text" value="${map['map']['prefered_mod'].decode('utf-8') if map else 'dm'}" />
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
  <button>Add map</button>
</form> 
