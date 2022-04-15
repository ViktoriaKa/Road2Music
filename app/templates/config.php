<?php
    extract($_REQUEST);
    $file=fopen("form-save.txt","a");

    fwrite($file,"songname :");
    fwrite($file, $songname ."\n");
    fwrite($file,"artistname :");
    fwrite($file, $artistname ."\n");
    fclose($file);
    header("location: contact.php");
 ?>
