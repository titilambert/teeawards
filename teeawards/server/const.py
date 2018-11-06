ENGINE_SETTINGS = [
    ('sv_name', 'Name of the server', 'unnamed server'),
    ('sv_bindaddr', 'Address to bind', ''),
    ('sv_port', 'Port the server will listen on', '8303'),
    ('sv_external_port', 'Port to report to the master servers (e.g. in case of a firewall rename)','0'),
    ('sv_max_clients', 'Number of clients that can be connected to the server at the same time', '12'),
    ('sv_max_clients_per_ip', 'Number of clients with the same ip that can be connected to the server at the same time', '12'),
    ('sv_high_bandwidth', 'Use high bandwidth mode, for LAN servers only', '1'),
    ('sv_register', 'Register on the master servers', '0'),
    ('sv_map', 'Map to use', 'dm1'),
    ('sv_rcon_password', 'Password to access the remote console (if not set, rcon is disabled)', ''),
    ('password', 'Password to connect to the server', ''),
    ('logfile', 'Path to a logfile', ''),
    ('console_output_level', 'Adjust the amount of messages in the console', '0'),
    ('sv_rcon_max_tries', 'Maximum number of tries for remote console authetication', '3'),
    ('sv_rcon_bantime', 'Time (in minutes) a client gets banned if remote console authentication fails (0 makes it just use kick)', '5'),
]

GAME_SETTINGS = [
    ('sv_warmup', 'Warmup time between rounds', '0'),
    ('sv_scorelimit', 'Score limit of the game (0 disables it)', '20'),
    ('sv_timelimit', 'Time limit of the game (in case of equal points there will be sudden death)', '0'),
    ('sv_gametype', 'Gametype (dm/ctf/tdm) (This setting needs the map to be reloaded in order to take effect)', 'dm'),
    ('sv_maprotation', 'The maps to be rotated', ''),
    ('sv_rounds_per_map', 'Number of rounds before changing to next map in rotation', '1'),
    ('sv_motd', ' Message of the day, shown in server info and when joining a server', ''),
    ('sv_spectator_slots', 'Number of clients that can only be spectators', '0'),
    ('sv_teambalance_time', 'Time in minutes after the teams are uneven, to auto balance', '1'),
    ('sv_spamprotection', 'Enable spam filter', 'False'),
    ('sv_tournament_mode', 'Players will automatically join as spectator', '0'),
    ('sv_respawn_delay_tdm', 'Time in seconds needed to respawn in the tdm gametype', '3'),
    ('sv_teamdamage', 'Enable friendly fire', '1'),
    ('sv_powerups', 'Enable powerups (katana)', '1'),
    ('sv_vote_kick', 'Enable kick voting', '1'),
    ('sv_vote_kick_bantime', 'Time in minutes to ban a player if kicked by voting (0 equals only kick)', '5'),
    ('sv_vote_kick_min', 'Minimum number of players required to start a kick vote', '0'),
    ('sv_inactivekick_time', 'Time in minutes after an inactive player will be taken care of', '3'),
    ('sv_inactivekick', 'How to deal with inactive players (0 = move to spectator, 1 = move to free spectator slot/kick, 2 = kick)', '1'),
]   

OTHER_SETTINGS = [
    ('server_binary', 'Server Binary (empty means use system binary)', ''),
    ('server', 'old server binary', ''),
    ('record_stats', 'Records stats', '1'),
]

ECON_PORT = 9999
