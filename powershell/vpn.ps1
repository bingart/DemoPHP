$vpnName = "ALIVPN";
$vpn = Get-VpnConnection -Name $vpnName;
if($vpn.ConnectionStatus -eq "Disconnected"){
	rasdial $vpnName;
}

Start-Sleep -s 60

rasdial $vpnName /disconnect