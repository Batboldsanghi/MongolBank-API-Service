CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `action` varchar(50) NOT NULL,
  `request` text NOT NULL,
  `response` text,
  `status` tinyint(4) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;