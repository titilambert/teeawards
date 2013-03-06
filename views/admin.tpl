<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<div>
    Admin page
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
