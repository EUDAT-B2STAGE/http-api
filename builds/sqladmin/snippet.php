<?PHP

/*
    * Solution for sqllite login not working...
    * Taken from Github in http://j.mp/adminer_sqllite_fix
*/

function adminer_object() {
    class AdminerSoftware extends Adminer {
        function login($login, $password) {
            return true;
        }
    }
    return new AdminerSoftware;
}

// include original script moved to main.php
include "./main.php";

?>