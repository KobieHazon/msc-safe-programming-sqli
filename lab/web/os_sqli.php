<?php
ob_start();
session_start();
include("db_config.php");
ini_set('display_errors', 1);
if (!$_SESSION["username"]) {
	header('Location:login.php?msg=3');
}
ini_set('display_errors', 1);
?>

<!-- Enable debug using ?debug=true" -->
<html lang="en">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>OS interaction using SQL Injection - SQL Injection Training App</title>

	<link href="./css/htmlstyles.css" rel="stylesheet">
</head>

<body>
	<div class="container-narrow">

		<div class="jumbotron">
			<p class="lead" style="color:white">
				OS interaction using SQL Injection - Let's drop a shell!</a>
			</p>
		</div>

		<?php
		if (isset($_GET["user"])) {
			$user = $_GET["user"];
			$q = "SELECT * FROM users WHERE username = '" . $user . "'";

			if (mysqli_multi_query($con, $q)) {
				do {
					// Store first result set
					if ($result = mysqli_store_result($con)) {
						// Fetch one and one row
						while ($row = mysqli_fetch_row($result)) {
							$username = $row[1];
							$name = $row[3];
							$descr = $row[4];
						}
						// Free result set
						mysqli_free_result($result);
					}
				} while (mysqli_next_result($con));
			}
		} //end if isset

		?>

		<div class="response">

			<p style="color:white">
			<table class="response">

				<tr>
					<td>
						Username:
					</td>
					<td>
						<?php echo $username; ?>
					</td>
				</tr>

				<tr>
					<td>
						Name:
					</td>
					<td>
						<?php echo $name; ?>
					</td>
				</tr>

				<tr>
					<td>
						Description:
					</td>
					<td>
						<?php echo $descr; ?>
					</td>
				</tr>
			</table>
			</p>

		</div>


		<br />

		<?php
		if (isset($_GET['debug'])) {
			$digest = hash('sha256', $_GET['debug']);
			if ($digest === '7a64c3371a789afbf344e1f0138439b4a5482faf00941e3127f9251d0fa0f6ed') {
				$msg = "<div style=\"border:1px solid #4CAF50; padding: 10px\">" . $q . "</div><br />";
				echo $msg;
			}
		}

		if (isset($_GET['hint']) && $_GET['hint'] === '1') {
			echo "<div style=\"border:1px solid #4CAF50; padding: 10px\">This page uses mysqli_multi_query!.
			</div><br />";
		}

		if (isset($_GET['hint']) && $_GET['hint'] === '2') {
			$msg = "<div style=\"border:1px solid #4CAF50; padding: 10px\"> The query being executed is: <br />" . $q . "</div><br />";
			echo $msg;
		}

		?>



		<div class="footer">
			<p>
			<h4><a href="blindsqli.php?user=<?php echo $_SESSION['username']; ?>">Profile</a> | <a href="logout.php">Logout</a> | <a href="index.php">Home</a>
				<h4>
					</p>
		</div>


		<div class="footer">
			<p><a href="https://appsecco.com">Appsecco</a> | Riyaz Walikar | <a href="https://twitter.com/riyazwalikar">@riyazwalikar</a></p>
		</div>

	</div> <!-- /container -->

</body>

</html>