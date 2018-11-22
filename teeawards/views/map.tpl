<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
</div>

% if id_ is not None:
<form enctype="multipart/form-data" name="new_conf" method="post" action="/admin/map/edit/${id_}">
% else:
<form enctype="multipart/form-data" name="new_conf" method="post" action="/admin/map/edit">
% endif
    % if map:
    <button>Save map</button>
    % else:
    <button>Add map</button>
    % endif
    <table>
      <thead>
        <tr>
          <th colspan="20">
            % if map:
              Edit map ${map['map_name']}
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
          % if map:
            ${map['map_name']}
          <input name="map_name" type="hidden" value="${map['map_name']}" />
          % else:
          <input name="map_name" type="text" value="${map['map_name']}" />
          % endif
        </td>
      </tr>
      <tr>
        <td>
          Map file
          % if map:
         <br>
          % endif
        </td>
        <td>
        % if map:
         <strong>${map['map_name']}.map</strong>
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
          <input name="min_players" type="text" value="${map['min_players'] if map else '0'}" />
        </td>
      </tr>
      <tr>
        <td>
          Maximum players
        </td>
        <td>
          <input name="max_players" type="text" value="${map['max_players'] if map else '32'}" />
        </td>
      </tr>
      <tr>
        <td>
          Best mod for this map
        </td>
        <td>
          <input name="prefered_mod" type="text" value="${map['prefered_mod'] if map else 'dm'}" />
        </td>
      </tr>
      <tr>
        <td>
          Screenshot
        </td>
        <td>
          <input name="screenshot" type="file" value="" />
          % if map:
          No file means no change
          % endif
        </td>
      </tr>
    </table>
    % if map:
    <button>Save map</button>
    % else:
    <button>Add map</button>
    % endif
</form> 
