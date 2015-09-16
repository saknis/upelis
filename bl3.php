
<?php
#ini_set('max_execution_time', '120');
$t=ini_get('max_execution_time');
//echo $t."; ";

$t1=time();
$i=0;
/*
* Check DNSBL 
*/
    $dnsbl_lists = array(
'1' => "bl.spamcop.net", 
'2' => "list.dsbl.org", 
'3' => "sbl.spamhaus.org",
'4' => "b.barracudacentral.org",	
'5' => "bl.deadbeef.com",	
'6' => "bl.emailbasura.org",
'7' => "bl.spamcannibal.org",	
'8' => "bl.spamcop.net",	
'9' => "blackholes.five-ten-sg.com",
'10' => "blacklist.woody.ch",	
'11' => "bogons.cymru.com",	
'12' => "cbl.abuseat.org",
'13' => "cdl.anti-spam.org.cn",	
'14' => "combined.abuse.ch",	
'15' => "combined.rbl.msrbl.net",
'16' => "db.wpbl.info",	
'17' => "dnsbl-1.uceprotect.net",	
'18' => "dnsbl-2.uceprotect.net",
'19' => "dnsbl-3.uceprotect.net",	
'20' => "dnsbl.ahbl.org",	
'21' => "dnsbl.cyberlogic.net",
'22' => "dnsbl.inps.de",	
'23' => "dnsbl.njabl.org",	
'24' => "dnsbl.sorbs.net",
'25' => "drone.abuse.ch",	
'26' => "drone.abuse.ch",	
'27' => "duinv.aupads.org",
'28' => "dul.dnsbl.sorbs.net",	
'29' => "dul.ru",	
'30' => "dyna.spamrats.com",
'31' => "dynip.rothen.com",	
'32' => "http.dnsbl.sorbs.net",
'33' => "images.rbl.msrbl.net",
'34' => "ips.backscatterer.org",
'35' => "ix.dnsbl.manitu.net",
'36' => "korea.services.net",
'37' => "misc.dnsbl.sorbs.net",
'38' => "noptr.spamrats.com",
'39' => "ohps.dnsbl.net.au",
'40' => "omrs.dnsbl.net.au",
'41' => "orvedb.aupads.org",
'42' => "osps.dnsbl.net.au",
'43' => "osrs.dnsbl.net.au",
'44' => "owfs.dnsbl.net.au",
'45' => "owps.dnsbl.net.au",
'46' => "pbl.spamhaus.org",
'47' => "phishing.rbl.msrbl.net",
'48' => "probes.dnsbl.net.au",
'49' => "proxy.bl.gweep.ca",
'50' => "proxy.block.transip.nl",
'51' => "psbl.surriel.com",
'52' => "rbl.interserver.net",
'53' => "rdts.dnsbl.net.au",
'54' => "relays.bl.gweep.ca",
'55' => "relays.bl.kundenserver.de",
'56' => "relays.nether.net",
'57' => "residential.block.transip.nl",
'58' => "ricn.dnsbl.net.au",
'59' => "rmst.dnsbl.net.au",
'60' => "sbl.spamhaus.org",
'61' => "short.rbl.jp",
'62' => "smtp.dnsbl.sorbs.net",
'63' => "socks.dnsbl.sorbs.net",
'64' => "spam.abuse.ch",
'65' => "spam.dnsbl.sorbs.net",
'66' => "spam.rbl.msrbl.net",
'67' => "spam.spamrats.com",
'68' => "spamlist.or.kr",
'69' => "spamrbl.imp.ch",
'70' => "t3direct.dnsbl.net.au",
'71' => "tor.ahbl.org",
'72' => "tor.dnsbl.sectoor.de",
'73' => "torserver.tor.dnsbl.sectoor.de",
'74' => "ubl.lashback.com",
'75' => "ubl.unsubscore.com",
'76' => "virbl.bit.nl",
'77' => "virus.rbl.jp",
'78' => "virus.rbl.msrbl.net",
'79' => "web.dnsbl.sorbs.net",
'80' => "wormrbl.imp.ch",
'81' => "xbl.spamhaus.org",
'82' => "zen.spamhaus.org",
'83' => "zombie.dnsbl.sorbs.net"
);
$ip=$_GET['ip'];
$nr=$_GET['nr'];
$nr = ereg_replace("([^0-9])","", $nr); 

$dnsbl_list = $dnsbl_lists[$nr];
function blacklisted($ip,$dnsbl_list) {
        $reverse_ip = implode(".", array_reverse(explode(".", $ip)));
            if (function_exists("checkdnsrr")) {
                if (checkdnsrr($reverse_ip . "." . $dnsbl_list . ".", "A")) {
                    return $reverse_ip . "." . $dnsbl_list;} } }  
//    if ($ip && preg_match('/^([0-9]{1, 3})\.([0-9]{1, 3})\.([0-9]{1, 3})\.([0-9]{1, 3})/', $ip)) {
if ($z=blacklisted($ip,$dnsbl_list)) {
print "true ".$z."; server: ".$nr;
}
else {
print "false; server: ".$nr;}
//} else {
//print "error ip";
//}

?>

