<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
</div>

<div>
    <a href="/admin/new">New conf</a>
</div>


<div>
  <table>
    <thead>
        <tr>
          <th colspan="20">
            Configurations
          </th>
        </tr>
    </thead>
    <tbody>
      % for conf in config_list:
          <tr>
            <td>
              ${conf['name']}
            </td>
            <td>
              <a href="/admin/conf/edit/${conf['_id']}">Edit</a>
            </td>
            <td>
              <a href="/admin/conf/delete/${conf['_id']}">Delete</a>
            </td>
          </tr>
      % endfor
    </tbody>
  </table>

</div>

<div>
    Server status ${server_alive}
</div>

% if server_alive:
  <form name="toggle_server" method="post" action="/admin">
    <input type="hidden" value="stop" name="toggle_server" />
    <button>Stop server</button>
  </form>
% else:
  <form name="toggle_server" method="post" action="/admin">
    <input type="hidden" value="start" name="toggle_server" />
    <button>Start server</button>
  </form>
% endif


% if engine_settings and game_settings:
  <form name="new_conf" method="post" action="/admin/new">
    <button>Save configuration</button>
    <table>
      <thead>
        <tr>
          <th colspan="20">
            Engine settings
          </th>
        </tr>
      </thead>
    % for setting in engine_settings:
      <tr>
        <td>
          ${setting[1]}
        </td>
        <td>
          <input name="${setting[0]}" type="text" value="${setting[2]}" />
        </td>
      </tr>
    % endfor
    </table>
    <table>
      <thead>
        <tr>
          <th colspan="20">
            Game settings
          </th>
        </tr>
      </thead>
    % for setting in game_settings:
      <tr>
        <td>
          ${setting[1]}
        </td>
        <td>
          <input name="${setting[0]}" type="text" value="${setting[2]}" />
        </td>
      </tr>
    % endfor
    </table>
    <button>Save configuration</button>
  </form> 
% endif

