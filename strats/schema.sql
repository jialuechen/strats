CREATE TABLE IF NOT EXISTS 'symbols'()

CREATE TABLE IF NOT EXISTS 'bars'(
    `id` unsigned NOT NULL AUTO_INCREMENT,
    `datetime` datetime NOT NULL,
    'open' double unsigned DEFAULT NULL,
    'high' double unsigned DEFAULT NULL,
    'low' double unsigned DEFAULT NULL,
    'close' double unsigned DEFAULT NULL,
    'volume' double unsigned DEFAULT NULL,
    PRIMARY KEY (`id`),
)



