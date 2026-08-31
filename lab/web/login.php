<?php
ob_start();
session_start();
include("db_config_weak.php");
ini_set('display_errors', 1);
?>

<!-- Enable debug using ?debug=true" -->

<html lang="en">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Login Page 2 - SQL Injection Training App</title>

	<link href="./css/htmlstyles.css" rel="stylesheet">
</head>

<body>
	<div class="container-narrow">

		<div class="jumbotron">
			<p class="lead" style="color:white">
				Login Page - Login bypass

			<p style="color: red">
				<?php
				$_SESSION['next'] = '';
				if (!empty($_REQUEST['msg'])) {
					if ($_REQUEST['msg'] === "1") {
						$_SESSION['next'] = 'searchproducts.php';
						echo "<br />Please login to continue to Search Products";
					} elseif ($_REQUEST['msg'] === "2") {
						$_SESSION['next'] = 'blindsqli.php';
						echo "<br />Please login to continue to Blind SQL Injection Page";
					} elseif ($_REQUEST['msg'] === "3") {
						$_SESSION['next'] = 'os_sqli.php';
						echo "<br />Please login to continue to OS Command Injection Page";
					} else {
						$_SESSION['next'] = 'searchproducts.php';
					}
				}
				?>
			</p>
			</p>
		</div>

		<div class="response">
			<form method="POST" autocomplete="off">
				<p style="color:white">
					Username: <input type="text" id="uid" name="uid"><br /></br />
					Password: <input type="password" id="password" name="password"> </br>
					<input type="checkbox" id="admin_access" name="admin_access" value="1" /> Admin connection
				</p>
				<br />
				<p>
					<input type="submit" value="Submit" />
					<input type="reset" value="Reset" />
				</p>
			</form>
		</div>


		<br />

		<div class="row marketing">
			<div class="col-lg-6">

				<?php

				function hashPassword($password, $salt) {
					if (!is_string($password)) {
						throw new Exception();
					}

					if (is_string($salt)) {
						return md5($salt . $password);
					} else {
						return md5($password);
					}
				}

				function checkAdminAccess($conn, $username, $password) {
					if (!is_string($username) || !is_string($password)) {
						return false;
					}
					
					// Let's sanitize the input ourselves. It is easy when it comes to alphanumeric (I think)
					if (-1 == preg_match("/[a-zA-Z0-9]+/", $username)) {
						throw new Exception();
					}

					$q = "SELECT * FROM admins where (username='" . $username . "')";
					$result = mysqli_query($conn, $q);
					if (!$result) {
						throw new Exception();
					}
					$row = mysqli_fetch_array($result);
					if (!$row) {
						throw new Exception();
					}
					$hash = $row["password"];
					$salt = $row["salt"];

					if (isset($_GET['hint']) && $_GET['hint'] === '4') {
						echo sprintf("<div style=\"border:1px solid #4CAF50; padding: 10px\">%s,%s,%s,%s </div><br />", $hash, $password, $salt, hashPassword($password, $salt));
					}
					if ($hash === hashPassword($password, $salt)) {
						return $row;
					}
					return null;
				}

				function checkUserAccess($conn, $username, $password) {
					if (!is_string($username) || !is_string($password)) {
						return false;
					}
					
					$q = "SELECT * FROM users where (username='" . $username . "') AND (password='" . md5($password) ."')";
					$result = mysqli_query($conn, $q);
					if (!$result) {
						throw new Exception();
					}
					if ($row = mysqli_fetch_array($result)) {
						return $row;
					}
					return null;
				}

				if (isset($_GET['hint']) && $_GET['hint'] === '1') {
					echo "<div style=\"border:1px solid #4CAF50; padding: 10px\">Backend query uses brackets to enclose variables. 
					</div><br />";
				}
				
				if (!empty($_REQUEST['uid'])) {
					$username = ($_REQUEST['uid']);
					$pass = $_REQUEST['password'];
					$is_admin_logon = false;
					if (isset($_REQUEST['admin_access']) && intval($_REQUEST['admin_access']) === 1) {
						$is_admin_logon = true;
					}
					
					if ($is_admin_logon && isset($_GET['hint']) && $_GET['hint'] === '2') {
						echo "<div style=\"border:1px solid #4CAF50; padding: 10px\">username is sanitized with the following regex: [a-zA-Z0-9]+. 
						</div><br />";
					}
					
					if ($is_admin_logon && isset($_GET['hint']) && $_GET['hint'] === '3') {
						echo "<div style=\"border:1px solid #4CAF50; padding: 10px\">The admin tables contains some interesting columns. password_hash=md5(salt + password)
						</div><br />";
					}

					try {
						$row = null;
						if ($is_admin_logon) {
							$row = checkAdminAccess($con, $username, $pass);
						} else {
							$row = checkUserAccess($con, $username, $pass);
						}

						if (mysqli_warning_count($con)) {
							$e = mysqli_get_warnings($con);
							if ($e) {
								do {
									echo "Warning: $e->errno: $e->message\n";
								} while ($e->next());
							}
						}

						if ($row) {
							$_SESSION["username"] = $row[1];
							$_SESSION["name"] = $row[3];
							if ($is_admin_logon) {
								echo sprintf("<font style=\"color:#0FA70F\">Welcome %s, your majesty and excellency! We are so honored to host you in our humble site</font\>", htmlspecialchars($row[1]));
							} else {
								echo sprintf("<font style=\"color:#0FA70F\">Welcome %s!</font\>", htmlspecialchars($row[1]));
							}

							if ($_SESSION['next'] == "searchproducts.php") {
								header('Location: searchproducts.php');
							} elseif ($_SESSION['next'] == "blindsqli.php") {
								header('Location: blindsqli.php?user=' . $_SESSION["username"]);
							} elseif ($_SESSION['next'] == "os_sqli.php") {
								header('Location: os_sqli.php?user=' . $_SESSION["username"]);
							}
						} else {
							echo "<font style=\"color:#FF0000\">Invalid password!</font\>";
						}
					} catch (Exception $e) {
						echo 'Error: ' . mysqli_error($con);
					}

					if (isset($_GET['debug'])) {
						$digest = hash('sha256', $_GET['debug']);
						if ($digest === '7a64c3371a789afbf344e1f0138439b4a5482faf00941e3127f9251d0fa0f6ed') {
							$q = "SELECT * FROM users where (username='" . $username . "') AND (password='" . md5($password) ."')";
							$msg = "<div style=\"border:1px solid #4CAF50; padding: 10px\">" . $q . "</div><br />";
							echo $msg;
						}
					}
				}
				
				//}
				?>

			</div>
		</div>

		<div class="footer">
			<p>
			<h4><a href="index.php">Home</a>
				<h4>
					</p>
		</div>

		<div class="footer">
			<p><a href="https://appsecco.com">Appsecco</a> | Riyaz Walikar | <a href="https://twitter.com/riyazwalikar">@riyazwalikar</a></p>
		</div>
	</div> <!-- /container -->

</body>

</html>