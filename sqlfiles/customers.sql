CREATE TABLE `customers` (
  `id` varchar(12) NOT NULL,
  `rnumber` varchar(10) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `lastname` varchar(100) DEFAULT NULL,
  `data` text,
  `status` tinyint(4) NOT NULL DEFAULT '0',
  `parents` text,
  `children` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rnumber` (`rnumber`);
COMMIT;
