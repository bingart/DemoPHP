$vpnName = "ALIVPN";
$vpn = Get-VpnConnection -Name $vpnName;
if($vpn.ConnectionStatus -eq "Disconnected"){
	rasdial $vpnName;
}
echo "connected"