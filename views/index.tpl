<%namespace name="lib" file="lib.tpl" inheritable="True" />

<%inherit file="base.tpl" />

${lib.search_player()}


<div class="card">
  <div class="title">
    Best Score
  </div>
  <div class="img">
    <img src="/images/card/best_score.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_score[0]}">${best_score[0]}</a></div>
    <div class="score">${best_score[1]} points</div>
  </div> 
</div>



<div class="card">
  <div class="title">
    Best Killer
  </div>
  <div class="img">
    <img src="/images/card/best_killer.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_killer[0]}">${best_killer[0]}</a></div>
    <div class="score">${best_killer[1]} kills</div>
  </div> 
</div>



<div class="card">
  <div class="title">
    Best Ratio
  </div>
  <div class="img">
    <img src="/images/card/best_ratio.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_ratio[0]}">${best_ratio[0]}</a></div>
    <div class="score">${best_ratio[1]} Kills/Deaths</div>
  </div> 
</div>

<div class="card">
  <div class="title">
    Best Suicider
  </div>
  <div class="img">
    <img src="/images/card/best_suicider.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_ratio[0]}">${best_suicider[0]}</a></div>
    <div class="score">${best_suicider[1]} suicides</div>
  </div> 
</div>

<div class="card">
  <div class="title">
    Best Victim
  </div>
  <div class="img">
    <img src="/images/card/best_victim.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_victim[0]}">${best_victim[0]}</a></div>
    <div class="score">${best_victim[1]} deaths</div>
  </div> 
</div>

<div class="card">
  <div class="title">
    Hammer Lover
  </div>
  <div class="img">
    <img src="/images/card/best_hammer_victim.png" />
&nbsp;
  </div>
  <div class="data">
    <div class="player"><a href="/player_stats/${best_hammer_victim[0]}">${best_victim[0]}</a></div>
    <div class="score">${best_hammer_victim[1]} hammer deaths</div>
  </div> 
</div>

<div style="clear: both">
</div>
