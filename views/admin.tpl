<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div class="statstitle">
    Admin page
</div>

<table class="servermanager">
<thead>
  <tr><th colspan="3">
    Server Manager
  </td></th>
</thead>
<tbody>
  <tr>
    <% configlist = [x for x in config_list] %>
    % if server_alive:
    <td>
      ${fullserverstatus['name']}
    </td>
    <td class="last">
      <form name="toggle_server" method="post" action="/admin/toggle_server">
        <input type="hidden" value="stop" name="toggle_server" />
        <button>Stop server</button>
      </form>
    </td>
    % else:
    <form name="toggle_server" method="post" action="/admin/toggle_server">
    <td>
        <select name="config">
          % for conf in configlist:
            <option value="${conf['name']}">${conf['name']}</option>
          % endfor
        </select>
    </td>
    <td class="last">
      <input type="hidden" value="start" name="toggle_server" />
      <button>Start server</button>
    </td>
    </form>
% endif
</td></td>
<tbody>
</table>


% if fullserverstatus:
<table class="serverstatus">
  <thead>
    <tr>
      <th colspan="40">
        Server Status
      </th>
    </tr>
  </thead>
  <tbody>
    % for k, v in fullserverstatus.items():
      <tr>
        <td>
            ${k.capitalize()}
        </td>
        <td class="last">
        % if k == 'players':
          ${"<br/>".join([p['name'] for p in v])}
        % else:
          ${v}
        % endif
        </td>
      </tr>
    %endfor
  </tbody>
</table>
% endif


<div>
  <table class="configlist">
    <thead>
        <tr>
          <th colspan="20">
            Configurations
          </th>
        </tr>
    </thead>
    <tbody>
      % for conf in configlist:
          <tr>
            <td>
              ${conf['name']}
            </td>
            <td>
              <a href="/admin/conf/edit/${conf['name']}">Edit</a>
            </td>
            <td class="last">
              <a href="/admin/conf/delete/${conf['_id']}">Delete</a>
            </td>
          </tr>
      % endfor
      <tr>
        <td colspan="3" class="last">
          <a href="/admin/conf/edit">New conf</a>
        </td>
      </tr>
    </tbody>
  </table>
</div>


<div>
    <table class="maplist">
    <thead>
        <tr>
          <th colspan="20">
           Maps
          </th>
        </tr>
        <tr class="subhead">
          <th>
           Map name
          </th>
          <th>
           Min player
          </th>
          <th>
           Max player
          </th>
          <th>
           Best mode
          </th>
          <th>
           Likes
          </th>
          <th colspan="2">
           Actions
          </th>
        </tr>
    </thead>
    <tbody>
      % for map_ in map_list:
          <tr>
            <td>
              <a href="/maps#${map_['name']}">${map_['name']}</a>
            </td>
            <td>
              ${map_['map']['min_players']}
            </td>
            <td>
              ${map_['map']['max_players']}
            </td>
            <td>
              ${map_['map']['prefered_mod']}
            </td>
            <td>
              ${map_['map']['likes'] if 'like' in map_['map'] else '0'}
            </td>
            <td>
              <a href="/admin/map/edit/${map_['name']}">Edit</a>
            </td>
            <td class="last">
              <a href="/admin/map/delete/${map_['_id']}">Delete</a>
            </td>
          </tr>
      % endfor
      <tr>
        <td colspan="9" class="last">
          <a href="/admin/map/edit">New map</a>
        </td>
      </tr>
    </tbody>
  </table>
  <div>
    <form action="/admin/reset_data">
    <button >Reset data</button>
    </form>
  </div>
</div>

