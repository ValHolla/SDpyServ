DROP DATABASE IF EXISTS sdpyserv;
CREATE DATABASE sdpyserv;
USE sdpyserv;
GRANT ALL ON sdpyserv.* TO sdpyserv@localhost IDENTIFIED BY '$d_Py$3rv';

CREATE TABLE album (
    album_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    album_name TEXT NOT NULL,
    PRIMARY KEY (album_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE artist (
    artist_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    artist_name TEXT NOT NULL,
    PRIMARY KEY (artist_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE album_artist (
    album_artist_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    album_artist_name TEXT NOT NULL,
    PRIMARY KEY (album_artist_id)
) ENGINE=INNODB CHARSET=utf8;
    
CREATE TABLE directory (
    directory_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    directory_name TEXT NOT NULL,
    PRIMARY KEY (directory_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE genre (
    genre_id INT UNSIGNED NOT NULL,
    genre_name TEXT NOT NULL,
    PRIMARY KEY (genre_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE file_modes (
    file_mode_id TINYINT UNSIGNED NOT NULL,
    file_mode_name VARCHAR(15),
    PRIMARY KEY (file_mode_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE song (
    song_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    song_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    track_num INT UNSIGNED NOT NULL DEFAULT 1,
    sample_rate INT UNSIGNED NOT NULL DEFAULT 1,
    bitrate INT UNSIGNED NOT NULL DEFAULT 1,
    vbr_bool TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
    duration_sec INT UNSIGNED NOT NULL DEFAULT 1,
    file_mode_id TINYINT UNSIGNED NOT NULL DEFAULT 0,
    genre_id INT UNSIGNED NOT NULL DEFAULT 126,
    album_id INT UNSIGNED NOT NULL DEFAULT 1,
    artist_id INT UNSIGNED NOT NULL DEFAULT 1,
    album_artist_id INT UNSIGNED NOT NULL DEFAULT 1,
    directory_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (song_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id),
    FOREIGN KEY (file_mode_id) REFERENCES file_modes(file_mode_id),
    FOREIGN KEY (album_id) REFERENCES album(album_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id),
    FOREIGN KEY (album_artist_id) REFERENCES album_artist(album_artist_id),
    FOREIGN KEY (directory_id) REFERENCES directory(directory_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE options (
    serving_directory TEXT,
    send_slots_num INT UNSIGNED NOT NULL,
    dynamic_slots_num INT UNSIGNED NOT NULL,
    queue_nick_num INT UNSIGNED NOT NULL,
    queue_full_num INT UNSIGNED NOT NULL,
    max_find_results INT UNSIGNED NOT NULL,
    sm_file_low_cps INT UNSIGNED NOT NULL,
    lg_file_low_cps INT UNSIGNED NOT NULL,
    lg_file_size_mb INT UNSIGNED NOT NULL,
    max_list_queue INT UNSIGNED NOT NULL,
    ctcp_send_freq INT UNSIGNED NOT NULL,
    rndm_play_freq INT UNSIGNED NOT NULL,
    queue_list_bool TINYINT(1) UNSIGNED NOT NULL,
    send_ctcp_bool TINYINT(1)  UNSIGNED NOT NULL,
    rndm_play_bool TINYINT(1)  UNSIGNED NOT NULL,
    enable_find_bool TINYINT(1) UNSIGNED NOT NULL,
    zip_lists_bool TINYINT(1) UNSIGNED NOT NULL,
    log_option TINYINT(1) UNSIGNED NOT NULL
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE priority (
    server_priority TINYINT(1) UNSIGNED NOT NULL,
    priority_extentions TEXT 
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE list_dirs (
    list_dir_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    dir_name TEXT NOT NULL,
    PRIMARY KEY (list_dir_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE list_names (
    list_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    list_name VARCHAR(255) NOT NULL,
    UNIQUE KEY (list_name),
    PRIMARY KEY (list_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE list_name_dir(
    list_id INT UNSIGNED NOT NULL,
    list_dir_id INT UNSIGNED NOT NULL,
    dir_recurse_bool TINYINT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (list_id) REFERENCES list_names (list_id),
    FOREIGN KEY (list_dir_id) REFERENCES list_dirs (list_dir_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE networks (
    network_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    network_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (network_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE serving_nicks (
    nick_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nick_name varchar(255) NOT NULL,
    UNIQUE KEY (nick_name),
    PRIMARY KEY (nick_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE channels (
    channel_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    channel_name VARCHAR(255) NOT NULL,
    network_id INT UNSIGNED NOT NULL,
    nick_id INT UNSIGNED NOT NULL,
    list_id INT UNSIGNED NOT NULL,
    ad_frequency INT UNSIGNED NOT NULL,
    text_before_ad_bool TINYINT(1) NOT NULL DEFAULT 0,
    text_before_rand_bool TINYINT(1) NOT NULL DEFAULT 0,
    text_before_ad TEXT,
    text_before_rand TEXT,
    PRIMARY KEY (channel_id),
    FOREIGN KEY (network_id) REFERENCES networks (network_id),
    FOREIGN KEY (list_id) REFERENCES list_names (list_id),
    FOREIGN KEY (nick_id) REFERENCES serving_nicks (nick_id),
    UNIQUE KEY unique_channel_key (channel_name, network_id, nick_id, list_id)
) ENGINE=INNODB CHARSET=utf8;
    
CREATE TABLE stats (
    last_reset_date DATE NOT NULL,
    list_requested INT UNSIGNED NOT NULL,
    list_finished INT UNSIGNED NOT NULL,
    files_requested INT UNSIGNED NOT NULL,
    files_sent INT UNSIGNED NOT NULL,
    cancelled_cps_small INT UNSIGNED NOT NULL,
    cancelled_cps_large INT UNSIGNED NOT NULL,
    cancelled_lost_nick INT UNSIGNED NOT NULL,
    timeouts INT UNSIGNED NOT NULL
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE nick_served (
    nick_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nick VARCHAR(255) NOT NULL,
    PRIMARY KEY (nick_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE nick_stats (
    nick_stat_id INT UNSIGNED NOT NULL,
    nick_id INT UNSIGNED NOT NULL,
    number_requested INT UNSIGNED NOT NULL,
    number_received INT UNSIGNED NOT NULL,
    size_received VARCHAR(255) NOT NULL,
    PRIMARY KEY (nick_stat_id),
    FOREIGN KEY (nick_id) REFERENCES nick_served (nick_id)
) ENGINE=INNODB CHARSET=utf8;
    
CREATE TABLE ban_codes (
    ban_code INT UNSIGNED NOT NULL,
    ban_reason TEXT,
    PRIMARY KEY(ban_code)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE nick_bans (
    ban_id INT UNSIGNED NOT NULL,
    ban_code INT UNSIGNED NOT NULL,
    nick_id INT UNSIGNED NOT NULL,
    network_id INT UNSIGNED NOT NULL,
    channel_id INT UNSIGNED NOT NULL,
    PRIMARY KEY(ban_id),
    FOREIGN KEY(ban_code) REFERENCES ban_codes (ban_code),
    FOREIGN KEY(nick_id) REFERENCES nick_served (nick_id),
    FOREIGN KEY(network_id) REFERENCES networks (network_id),
    FOREIGN KEY(channel_id) REFERENCES channels (channel_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE queues (
    queue_id INT UNSIGNED NOT NULL,
    nick_id INT UNSIGNED NOT NULL,
    channel_id INT UNSIGNED NOT NULL,
    network_id INT UNSIGNED NOT NULL,
    queue_number INT UNSIGNED NOT NULL,
    PRIMARY KEY (queue_id),
    FOREIGN KEY (nick_id) REFERENCES nick_served (nick_id),
    FOREIGN KEY (channel_id) REFERENCES channels (channel_id),
    FOREIGN KEY (network_id) REFERENCES networks (network_id)
) ENGINE=INNODB CHARSET=utf8;

insert into album 
(album_name)
values
('Unknown');

insert into artist 
(artist_name)
values
('Unknown');

insert into album_artist 
(album_artist_name)
values 
('Unknown');

insert into file_modes
(file_mode_id, file_mode_name)
values 
(0, 'Stereo'), (1, 'Joint Stereo'),
(2, 'Dual Channel'), (3, 'Mono');


insert into options
(send_slots_num, dynamic_slots_num, queue_nick_num,
    queue_full_num, max_find_results, sm_file_low_cps,
    lg_file_low_cps, max_list_queue, ctcp_send_freq,
    rndm_play_freq, lg_file_size_mb, queue_list_bool, send_ctcp_bool,
    enable_find_bool, rndm_play_bool, log_option, zip_lists_bool) 
values 
(2,0,10,50,5,100,100,5,300,300,10,1,1,1,0,0,1);

insert into priority
(server_priority, priority_extentions) 
values 
(0, "zip,txt");

insert into stats
(last_reset_date, list_requested, list_finished,
files_requested, files_sent, cancelled_cps_small,
cancelled_cps_large, cancelled_lost_nick, timeouts)
values
(date_format(now(), '%Y-%m-%d'),0,0,0,0,0,0,0,0);


insert into genre 
(genre_id, genre_name) 
values 
("0", "Blues"), ("1", "Classic Rock"), ("2", "Country"),
("3", "Dance"), ("4", "Disco"), ("5", "Funk"),
("6", "Grunge"), ("7", "Hip-Hop"), ("8", "Jazz"),
("9", "Metal"), ("10", "New Age"), ("11", "Oldies"),
("12", "Other"), ("13", "Pop"), ("14", "R&B"),
("15", "Rap"), ("16", "Reggae"), ("17", "Rock"), ("18", "Techno"),
("19", "Industrial"), ("20", "Alternative"), ("21", "Ska"),
("22", "Death Metal"), ("23", "Pranks"), ("24", "Soundtrack"),
("25", "Euro-Techno"), ("26", "Ambient"), ("27", "Trip-Hop"),
("28", "Vocal"), ("29", "Jazz+Funk"), ("30", "Fusion"),
("31", "Trance"), ("32", "Classical"), ("33", "Instrumental"),
("34", "Acid"), ("35", "House"), ("36", "Game"), ("37", "Sound Clip"),
("38", "Gospel"), ("39", "Noise"), ("40", "AlternRock"), ("41", "Bass"),
("42", "Soul"), ("43", "Punk"), ("44", "Space"), ("45", "Meditative"),
("46", "Instrumental Pop"), ("47", "Instrumental Rock"), ("48", "Ethnic"),
("49", "Gothic"), ("50", "Darkwave"), ("51", "Techno-Industrial"),
("52", "Electronic"), ("53", "Pop-Folk"), ("54", "Eurodance"),
("55", "Dream"), ("56", "Southern Rock"), ("57", "Comedy"),
("58", "Cult"), ("59", "Gangsta"), ("60", "Top 40"), ("61", "Christian Rap"),
("62", "Pop/Funk"), ("63", "Jungle"), ("64", "Native American"),
("65", "Cabaret"), ("66", "New Wave"), ("67", "Psychadelic"),
("68", "Rave"), ("69", "Showtunes"), ("70", "Trailer"), ("71", "Lo-Fi"),
("72", "Tribal"), ("73", "Acid Punk"), ("74", "Acid Jazz"), ("75", "Polka"),
("76", "Retro"), ("77", "Musical"), ("78", "Rock & Roll"),
("79", "Hard Rock"), ("80", "Folk"), ("81", "Folk-Rock"),
("82", "National Folk"), ("83", "Swing"), ("84", "Fast Fusion"),
("85", "Bebob"), ("86", "Latin"), ("87", "Revival"), ("88", "Celtic"),
("89", "Bluegrass"), ("90", "Avantgarde"), ("91", "Gothic Rock"),
("92", "Progressive Rock"), ("93", "Psychedelic Rock"),
("94", "Symphonic Rock"), ("95", "Slow Rock"), ("96", "Big Band"),
("97", "Chorus"), ("98", "Easy Listening"), ("99", "Acoustic"),
("100", "Humour"), ("101", "Speech"), ("102", "Chanson"), ("103", "Opera"),
("104", "Chamber Music"), ("105", "Sonata"), ("106", "Symphony"),
("107", "Booty Bass"), ("108", "Primus"), ("109", "Porn Groove"),
("110", "Satire"), ("111", "Slow Jam"), ("112", "Club"), ("113", "Tango"),
("114", "Samba"), ("115", "Folklore"), ("116", "Ballad"),
("117", "Power Ballad"), ("118", "Rhythmic Soul"), ("119", "Freestyle"),
("120", "Duet"), ("121", "Punk Rock"), ("122", "Drum Solo"),
("123", "Acapella"), ("124", "Euro-House"), ("125", "Dance Hall"),
("126", "Unknown");
commit;
