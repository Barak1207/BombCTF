<html>
<body>
<h1>Report:</h1>
<?php
echo  "Tester: " . $_POST["lname"] ,' ', $_POST["fname"];
echo "<br/>";
echo "Method: " . $_POST['method_box'];
echo "<br/>";
echo "<br/>";
echo "<br/>";
switch ( $_POST['method_box'] )
{
        case 'Get IP' :
                echo 'Your IP is :', $_SERVER['REMOTE_ADDR'];
                echo "<br/>";
                echo 'Conent is irrelevant.';
                break;
        case 'Ping' :
                echo "Ping echoed back: ";
                #$content_no_spaces = str_replace(" ", "", $_POST["content_box"]);
                echo passthru("python /home/pi/Barak/cyber_course_1/memory_leaker.py " . $_POST["content_length_box"] . ' ' . $_POST["content_box"] );
//                echo "python /home/pi/Barak/cyber_course_1/memory_leaker.py " . $content_no_spaces . ' ' . $_POST["content_length_bo$
                break;
        default:
//              echo $_POST["content_box"];
//              echo "<br/>";
//              echo $_POST["content_length_box"];
                break;
}
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo "<br/>";
echo 'If this isn\'t correct please contact your system administrator.';
#echo 'content length ', $_POST["content_length_box"];

