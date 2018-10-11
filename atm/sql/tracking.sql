CREATE TABLE `tracking` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(256) NOT NULL,
  `ua` varchar(512) NOT NULL,
  `uip` varchar(64) NOT NULL,
  `referer` varchar(256) NULL,
  `createTime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

ALTER TABLE `tracking` ADD UNIQUE INDEX unique_url_create_time (url, createTime);