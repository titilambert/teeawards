<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
</div>

% if engine_settings and game_settings:
  <form name="new_conf" method="post" action="/admin/conf/edit/${id}">
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

