<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

${lib.search_player()}

% if not_found:
    <div class="error">
    Player '${not_found}' not found
    </div>
%else:

<div class="statstitle">
  <div class="imagerank">
    <img src="/images/ranks/rank_${rank[0]}.jpg" />
  </div>
  "${rank[1]}"<br/> ${player}
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
          Rounds
        </td>
        <td class="datavalue">
          ${rounds} rounds
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
      <tr>
        <td class="dataname">
          Suicide
        </td>
        <td class="datavalue">
          ${suicides} suicides
        </td>
      </tr>
      <tr>
        <td class="dataname">
          TeamKills
        </td>
        <td class="datavalue">
          ${teamkills} teamkills
        </td>
      </tr>
    </body>
  </table>
</div>
</div>

% if kills_by_weapons:
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
        % if w != 'exit' and w != 'death fall':
        <td>
          <a href="/items#${w}">${w}</a>
        </td>
        % endif
      %endfor
    </tr>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit' and w != 'death fall':
          <td>
            % if w in kills_by_weapons:
              ${kills_by_weapons[w]}
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
% endif

% if deaths_by_weapons:
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
          <a href="/items#${w}">${w}</a>
        </td>
        % endif
      %endfor
    </tr>
    <tr>
      %for w in kill_mapping:
        % if w != 'exit':
          <td>
            % if w in deaths_by_weapons:
              ${deaths_by_weapons[w]}
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
% endif


<div style="clear: both">
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
      % if favorite_weapon:
      <tr>
        <td class="dataname">
          Weapon
        </td>
        <td class="image">
          <img src="/images/weapon/${favorite_weapon[0]}.png" alt="${favorite_weapon[0]}"/>
        </td>
        <td class="datavalue">
          ${favorite_weapon[1]} ${favorite_weapon[0]} kills
        </td>
      </tr>
      % endif
      % if favorite_victim:
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
      % endif
      % if favorite_killer:
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
      % endif
      % if favorite_map:
      <tr>
        <% map_name = favorite_map[0].split(".", 1)[0] %>
        <td class="dataname">
          Map
        </td>
        <td class="image">
          <img src="/map_screenshots/${map_list[map_name].get('screenshot', '')}" alt="${map_name}" />
        </td>
        <td class="datavalue">
          You played ${favorite_map[1]} rounds on ${map_name}
        </td>
      </tr>
      % endif
    </body>
  </table>
</div>
</div>

% if selected_gametype in ['ctf', 'all']:
<div class="statscard">
<div class="profilecard">
  <table>
    <thead>
      <tr>
        <th colspan="2">
          CTF Statistics
        </th>
      </tr>
    </thead>
    <body>
      <tr>
        <td class="dataname">
          Flag grabs
        </td>
        <td class="datavalue">
          ${flaggrab} flag grab
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Flag return
        </td>
        <td class="datavalue">
          ${flagreturn} flag return
        </td>
      </tr>
      <tr>
        <td class="dataname">
          Flag capture
        </td>
        <td class="datavalue">
          ${flagcapture} flag capture
        </td>
      </tr>
    </body>
  </table>
</div>
</div>
% endif




% if item_stats:
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
          <a href="/items#${i}">${i}</a>
        </td>
      %endfor
    </tr>
    <tr>
      %for i in pickup_mapping:
          <td>
            % if i in item_stats:
              ${item_stats[i]}
            % else:
              0
            % endif
          </td>
      %endfor
    </tr>
  </tbody>
</table>
</div>
% endif

<div class="statscard">
<table class="nextrank">
  <thead>
    <tr>
      <th colspan="10">
        Progress towards Next Rank
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="image">
        <img src="/images/ranks/rank_${nextrank[0]}.jpg" />
      </td>
      <td class="requirements last">
        <strong>
            Next rank: ${nextrank[1]}:
        </strong>
        <% prct = 100 * (score - rank[2]) / float(nextrank[2] - rank[2]) %>
        <% prct = prct if prct > 0 else 0 %>
        <div class="progressbar">
            <div class="progress" style="width: ${prct}%">${"%0.2f" % prct}%</div>
        </div>
        <br/>
        Current Global Score: ${score} of ${nextrank[2]}. Remaining points: ${nextrank[2] - score}.
      </td>
    </tr>
  </tbody>
</table>
</div>

<div style="clear: both">

<div class="statscard achievement_div_title">
<table class="achievement_title">
  <thead>
    <tr>
      <th colspan="10">
        Achievements
      </th>
    </tr>
  </thead>
</table>
</div>

<div style="clear: both">

% for a, data in achievement_list.items():
  <div class="achievement">
    ${data}
  </div>
% endfor

<div style="clear: both">
<div style="clear: both">
<br/>

% endif
