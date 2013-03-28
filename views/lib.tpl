<%def name="header(title='TeeStats')">
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" type="text/css" href="/css/teestats.css">
    <link rel="shortcut icon" href="/images/favicon.ico" type="image/ico">
    ##<script src="js/checkmk.js" type="text/javascript"></script>
    ##<script src="js/hover.js" type="text/javascript"></script>
    <title>
      ${title.capitalize()}
    </title>
  </head>
  <body>
    <div id="outer">
      <div id="top_left">
        <div id="top_right">
          <div id="top_mid">
            <div class="teeawards_title">
              <a href="/">
                <img class="logo"  src="/images/teeawards-logo.png" alt="tee-awards logo">
              </a>
            </div>
            <div class="serverstatus" >
              % if fullserverstatus:
                <div style="color:#7fd538">
                  Server ONLINE
                  <br/>
                  <img class="logo"  src="/images/greendot.png" alt="online"><br/>
                  Game: ${gametype}
                  <br/>
                  <span title='${playernames}'>
                    % if fullserverstatus['num_players'] > 1:
                      ${fullserverstatus['num_players']} players online
                    % else:
                      ${fullserverstatus['num_players']} player online
                    % endif
                  </span>
                </div>
              % else:
                <div style="color:#fd778a">
                  Server offline
                  <br/>
                  <img class="logo"  src="/images/reddot.png" alt="offline">
                </div>
              % endif
            </div>

          </div>
        </div>
      </div>

</%def>

<%def name="footer()">
      <div id="blc">
        <div id="brc">
          <div id="bb"> </div>
        </div>
      </div>
    </div>
    <div id="page_foot">
      TeeWorlds Stats - Awards - Copyright (C) Thibault cohen - 
      <a href="/">Contact us!</a>
    </div>
  </body>
</html>
</%def>

<%def name="main_menu(selected_tab='home')">
<div id="menu_left">
  <div id="menu_right">
    <div id="menu_mid">
      <div id="menu">
        <ul>
          % for tab in ['admin', 'maps', 'achievements', 'ranks', 'items', 'ladder', 'home']:
            % if tab == selected_tab:
              <li id="current">
            % else:
              <li>
            % endif
              <a href="/${tab}">${tab.capitalize()}</a>
            </li>
          %endfor
        </ul>
      </div>
    </div>
  </div>
</div>
<div id="tlc">
  <div id="trc">
    <div id="tb"> </div>
  </div>
</div>
</%def>

<%def name="search_player()">
<div id="search_player"> 
  <form method="post" name="search_player" action="/player_stats"> 
     <label>Search for player stats : </label> 
     <input name="player" text="" /> 
  </form> 
</div>
</%def>
