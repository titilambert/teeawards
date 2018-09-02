<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />


% for i, item in enumerate(items):
<% item_name = itemlist[i] %>
<table class="itemstats" id="${item_name}">
  <thead>
    <tr>
      <th>
        ${item_name.capitalize()} Stats
      </th>
      %for i in xrange(min(max([len(x) for x in item.values()]),7)):
      <th>
        #${i + 1}
      </th>
      %endfor
    </tr>
  </thead>
  <tbody>
  <% sorted_items = sorted(item.keys(), reverse=True) %>
    %for stat in sorted_items:
      <% sorted_data = sorted([x for x in item[stat].items()], key=lambda x: x[1], reverse=True) %>
      <tr>
        <td class="statname">
          ${stat.capitalize()}
        </td>
        % for player, nb in sorted_data[:7]:
        <td class="last">
            <a href="/player_stats/${player}">${player}</a><br/>Count: ${nb}
        </td>
        % endfor
      </tr>
    %endfor
  </tbody>
</table>

%endfor
