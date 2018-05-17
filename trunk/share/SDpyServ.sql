DROP DATABASE IF EXISTS sdpyserv;
CREATE DATABASE sdpyserv;
USE sdpyserv;
GRANT ALL ON sdpyserv.* TO sdpyserv@localhost IDENTIFIED BY '$d_Py$3rv';

CREATE TABLE directory (
    directory_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    directory_name TEXT NOT NULL,
    PRIMARY KEY (directory_id)
) ENGINE=INNODB CHARSET=utf8;

CREATE TABLE file (
    file_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    file_name TEXT NOT NULL,
    directory_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (file_id),
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

CREATE TABLE list_contents(
    list_id INT UNSIGNED NOT NULL,
    file_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (list_id) REFERENCES list_names (list_id),
    FOREIGN KEY (file_id) REFERENCES file (file_id)
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

