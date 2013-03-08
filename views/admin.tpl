<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
</div>

<% configlist = [x for x in config_list] %>
% if server_alive:
  <form name="toggle_server" method="post" action="/admin/toggle_server">
    <input type="hidden" value="stop" name="toggle_server" />
    <button>Stop server</button>
  </form>
% else:
  <form name="toggle_server" method="post" action="/admin/toggle_server">
    <select name="config">
      % for conf in configlist:
        <option value="${conf['name']}">${conf['name']}</option>
      % endfor
    </select>
    <input type="hidden" value="start" name="toggle_server" />
    <button>Start server</button>
  </form>
% endif


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
      % for conf in configlist:
          <tr>
            <td>
              ${conf['name']}
            </td>
            <td>
              <a href="/admin/conf/edit/${conf['name']}">Edit</a>
            </td>
            <td>
              <a href="/admin/conf/delete/${conf['_id']}">Delete</a>
            </td>
          </tr>
      % endfor
      <tr>
        <td>
          <a href="/admin/conf/edit">New conf</a>
        </td>
      </tr>
    </tbody>
  </table>

</div>

<div>
    Server status ${fullserverstatus}
</div>


