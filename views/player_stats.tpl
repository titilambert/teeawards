<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

${lib.search_player()}

<div class="statstitle">
    Stats for ${player}
</div>

<div class="statscard">
<div class="profilecard">
  <table>
    <thead>
      <tr>
        <th colspan="2">
          General Statistics
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="dataname">
          Name
        </td>
        <td class="datavalue">
          ${player}
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Score
        </td>
        <td class="datavalue">
          ${score} points
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Ratio
        </td>
        <td class="datavalue">
          ${"%0.2f" % ratio} Kills/deaths
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Kills
        </td>
        <td class="datavalue">
          ${kills} kills
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Death
        </td>
        <td class="datavalue">
          ${deaths} deaths
        </td>
      </tr>
    </body>
  </table>
</div>
</div>

<div class="statscard">
<table class="weaponstats">
  <thead>
    <tr>
      <th colspan="10">
        Kills Weapons Stats
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit':
        <td>
          <a href="/item_stats/${w}">${w}</a>
        </td>
        % endif
      %endfor
    </tr>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit':
          <td>
            % if w in kstats['weapon']:
              ${kstats['weapon'][w]}
            % else:
              0
            % endif
          </td>
        % endif
      %endfor
    </tr>
  </tbody>
</table>
</div>

<div class="statscard">
<table class="weaponstats">
  <thead>
    <tr>
      <th colspan="10">
        Deaths Weapons Stats
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit':
        <td>
          <a href="/item_stats/${w}">${w}</a>
        </td>
        % endif
      %endfor
    </tr>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit':
          <td>
            % if w in vstats['weapon']:
              ${vstats['weapon'][w]}
            % else:
              0
            % endif
          </td>
        % endif
      %endfor
    </tr>
  </tbody>
</table>
</div>

<div class="statscard">
<div class="profilecard favorites">
  <table>
    <thead>
      <tr>
        <th colspan="3">
          Favorites
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="dataname">
          Weapon
        </td>
        <td class="image">
          <img src="/images/weapon/${favorite_weapon[0]}.png" />
        </td>
        <td class="datavalue">
          ${favorite_weapon[1]} ${favorite_weapon[0]} kills
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Victim
        </td>
        <td class="image">
          <img src="/images/favorites/victim.png" />
        </td>
        <td class="datavalue">
          <span>You killed</span>
          <br/>
          <a href="/player_stats/${favorite_victim[0]}">${favorite_victim[0]}</a>
          <br/>
          <span>${favorite_victim[1]} times</span>
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Killer
        </td>
        <td class="image">
          <img src="/images/favorites/killer.jpg" />
        </td>
        <td class="datavalue">
          <a href="/player_stats/${favorite_killer[0]}"> ${favorite_killer[0]}</a>
          <br/>
          <span>killed YOU ${favorite_killer[1]} times</span>
        </td>
      </tr>
    </body>
  </table>
</div>
</div>






<div class="statscard">
<table class="weaponstats">
  <thead>
    <tr>
      <th colspan="10">
        Picked up items stats
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      %for i in pickup_mapping:
        <td>
          <a href="/item_stats/${i}">${i}</a>
        </td>
      %endfor
    </tr>
    <tr>
      %for i in pickup_mapping:
          <td>
            % if i in pstats:
              ${pstats[i]}
            % else:
              0
            % endif
          </td>
      %endfor
    </tr>
  </tbody>
</table>
</div>

<div style="clear: both">
</div>

