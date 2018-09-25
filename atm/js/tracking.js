<script> /* tracking version */
(function () {
	function _pf_log(content) {if(true){console.log(content);}}
	function _pf_event(category, action, label) {if (typeof ga == "function") { ga('send', 'event', category, action, label, { nonInteraction: true }); }}
	function replaceAll(str, find, replace) { return str.replace(new RegExp(find, 'g'), replace); }
	var isBot = /bot|google|baidu|bing|msn|duckduckgo|teoma|slurp|yandex/i.test(navigator.userAgent);
	var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
	var isAdTracking = ((location.href.indexOf('?atr=1') == -1) && (!isBot));
    jQuery(function($){
		function postTracking() {
			var req = {
				url: location.href,
				ua: navigator.userAgent
			}
			$.ajax({
				url: '/wp-content/plugins/post-tester/tracking.php',
				type: 'post',
				dataType: 'json',
				contentType: 'application/json',
				success: function (data) {
					_pf_log('post data:' + data);
				},
				data: JSON.stringify(req),
			});
		}
		
		$(document).ready(function(){
			if (isAdTracking) {
				postTracking();
			}
		});
	});
})();
</script>