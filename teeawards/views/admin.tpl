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
            <option value="${conf['_id']}">${conf['name'].decode('utf-8')}</option>
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
          % for player in v:
            <form action="/admin/kick/${player['name']}" method="post">
              ${player['name']}
              <button>Kick</button>
            </form>
          % endfor
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
              ${conf['name'].decode('utf-8')}
            </td>
            <td>
              <a href="/admin/conf/edit/${conf['_id']}">Edit</a>
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
              <a href="/maps#${map_['name']}">${map_['name'].decode('utf-8')}</a>
            </td>
            <td>
              ${map_['map']['min_players'].decode('utf-8')}
            </td>
            <td>
              ${map_['map']['max_players'].decode('utf-8')}
            </td>
            <td>
              ${map_['map']['prefered_mod'].decode('utf-8')}
            </td>
            <td>
              ${map_['map']['likes'] if 'like' in map_['map'] else '0'}
            </td>
            <td>
              <a href="/admin/map/edit/${map_['_id']}">Edit</a>
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
</div>



<div>
  <table>
  <head>
    <tr>
      <th colspan="4">
        Administration
      </th>
    </tr>
  </head>
  <body>
    <tr>
      <form action="/admin/export" method="post">
        <td>
          Export data
        </td>
        <td>
          <span class="export_stats">
            <label>Export stats</label>
            <input type="checkbox" name="stats" />
          </span>
        </td>
        <td>
          <button >Export data</button>
        </td>
      </form>
    </tr>
    <tr>
      <form action="/admin/restore" method="post" enctype="multipart/form-data">
        <td>
          Restore data
        </td>
        <td>
          <input type="file" name="dumpfile" />
        </td>
        <td>
          <button >Restore data</button>
        </td>
      </form>
    </tr>
    <tr>
      <td>
      <form action="/admin/reset_data" method="post">
        <button onclick='return reset_confirm();' >Reset stats</button>
        <script type'text/javascript'>
function reset_confirm() {
    var r = confirm("You're going to RESET ALL STATS !\nAre you sure ?")
    if ( r == true ) {
        var c = confirm("Are you really really sure to RESET ALL STATS !?")
        if ( c == true ) {
            alert("OK, OK...  ALL STATS WILL BE DELETE ...");
            return true;
        }
        return false;
    }
    else {
        return false;
    }
}
        </script>
      </form>
      </td>
    </tr>
  </body>
  </table>
</div>

