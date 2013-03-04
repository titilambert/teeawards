<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<table>
  <thead>
    <tr>
      <th>
        Stats
      </th>
      %for i in xrange(max([len(x) for x in stats.values()])):
      <th>
        #${i + 1}
      </th>
      %endfor
    </tr>
  </thead>
  <tbody>
    %for stat, data in stats.items():
    <% sorted_data = sorted([x for x in data.items()], key=lambda x: x[1], reverse=True) %>
      <tr>
        <td>
          ${stat.capitalize()}
        </td>
        % for player, nb in sorted_data:
        <td>
            ${player}<br/>${nb}
        </td>
        % endfor
      </tr>
    %endfor

  </tbody>
</table>
