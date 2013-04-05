<table class="multikill_achievement achievements">
  <thead>
    <tr>
      <th colspan="10">
        Multi Kill
      </th>
    </tr>
  </thead>
  <tbody>
    <% datas = sorted([x for x in multikill_list.items()], key=lambda x: x[0]) %>
    % for number, data in datas:
      <tr>
        <td>
          ${data[0]}
          <br/>
          <span style="font-size: 8px;">${number} kills without dead</span>
        </td>
        <td class="last">
          ${data[1]}
        </td>
      </tr>
    % endfor
  </tbody>
</table>

