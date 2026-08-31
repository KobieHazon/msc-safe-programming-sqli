REVOKE GRANT OPTION ON *.* FROM root;
CREATE USER 'weak'@'%' IDENTIFIED WITH 'mysql_native_password' BY 'weak';
CREATE DATABASE IF NOT EXISTS `sqlitraining` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
GRANT SELECT ON sqlitraining.* TO weak;
