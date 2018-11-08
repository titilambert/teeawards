<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

<table class="ranklist">
  <tbody>
    % for level, rank in enumerate(ranks):
    <tr>
      <th colspan="2">
        ${rank[0]}
      </th>
    </tr>
    <tr>
      <td class="image">
        <img src="/images/ranks/rank_${level}.jpg" />
      </td>
      <td class="requirements">
        <strong>Requirements: </strong>
        <ul>
          <li>
            Score: ${'{0:,}'.format(rank[1]).replace(",", " ")}
          </li>
        </ul>
      </td>
    </tr>
    %endfor
  </tbody>
</table>
